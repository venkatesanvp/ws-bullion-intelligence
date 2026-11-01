# Initial daily-market workbench schema. DC-01/02/03.
from alembic import op

revision = "0001_market_workbench"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE TABLE data_sources (\n\tid UUID NOT NULL, \n\tlabel VARCHAR(256) NOT NULL, \n\tsource_kind VARCHAR(32) NOT NULL, \n\tqualification VARCHAR(32) NOT NULL, \n\trights_evidence_ref TEXT, \n\tpermitted_uses JSONB NOT NULL, \n\treviewed_at TIMESTAMP WITH TIME ZONE, \n\tcontract_version VARCHAR(64) NOT NULL, \n\tprofile JSONB NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_source_kind CHECK (source_kind = 'USER_CSV'), \n\tCONSTRAINT ck_qualification CHECK (qualification IN ('UNVERIFIED','QUALIFIED_FOR_RESEARCH','RESTRICTED')), \n\tCONSTRAINT ck_qualified_evidence CHECK (qualification <> 'QUALIFIED_FOR_RESEARCH' OR (rights_evidence_ref IS NOT NULL AND reviewed_at IS NOT NULL))\n)"
    )
    op.execute(
        "CREATE TABLE instruments (\n\tid UUID NOT NULL, \n\texchange VARCHAR(16) NOT NULL, \n\tsymbol VARCHAR(64) NOT NULL, \n\tname VARCHAR(256) NOT NULL, \n\tmetal VARCHAR(8) NOT NULL, \n\tcurrency VARCHAR(3) NOT NULL, \n\tisin VARCHAR(12), \n\tactive BOOLEAN NOT NULL, \n\tdata_revision BIGINT NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_listing UNIQUE (exchange, symbol), \n\tCONSTRAINT ck_metal CHECK (metal IN ('GOLD','SILVER')), \n\tCONSTRAINT ck_currency CHECK (currency = 'INR'), \n\tCONSTRAINT ck_revision CHECK (data_revision >= 0)\n)"
    )
    op.execute(
        "CREATE TABLE watchlists (\n\tid UUID NOT NULL, \n\tname VARCHAR(256) NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tupdated_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (name)\n)"
    )
    op.execute(
        "CREATE TABLE import_batches (\n\tid UUID NOT NULL, \n\trequest_key UUID NOT NULL, \n\tinstrument_id UUID NOT NULL, \n\tsource_id UUID NOT NULL, \n\tfile_sha256 VARCHAR(64) NOT NULL, \n\tprofile_sha256 VARCHAR(64) NOT NULL, \n\tprofile_snapshot JSONB NOT NULL, \n\tstatus VARCHAR(16) NOT NULL, \n\tbytes BIGINT NOT NULL, \n\trow_count INTEGER NOT NULL, \n\tnew_count INTEGER NOT NULL, \n\tduplicate_count INTEGER NOT NULL, \n\terror_count INTEGER NOT NULL, \n\tsanitized_name VARCHAR(256), \n\tsubmitted_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tfinished_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\trequest_id VARCHAR(36) NOT NULL, \n\terror_code VARCHAR(64), \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_import_request UNIQUE (request_key), \n\tCONSTRAINT uq_batch_identity UNIQUE (id, instrument_id, source_id), \n\tCONSTRAINT ck_batch_status CHECK (status IN ('ACCEPTED','NO_CHANGE','REJECTED','FAILED')), \n\tCONSTRAINT ck_batch_counts CHECK (bytes >= 0 AND row_count >= 0 AND new_count >= 0 AND duplicate_count >= 0 AND error_count >= 0), \n\tFOREIGN KEY(instrument_id) REFERENCES instruments (id), \n\tFOREIGN KEY(source_id) REFERENCES data_sources (id)\n)"
    )
    op.execute(
        "CREATE TABLE watchlist_members (\n\twatchlist_id UUID NOT NULL, \n\tinstrument_id UUID NOT NULL, \n\tadded_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tPRIMARY KEY (watchlist_id, instrument_id), \n\tFOREIGN KEY(watchlist_id) REFERENCES watchlists (id), \n\tFOREIGN KEY(instrument_id) REFERENCES instruments (id)\n)"
    )
    op.execute(
        "CREATE TABLE import_rows (\n\tbatch_id UUID NOT NULL, \n\trow_number INTEGER NOT NULL, \n\tmapped_raw JSONB NOT NULL, \n\tcanonical_hash VARCHAR(64), \n\tPRIMARY KEY (batch_id, row_number), \n\tCONSTRAINT ck_row_number CHECK (row_number > 0), \n\tFOREIGN KEY(batch_id) REFERENCES import_batches (id)\n)"
    )
    op.execute(
        "CREATE TABLE price_observations (\n\tid UUID NOT NULL, \n\tinstrument_id UUID NOT NULL, \n\tsource_id UUID NOT NULL, \n\ttrading_date DATE NOT NULL, \n\tinterval VARCHAR(8) NOT NULL, \n\tprice_basis VARCHAR(32) NOT NULL, \n\tclose NUMERIC(24, 10) NOT NULL, \n\topen NUMERIC(24, 10), \n\thigh NUMERIC(24, 10), \n\tlow NUMERIC(24, 10), \n\tvolume BIGINT, \n\tevent_time TIMESTAMP WITH TIME ZONE, \n\tevent_precision VARCHAR(16) NOT NULL, \n\tprovider_published_at TIMESTAMP WITH TIME ZONE, \n\tingested_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tbatch_id UUID NOT NULL, \n\trow_number INTEGER NOT NULL, \n\tcanonical_hash VARCHAR(64) NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_observation UNIQUE (instrument_id, source_id, trading_date, interval, price_basis), \n\tCONSTRAINT uq_observation_raw_row UNIQUE (batch_id, row_number), \n\tCONSTRAINT fk_observation_raw FOREIGN KEY(batch_id, row_number) REFERENCES import_rows (batch_id, row_number), \n\tCONSTRAINT fk_observation_batch_identity FOREIGN KEY(batch_id, instrument_id, source_id) REFERENCES import_batches (id, instrument_id, source_id), \n\tCONSTRAINT ck_daily CHECK (interval = '1d'), \n\tCONSTRAINT ck_basis CHECK (price_basis IN ('RAW_CLOSE','PROVIDER_ADJUSTED','UNKNOWN')), \n\tCONSTRAINT ck_close CHECK (close > 0 AND close <> 'NaN'::numeric), \n\tCONSTRAINT ck_ohlc CHECK ((open IS NULL AND high IS NULL AND low IS NULL) OR (open IS NOT NULL AND high IS NOT NULL AND low IS NOT NULL AND open > 0 AND low > 0 AND high > 0 AND open <> 'NaN'::numeric AND high <> 'NaN'::numeric AND low <> 'NaN'::numeric AND high >= greatest(open,low,close) AND low <= least(open,high,close))), \n\tCONSTRAINT ck_volume CHECK (volume IS NULL OR volume >= 0), \n\tCONSTRAINT ck_event_precision CHECK ((event_time IS NULL AND event_precision = 'SESSION_DATE') OR (event_time IS NOT NULL AND event_precision = 'INSTANT')), \n\tFOREIGN KEY(instrument_id) REFERENCES instruments (id), \n\tFOREIGN KEY(source_id) REFERENCES data_sources (id)\n)"
    )
    op.execute(
        "CREATE TABLE quality_results (\n\tid UUID NOT NULL, \n\tbatch_id UUID NOT NULL, \n\trow_number INTEGER, \n\tcode VARCHAR(64) NOT NULL, \n\tseverity VARCHAR(16) NOT NULL, \n\tdetails JSONB NOT NULL, \n\tassessed_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT fk_quality_raw_row FOREIGN KEY(batch_id, row_number) REFERENCES import_rows (batch_id, row_number), \n\tCONSTRAINT ck_severity CHECK (severity IN ('ERROR','WARN','INFO','UNASSESSED')), \n\tFOREIGN KEY(batch_id) REFERENCES import_batches (id)\n)"
    )
    op.execute("CREATE INDEX ix_batch_time ON import_batches (submitted_at, id)")
    op.execute(
        "CREATE INDEX ix_series_date ON price_observations (instrument_id, source_id, interval, price_basis, trading_date)"
    )
    op.execute("CREATE INDEX ix_quality_batch_row ON quality_results (batch_id, row_number)")

    op.execute(
        "CREATE FUNCTION preserve_market_audit() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Accepted market audit records are immutable'; END; $$"
    )
    op.execute(
        "CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON price_observations FOR EACH ROW EXECUTE FUNCTION preserve_market_audit()"
    )
    op.execute(
        "CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON import_rows FOR EACH ROW EXECUTE FUNCTION preserve_market_audit()"
    )
    op.execute(
        "CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON import_batches FOR EACH ROW EXECUTE FUNCTION preserve_market_audit()"
    )
    op.execute(
        "CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON quality_results FOR EACH ROW EXECUTE FUNCTION preserve_market_audit()"
    )

    op.execute(
        "CREATE FUNCTION preserve_listing_identity() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF ROW(OLD.exchange,OLD.symbol,OLD.metal,OLD.currency,OLD.isin) IS DISTINCT FROM ROW(NEW.exchange,NEW.symbol,NEW.metal,NEW.currency,NEW.isin) AND EXISTS(SELECT 1 FROM price_observations WHERE instrument_id = OLD.id) THEN RAISE EXCEPTION 'Listing identity with accepted history is immutable'; END IF; RETURN NEW; END; $$"
    )
    op.execute(
        "CREATE TRIGGER immutable_listing_identity BEFORE UPDATE ON instruments FOR EACH ROW EXECUTE FUNCTION preserve_listing_identity()"
    )


def downgrade():
    raise RuntimeError("Destructive downgrade is disabled; restore a reviewed backup instead.")
