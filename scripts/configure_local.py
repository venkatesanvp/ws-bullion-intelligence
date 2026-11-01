"""Create local secrets without printing or overwriting them. No market data is seeded."""

from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    print("Existing .env preserved; no settings overwritten.")
else:
    password = secrets.token_hex(24)
    token = secrets.token_urlsafe(40)
    text = (
        f"POSTGRES_USER=bullion\nPOSTGRES_DB=bullion\nPOSTGRES_PASSWORD={password}\n"
        f"LOCAL_APP_TOKEN={token}\n"
        f"DATABASE_URL=postgresql+psycopg://bullion:{password}@db:5432/bullion\n"
    )
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)
    print(
        "Created untracked .env. Read LOCAL_APP_TOKEN locally to unlock the UI. No secret was printed."
    )
