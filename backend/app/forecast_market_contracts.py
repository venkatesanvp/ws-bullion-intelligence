"""Explicit Package4 conditional real-research contracts; synthetic guards remain intact."""

from typing import Literal
from pydantic import Field, model_validator
from .forecast_contracts import (
    Provenance,
    ForecastObservation,
    ForecastDataset,
    QualityRequirements,
    ForecastRequest,
    ForecastSnapshot,
    ForecastResult,
    ModelDescriptor,
    Stamp,
    Name,
)


class MarketProvenance(Provenance):
    data_class: Literal["REAL_MARKET"]
    availability_policy: Literal["LOCAL_FIRST_SEEN_ONLY"]
    permission_scope: Literal["TRANSIENT_OWNER_RESEARCH_ONLY"]
    source_qualification: Literal[
        "TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED", "QUALIFIED_FOR_RESEARCH"
    ]
    source_profile_fingerprint: Name
    canonical_source_basis: Literal["PROVIDER_ADJUSTED"] = "PROVIDER_ADJUSTED"
    adjustment_reference: str | None = Field(default=None, max_length=2048)
    timestamp_policy_reference: str | None = Field(default=None, max_length=2048)
    limitations: tuple[str, ...]


class MarketObservation(ForecastObservation):
    quality: Literal["CONDITIONAL_OWNER_RESEARCH", "DEGRADED", "UNKNOWN"]
    source_event_at: Stamp | None
    source_event_precision: str | None
    provider_published_at: Stamp | None
    canonical_id: Name
    canonical_hash: Name
    batch_id: Name
    source_row: int = Field(strict=True, ge=1)
    session_time_policy: Literal["EXCHANGE_SESSION_CLOSE_PROXY_NOT_PROVIDER_TIMESTAMP"]
    finality: Literal["PRIOR_DATE_DAILY_COMPLETED_CANDIDATE"]


class MarketDataset(ForecastDataset):
    schema_version: Literal["forecast-real-input-v1"] = "forecast-real-input-v1"
    provenance: MarketProvenance
    basis: Literal["PROVIDER_ADJUSTED_UNVERIFIED"]
    observations: tuple[MarketObservation, ...] = Field(max_length=5000)

    @model_validator(mode="after")
    def limited_basis(self):
        if (
            self.adjustment_policy_id != "PROVIDER_AS_DELIVERED_ADJUSTMENT_UNQUALIFIED"
            or self.adjustment_vintage_at is not None
        ):
            raise ValueError("NO_QUALIFIED_ADJUSTMENT_VINTAGE")
        return self


class MarketQuality(QualityRequirements):
    quality: Literal["CONDITIONAL_OWNER_RESEARCH"] = "CONDITIONAL_OWNER_RESEARCH"


class MarketRequest(ForecastRequest):
    quality: MarketQuality = Field(default_factory=MarketQuality)
    origin_policy: Literal["LATEST_ELIGIBLE_FINAL_WITH_EXPLICIT_LAG"] = (
        "LATEST_ELIGIBLE_FINAL_WITH_EXPLICIT_LAG"
    )
    max_origin_lag_sessions: int = Field(default=1, strict=True, ge=0, le=1)


class MarketSnapshot(ForecastSnapshot):
    provenance: MarketProvenance
    observations: tuple[MarketObservation, ...]
    basis: Literal["PROVIDER_ADJUSTED_UNVERIFIED"]
    quality: MarketQuality


class MarketDescriptor(ModelDescriptor):
    lifecycle: Literal["TRANSIENT_CONDITIONAL_REAL_RESEARCH_ONLY"] = (
        "TRANSIENT_CONDITIONAL_REAL_RESEARCH_ONLY"
    )


class MarketResult(ForecastResult):
    contract_version: Literal["forecast-research-v2"] = "forecast-research-v2"
    provenance: MarketProvenance
    basis: Literal["PROVIDER_ADJUSTED_UNVERIFIED"]
    model: MarketDescriptor
    data_quality: Literal["CONDITIONAL_OWNER_RESEARCH"] = "CONDITIONAL_OWNER_RESEARCH"
