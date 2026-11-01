# Local backup and isolated recovery

Authority: human Step 3 backup/recovery verification; REQ-05-009 / REQ-06-008 -> ADR-09 -> DC-09 -> VS01-T-22. This procedure verifies the approved SQL backup/restore mechanism with synthetic data. It does not switch the application to a restored database or establish final VS-01 acceptance.

## Reproduce the verification

Prerequisites: the locked Python environment, ignored generated `.env`, and Docker Desktop's Linux engine. From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts/verify_recovery.py
```

The script:

1. Starts only the disposable `test-db` service and checks that its configured database is exactly `bullion_test`.
2. Creates a unique `bullion_recovery_source_<run>_test` database, migrates it and seeds labeled synthetic listing/source/watchlist/import/quality data through the real API. No application database is selected.
3. Snapshots every row in all eight domain tables plus the migration table, preserving database decimal text; hashes constraints, indexes, triggers and functions; records a fixed-as-of exact-price history query.
4. Creates `backups/recovery-<run>/` with restricted permissions (Windows inheritance disabled; current user and SYSTEM only, or POSIX directory mode 0700).
5. Captures `pg_dump --format=custom --no-owner --no-privileges` as binary bytes. It does not use PowerShell's text redirection for the archive. Writes the dump exclusively, its SHA-256 sidecar and verifies a read-back checksum.
6. Inspects the archive with `pg_restore --list`, requiring every expected table.
7. Creates a separate, previously nonexistent `bullion_recovery_restored_<run>_test` database and restores with `--exit-on-error --single-transaction --no-owner --no-privileges`. There is no `--clean`, DROP, active-database restore or automatic failover.
8. Requires equal table counts and full-row hashes, equal normalized schema hashes, zero orphan observation/batch/raw-row links, and the same fixed-as-of history response including exact decimal prices. Confirms the restored append-only observation trigger rejects an update.
9. Writes a secret-free summary to `artifacts/recovery-verification.json`. A failure returns nonzero; inspect `checks` and `failure_type` without exposing connection settings.

The successful fixture contains one listing, one source, one watchlist/member, one batch, two raw rows, two observations, two quality records and one schema revision. Every table is nonempty. Both data and provenance match after restoration. No indicator output is claimed; indicators are not implemented.

## Observed schema representation difference

The initial comparison failed even though all rows and the history query matched. PostgreSQL 18 redistributed `varchar[] -> text[]` casts over literals when dumping/reparsing five existing enum CHECK constraints. The verifier accepts only the two exact equivalent deparses of those five named definitions; every other definition remains byte-compared. Index, trigger and function definitions matched without normalization. Failed-attempt evidence is retained in ignored `artifacts/recovery-first-attempt.json` and `artifacts/recovery-schema-diagnostic.json`; final success is recorded separately.

## Inspect and retain evidence safely

The report provides the archive's relative path, byte size and checksum. To independently compare the stored bytes:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath '<backup path from the report>'
```

Compare the full hash with the report and `.sha256` sidecar. Retain the archive, hash, report, matching source revision and dependency/image locks together in the owner-controlled location. A checksum alone does not prove restorability; the successful separate restore is the integrity evidence.

Test databases are left available in the disposable service for inspection. Stopping that service discards its tmpfs database contents; the host backup archive persists. After inspection:

```powershell
docker compose stop test-db
```

Backups, local reports and `.env` are excluded from Git and Docker build contexts. Backups may contain retained raw input and source evidence, so production archives require the same confidentiality controls as the data. No retention duration, RPO/RTO, encryption service or cloud destination is selected here.

## Owner recovery instructions

For a future recovery of qualified application data, use the same custom-format PostgreSQL dump and isolated-restore sequence, retain matching schema/runtime versions, validate checksums and table-of-contents, and verify complete row/provenance/query equality before considering a connection switch. Use a separate empty target and preserve the original application volume. Do not substitute `docker compose down -v`, a destructive migration downgrade, database reset or `pg_restore --clean` against the active application database.

This task tested generated data only. It did not back up private owner data, simulate loss of the actual volume, restore owner data, choose backup retention or authorize cutover. Those operational acceptance decisions remain explicit. The verifier's restore target is intentionally fixed to the disposable service; do not edit its guards to target the application.
