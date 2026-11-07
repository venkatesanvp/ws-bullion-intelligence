"""Add the provider source contract without replacing canonical tables or rows."""

from alembic import op

revision = "0002_provider_ingestion"
down_revision = "0001_market_workbench"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("ck_source_kind", "data_sources", type_="check")
    op.create_check_constraint(
        "ck_source_kind", "data_sources", "source_kind IN ('USER_CSV','DHANHQ')"
    )
    op.create_check_constraint(
        "ck_source_contract",
        "data_sources",
        "(source_kind = 'USER_CSV' AND contract_version = 'csv-v1') OR "
        "(source_kind = 'DHANHQ' AND contract_version = 'dhan-daily-v1-provisional')",
    )


def downgrade():
    # Never disguise provider data as CSV or delete it to make a downgrade work.
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM data_sources WHERE source_kind <> 'USER_CSV') THEN
            RAISE EXCEPTION 'Provider sources exist; downgrade refused without data loss';
        END IF;
    END $$""")
    op.drop_constraint("ck_source_contract", "data_sources", type_="check")
    op.drop_constraint("ck_source_kind", "data_sources", type_="check")
    op.create_check_constraint("ck_source_kind", "data_sources", "source_kind = 'USER_CSV'")
