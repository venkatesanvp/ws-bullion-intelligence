"""Chromium fixture seeder: SYNTHETIC only, hard guard against non-test databases."""

import json
import os
from uuid import uuid4
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from app.provider_ingestion import ingest_collected
from tests.provider_fixtures import collected, metadata, register


def main():
    raw = os.environ.get("TEST_DATABASE_URL", "")
    url = make_url(raw)
    if (
        url.drivername != "postgresql+psycopg"
        or url.host not in {"127.0.0.1", "localhost"}
        or not (url.database or "").endswith("_test")
    ):
        raise RuntimeError("Refusing fixture writes outside explicit local *_test database")
    engine = create_engine(raw)
    p, result, _ = collected()
    with Session(engine) as db:
        with db.begin():
            db.execute(
                text(
                    "TRUNCATE quality_results, price_observations, import_rows, import_batches, watchlist_members, watchlists, data_sources, instruments"
                )
            )
        source, ids = register(db, result.series, p)
        for item, identifier in zip(result.series, ids, strict=True):
            ingest_collected(
                db,
                item,
                metadata(item, source, identifier),
                uuid4(),
                "SYNTHETIC-browser",
                persistence_approved=True,
            )
    engine.dispose()
    print(
        json.dumps(
            {
                "source_id": str(source),
                "instruments": [
                    {"id": str(i), "symbol": s.listing.symbol}
                    for i, s in zip(ids, result.series, strict=True)
                ],
                "data_class": "SYNTHETIC_TEST",
            }
        )
    )


if __name__ == "__main__":
    main()
