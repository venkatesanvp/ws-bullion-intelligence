"""Public pinned gosu ELF symbol evidence; no application caches or secrets."""

import subprocess
import pathlib
import struct
import json
import hashlib

r = pathlib.Path.cwd()
d = "C:/Program Files/Docker/Docker/resources/bin/docker.exe"
c = subprocess.check_output(
    [
        d,
        "create",
        "--network",
        "none",
        "--entrypoint",
        "true",
        "sha256:3a4264520e121176619f54ff867d12774bc81e95e7b84db58d63bccdb6144b81",
    ],
    text=True,
).strip()
try:
    subprocess.run(
        [d, "cp", c + ":/usr/local/bin/gosu", str(r / "artifacts/gosu-public-image-binary")],
        check=True,
        capture_output=True,
    )
finally:
    subprocess.run([d, "rm", "-v", c], check=True, capture_output=True)
b = (r / "artifacts/gosu-public-image-binary").read_bytes()
assert b[:6] == b"\x7fELF\x02\x01"
shoff = struct.unpack_from("<Q", b, 40)[0]
size, num, names = struct.unpack_from("<HHH", b, 58)
sections = [struct.unpack_from("<IIQQQQIIQQ", b, shoff + i * size) for i in range(num)]
strings = b[sections[names][4] : sections[names][4] + sections[names][5]]


def name(s):
    return strings[s[0] :].split(b"\0")[0].decode()


pcln = next(s for s in sections if name(s) == ".gopclntab")
data = b[pcln[4] : pcln[4] + pcln[5]]
assert struct.unpack_from("<I", data)[0] == 0xFFFFFFF1 and data[7] == 8
nfunc = struct.unpack_from("<Q", data, 8)[0]
funcname, cu = struct.unpack_from("<QQ", data, 32)
funcs = [x.decode(errors="replace") for x in data[funcname:cu].split(b"\0") if x]
patterns = {
    "HTTP2": ["net/http", "golang.org/x/net/http2"],
    "IDNA": ["golang.org/x/net/idna"],
    "TLS": ["crypto/tls"],
    "WINDOWS_ROOT": ["internal/syscall/windows", "os.(*Root).Mkdir"],
}
result = {
    "data_class": "PUBLIC_IMAGE_BINARY_ONLY",
    "sha256": hashlib.sha256(b).hexdigest(),
    "format": "ELF64 little-endian; Go1.20+ pclntab",
    "nfunc": nfunc,
    "function_name_count": len(funcs),
    "main_present": "main.main" in funcs,
    "package_symbols": {
        k: [f for f in funcs if any(p in f for p in pats)] for k, pats in patterns.items()
    },
    "limitation": "Compiled symbol-presence evidence, not whole-program dynamic reachability proof. Windows code absent on Linux; removed helper is preferred remediation.",
}
assert result["main_present"]
(r / "artifacts/gosu-symbol-evidence.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
