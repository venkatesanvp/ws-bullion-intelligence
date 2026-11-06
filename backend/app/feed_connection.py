"""Bounded DNS/TCP/TLS dial for the single fixed Dhan read-only feed host.

A stalled resolver owns at most one daemon thread per process. Credentials never
enter the resolver/TCP layer. TLS hostname and certificate verification stay with
the WebSocket library. No proxy, alternate host or insecure TLS fallback.
"""

import socket
import time
from threading import Event, Lock, Thread
from websockets.sync.client import connect
from websockets.exceptions import InvalidStatus

_lock = Lock()
_lookup = None
_result = []
_done = Event()


def addresses():
    global _lookup
    with _lock:
        if _lookup is None or _done.is_set():
            _done.clear()
            _result.clear()

            def resolve():
                try:
                    values = socket.getaddrinfo("api-feed.dhan.co", 443, type=socket.SOCK_STREAM)
                    _result.extend(values)
                except OSError:
                    pass
                finally:
                    _done.set()

            _lookup = Thread(target=resolve, name="market-feed-dns", daemon=True)
            _lookup.start()
    if not _done.wait(timeout=2):
        raise TimeoutError("FEED_DNS_TIMEOUT")
    if not _result:
        raise OSError("FEED_DNS_UNAVAILABLE")
    # One host, maximum two resolved addresses, bounded total TCP time.
    unique = []
    for item in sorted(_result, key=lambda x: x[0] != socket.AF_INET):
        if item[4] not in [x[4] for x in unique]:
            unique.append(item)
    return unique[:2]


def connect_feed(url, **kwargs):
    deadline = time.monotonic() + 8
    candidates = addresses()
    for family, kind, protocol, _, destination in candidates:
        if time.monotonic() >= deadline:
            break
        sock = socket.socket(family, kind, protocol)
        try:
            sock.settimeout(min(2, max(0.1, deadline - time.monotonic())))
            sock.connect(destination)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("FEED_CONNECT_TIMEOUT")
            kwargs["open_timeout"] = remaining
            return connect(url, sock=sock, **kwargs)
        except InvalidStatus:
            sock.close()
            raise  # Auth/entitlement/rate status must reach the terminal-error policy.
        except Exception:
            sock.close()
    raise OSError("FEED_CONNECTION_UNAVAILABLE")
