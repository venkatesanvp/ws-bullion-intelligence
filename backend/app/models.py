import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Instrument(Base):
    __tablename__ = "instruments"
    __table_args__ = (
        UniqueConstraint("exchange", "symbol", name="uq_listing"),
        CheckConstraint("metal IN ('GOLD','SILVER')", name="ck_metal"),
        CheckConstraint("currency = 'INR'", name="ck_currency"),
        CheckConstraint("data_revision >= 0", name="ck_revision"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange: Mapped[str] = mapped_column(String(16))
    symbol: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(256))
    metal: Mapped[str] = mapped_column(String(8))
    currency: Mapped[str] = mapped_column(String(3))
    isin: Mapped[str | None] = mapped_column(String(12))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    data_revision: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class DataSource(Base):
    __tablename__ = "data_sources"
    __table_args__ = (
        CheckConstraint("source_kind IN ('USER_CSV','DHANHQ')", name="ck_source_kind"),
        CheckConstraint(
            "(source_kind = 'USER_CSV' AND contract_version = 'csv-v1') OR "
            "(source_kind = 'DHANHQ' AND contract_version = 'dhan-daily-v1-provisional')",
            name="ck_source_contract",
        ),
        CheckConstraint(
            "qualification IN ('UNVERIFIED','QUALIFIED_FOR_RESEARCH','RESTRICTED')",
            name="ck_qualification",
        ),
        CheckConstraint(
            "qualification <> 'QUALIFIED_FOR_RESEARCH' OR (rights_evidence_ref IS NOT NULL AND reviewed_at IS NOT NULL)",
            name="ck_qualified_evidence",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String(256))
    source_kind: Mapped[str] = mapped_column(String(32), default="USER_CSV")
    qualification: Mapped[str] = mapped_column(String(32), default="UNVERIFIED")
    rights_evidence_ref: Mapped[str | None] = mapped_column(Text)
    permitted_uses: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contract_version: Mapped[str] = mapped_column(String(64), default="csv-v1")
    profile: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class ImportBatch(Base):
    __tablename__ = "import_batches"
    __table_args__ = (
        UniqueConstraint("request_key", name="uq_import_request"),
        UniqueConstraint("id", "instrument_id", "source_id", name="uq_batch_identity"),
        CheckConstraint(
            "status IN ('ACCEPTED','NO_CHANGE','REJECTED','FAILED')", name="ck_batch_status"
        ),
        CheckConstraint(
            "bytes >= 0 AND row_count >= 0 AND new_count >= 0 AND duplicate_count >= 0 AND error_count >= 0",
            name="ck_batch_counts",
        ),
        Index("ix_batch_time", "submitted_at", "id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("instruments.id"))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id"))
    file_sha256: Mapped[str] = mapped_column(String(64))
    profile_sha256: Mapped[str] = mapped_column(String(64))
    profile_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(16))
    bytes: Mapped[int] = mapped_column(BigInteger)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    new_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    sanitized_name: Mapped[str | None] = mapped_column(String(256))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    request_id: Mapped[str] = mapped_column(String(36))
    error_code: Mapped[str | None] = mapped_column(String(64))


class ImportRow(Base):
    __tablename__ = "import_rows"
    __table_args__ = (CheckConstraint("row_number > 0", name="ck_row_number"),)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("import_batches.id"), primary_key=True)
    row_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    mapped_raw: Mapped[dict[str, Any]] = mapped_column(JSONB)
    canonical_hash: Mapped[str | None] = mapped_column(String(64))


class Observation(Base):
    __tablename__ = "price_observations"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "source_id",
            "trading_date",
            "interval",
            "price_basis",
            name="uq_observation",
        ),
        UniqueConstraint("batch_id", "row_number", name="uq_observation_raw_row"),
        ForeignKeyConstraint(
            ["batch_id", "row_number"],
            ["import_rows.batch_id", "import_rows.row_number"],
            name="fk_observation_raw",
        ),
        ForeignKeyConstraint(
            ["batch_id", "instrument_id", "source_id"],
            ["import_batches.id", "import_batches.instrument_id", "import_batches.source_id"],
            name="fk_observation_batch_identity",
        ),
        CheckConstraint("interval = '1d'", name="ck_daily"),
        CheckConstraint(
            "price_basis IN ('RAW_CLOSE','PROVIDER_ADJUSTED','UNKNOWN')", name="ck_basis"
        ),
        CheckConstraint("close > 0 AND close <> 'NaN'::numeric", name="ck_close"),
        CheckConstraint(
            "(open IS NULL AND high IS NULL AND low IS NULL) OR (open IS NOT NULL AND high IS NOT NULL AND low IS NOT NULL AND open > 0 AND low > 0 AND high > 0 AND open <> 'NaN'::numeric AND high <> 'NaN'::numeric AND low <> 'NaN'::numeric AND high >= greatest(open,low,close) AND low <= least(open,high,close))",
            name="ck_ohlc",
        ),
        CheckConstraint("volume IS NULL OR volume >= 0", name="ck_volume"),
        CheckConstraint(
            "(event_time IS NULL AND event_precision = 'SESSION_DATE') OR (event_time IS NOT NULL AND event_precision = 'INSTANT')",
            name="ck_event_precision",
        ),
        Index(
            "ix_series_date",
            "instrument_id",
            "source_id",
            "interval",
            "price_basis",
            "trading_date",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("instruments.id"))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id"))
    trading_date: Mapped[date] = mapped_column(Date)
    interval: Mapped[str] = mapped_column(String(8))
    price_basis: Mapped[str] = mapped_column(String(32))
    close: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    open: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    high: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    low: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    volume: Mapped[int | None] = mapped_column(BigInteger)
    event_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_precision: Mapped[str] = mapped_column(String(16))
    provider_published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    row_number: Mapped[int] = mapped_column(Integer)
    canonical_hash: Mapped[str] = mapped_column(String(64))


class QualityResult(Base):
    __tablename__ = "quality_results"
    __table_args__ = (
        ForeignKeyConstraint(
            ["batch_id", "row_number"],
            ["import_rows.batch_id", "import_rows.row_number"],
            name="fk_quality_raw_row",
        ),
        CheckConstraint("severity IN ('ERROR','WARN','INFO','UNASSESSED')", name="ck_severity"),
        Index("ix_quality_batch_row", "batch_id", "row_number"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("import_batches.id"))
    row_number: Mapped[int | None] = mapped_column(Integer)
    code: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Watchlist(Base):
    __tablename__ = "watchlists"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class WatchlistMember(Base):
    __tablename__ = "watchlist_members"
    watchlist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("watchlists.id"), primary_key=True)
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("instruments.id"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
