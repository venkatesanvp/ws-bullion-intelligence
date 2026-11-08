from datetime import date, datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class InstrumentCreate(Strict):
    exchange: Literal["XNSE", "XBOM"]
    symbol: str = Field(min_length=1, max_length=64, pattern=r"^[A-Z0-9&._-]+$")
    name: str = Field(min_length=1, max_length=256)
    metal: Literal["GOLD", "SILVER"]
    currency: Literal["INR"]
    isin: str | None = Field(default=None, pattern=r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")


class InstrumentPatch(Strict):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    active: bool | None = None
    exchange: Literal["XNSE", "XBOM"] | None = None
    symbol: str | None = Field(
        default=None, min_length=1, max_length=64, pattern=r"^[A-Z0-9&._-]+$"
    )
    metal: Literal["GOLD", "SILVER"] | None = None
    currency: Literal["INR"] | None = None
    isin: str | None = Field(default=None, pattern=r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")

    @model_validator(mode="after")
    def explicit_values(self):
        if any(getattr(self, key) is None for key in self.model_fields_set - {"isin"}):
            raise ValueError("Only ISIN can be explicitly cleared")
        return self


class WatchlistCreate(Strict):
    name: str = Field(min_length=1, max_length=256)


class MemberCreate(Strict):
    instrument_id: UUID


class CalendarProfile(Strict):
    evidence_ref: str = Field(min_length=1, max_length=1000)
    version: str = Field(min_length=1, max_length=64)
    coverage_start: date
    coverage_end: date
    session_dates: list[date] = Field(max_length=20_000)

    @model_validator(mode="after")
    def coherent(self):
        if self.coverage_start > self.coverage_end or any(
            not self.coverage_start <= d <= self.coverage_end for d in self.session_dates
        ):
            raise ValueError("Invalid calendar coverage")
        if len(self.session_dates) != len(set(self.session_dates)):
            raise ValueError("Duplicate calendar sessions")
        return self


class FreshnessProfile(Strict):
    evidence_ref: str = Field(min_length=1, max_length=1000)
    assessment_as_of: datetime
    expected_latest_session: date

    @field_validator("assessment_as_of")
    @classmethod
    def aware(cls, v):
        if v.tzinfo is None or v.utcoffset() is None:
            raise ValueError("Timezone required")
        return v


class AcquisitionReview(Strict):
    timestamp_policy: Literal["UNIX_SECONDS_IST_CANDIDATE_V1"]
    allow_provisional_session_dates: bool = False
    review_ref: str = Field(min_length=1, max_length=1000)


class SourceProfile(Strict):
    data_class: Literal["REAL_MARKET", "SYNTHETIC_TEST"]
    policy_version: Literal["quality-v1"] = "quality-v1"
    acquisition_review: AcquisitionReview | None = None
    calendar: CalendarProfile | None = None
    freshness: FreshnessProfile | None = None
    known_break_dates: list[date] = Field(default_factory=list, max_length=10_000)
    adjustment_definition_ref: str | None = Field(default=None, max_length=1000)


class SourceCreate(Strict):
    label: str = Field(min_length=1, max_length=256)
    source_kind: Literal["USER_CSV", "DHANHQ"] = "USER_CSV"
    contract_version: Literal["csv-v1", "dhan-daily-v1-provisional"] = "csv-v1"
    profile: SourceProfile

    @model_validator(mode="after")
    def matching_contract(self):
        if (self.source_kind == "USER_CSV") != (self.contract_version == "csv-v1"):
            raise ValueError("Source kind and contract must match")
        return self


class CanonicalImportMetadata(Strict):
    instrument_id: UUID
    source_id: UUID
    interval: Literal["1d"] = "1d"
    price_basis: Literal["PROVIDER_ADJUSTED"] = "PROVIDER_ADJUSTED"
    quality_policy_version: Literal["quality-v1"] = "quality-v1"
    qualification_ref: str = Field(min_length=1, max_length=1000)
    plan_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    requested_start: date
    requested_end: date


class PermittedUses(Strict):
    retrieval: bool
    storage: bool
    analysis: bool
    display: bool


class Qualification(Strict):
    qualification: Literal["UNVERIFIED", "QUALIFIED_FOR_RESEARCH", "RESTRICTED"]
    rights_evidence_ref: str | None = Field(default=None, max_length=1000)
    permitted_uses: PermittedUses
    retention_review_ref: str | None = Field(default=None, max_length=1000)
    profile: SourceProfile | None = None

    @model_validator(mode="after")
    def evidence(self):
        if self.qualification == "QUALIFIED_FOR_RESEARCH" and (
            not self.rights_evidence_ref
            or not self.retention_review_ref
            or not all(self.permitted_uses.model_dump().values())
        ):
            raise ValueError(
                "Qualified use requires evidence, retention review and all permitted uses"
            )
        return self


class ImportMetadata(Strict):
    instrument_id: UUID
    source_id: UUID
    interval: Literal["1d"]
    price_basis: Literal["RAW_CLOSE", "PROVIDER_ADJUSTED", "UNKNOWN"]
    mapping_version: str = Field(min_length=1, max_length=64)
    column_map: dict[str, str] = Field(min_length=2, max_length=12)
    quality_policy_version: str = Field(min_length=1, max_length=64)
    qualification_ref: str = Field(min_length=1, max_length=1000)

    @field_validator("column_map")
    @classmethod
    def mapping(cls, value):
        allowed = {
            "trading_date",
            "close",
            "open",
            "high",
            "low",
            "volume",
            "symbol",
            "currency",
            "provider_published_at",
            "event_time",
        }
        if not {"trading_date", "close"} <= set(value) or not set(value) <= allowed:
            raise ValueError("Invalid canonical mapping")
        if len(set(value.values())) != len(value) or any(
            not h or len(h) > 100 for h in value.values()
        ):
            raise ValueError("Invalid or duplicate mapped header")
        return value


class ComparisonSelection(Strict):
    instrument_id: UUID
    source_id: UUID
    price_basis: Literal["RAW_CLOSE", "PROVIDER_ADJUSTED", "UNKNOWN"]


class ComparisonRequest(Strict):
    qualification_mode: Literal["STRICT_COMPATIBILITY", "PROVISIONAL_AS_DELIVERED"] = "STRICT_COMPATIBILITY"
    acknowledge_source_limitations: bool = False
    series: list[ComparisonSelection] = Field(min_length=2, max_length=10)
    start: date
    end: date
    assessment_as_of: datetime | None = None

    @model_validator(mode="after")
    def coherent_comparison(self):
        if (self.qualification_mode == "PROVISIONAL_AS_DELIVERED") != self.acknowledge_source_limitations:
            raise ValueError("Provisional comparison requires explicit source-limitation acknowledgement")
        if self.start > self.end or len({s.instrument_id for s in self.series}) != len(self.series):
            raise ValueError("Select distinct listings and a coherent explicit period")
        if self.assessment_as_of is not None and (
            self.assessment_as_of.tzinfo is None or self.assessment_as_of.utcoffset() is None
        ):
            raise ValueError("Assessment timezone required")
        return self
