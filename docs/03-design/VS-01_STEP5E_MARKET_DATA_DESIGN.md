# Step 5E market-session implementation design

Authority: owner's Step 5E implementation instruction, 2026-11-06. Trace: D-14/D-16; REQ-02 market-data/quality/timeframe requirements; REQ-03-007 approved deterministic indicators; REQ-05 local security; DC-02/03/04/05/07; SQ-01/T-03 remain source-qualification gates. Requirements baseline and Decision Register are unchanged.

## P0 implemented architecture

The existing verified Dhan instrument catalog and provider-independent Listing remain authoritative. DhanMarketProvider extends the existing daily adapter with a batched quote operation and bounded intraday operation; it imports no account/trading SDK. MarketSessionProvider, MarketQuote, IntradayCandle and SessionResult are provider-neutral contracts. The existing canonical price guard/strict Decimal JSON decoder and pure indicator engine are reused. No second database/ingestion architecture.

ProviderBudget serializes all normal daily/quote/intraday calls at <=1/second, bounds daily calls, and pauses after authentication/entitlement/rate/service/network failures. There are no automatic HTTP retries, redirects or proxy credential forwarding. Separate quote and intraday locks single-flight requests; operation queues are bounded. Quotes batch configured instruments, cache last valid values and report event/retrieval ages separately. Historical/current intraday ranges have different freshness/negative-cache policies, bounded partition/call/row/coverage limits, and cancellation between chunks.

REST quote headers require both access-token and client-id. App name/key/secret are not sent. The ambiguous ohlc.close is retained as provider_close; previous close is derived from the documented last_price minus net_change relationship, corroborated against provider_close when equal. Differences are flagged instead of silently relabelling provider_close. Price changes use the explicit 34-digit Decimal context and existing twelve-place derived serialization.

Observed quote strings use DD/MM/YYYY HH:MM:SS; the explicit IST interpretation matched contemporaneous backend time for all four instruments. Intraday uses an explicit Unix-seconds/IST policy, supported by the official SDK converter and actual boundary checks. These are corroborated policies, not a claim of a complete universal timestamp contract. A last-trade timestamp is not quote-generation time.

Intraday API midnight-to-midnight request bounds avoid the opening-bar omission observed with fromDate=09:15. Actual Tata Gold 1-minute aggregation matched all 75 five-minute OHLCV observations; start-aligned windows matched, end-aligned windows did not consistently match. End timestamps are inferred from interval and clipped to the reviewed regular session close, not provider-published fields. A 60-second settlement guard keeps forming/recent bars provisional. Special sessions outside the reviewed template need additional qualification.

## Classification and analytics

Live quotes never enter the historical daily store. Intraday keys include ISIN, interval and aware start timestamp; rows preserve exact source epoch text/row, provider, retrieval and request-range evidence. Per-candle volume is documented and the 1m/5m sum was corroborated; aggregation is conditional on this volume-semantics flag. Missing candles are not imputed. Missing expected bars/session boundaries restart the unchanged indicator engine.

Daily and intraday indicators use separate inputs and explicit timeframe labels. Intraday calculations use completed bars and a bounded deterministic warm-up prefix. Current-session aggregates are always PROVISIONAL - INTRADAY AGGREGATED, even when all regular-session bars have completed, until official daily publication is separately considered. No quote snapshot is an official daily candle; no total-return, signal, investment-performance or replay qualification is inferred.

## Security, retention and deployment

Capability gates default false in committed configuration and are enabled only locally under standing authority. Credential values are unchanged and remain API-only. RAM caches cap quotes by the verified catalog, intraday rows at 100000, coverage metadata at its configured cap, and metadata receipts at 256. Overflow preserves existing rows. There are no provider-price PostgreSQL writes, raw-response files or hidden caches.

Authenticated, once-only cache transfer preserves canonical daily rows/IDs and available quote/intraday provenance through deployment entirely in RAM. Legacy rows whose original numeric epoch/full batch metadata were not exposed remain explicitly limited; missing evidence is never reconstructed. New transfer payloads preserve actual intraday source epoch strings. Ordinary restart still loses caches unless the controlled handoff is used; this is not durable backup or storage-rights approval.

## P1 extension boundary

WebSocket transport/decoder, secure normalized frontend events, bounded reconnect/fallback and official/provisional reconciliation are authorized next, but P0 must pass its separate software/live gate first. They must reuse this catalog, cache, budget policy and historical validator. No provisional/stream value may overwrite a qualified daily observation. P0 completion does not mark owner UAT or full VS-01 acceptance.

Official contracts reviewed 2026-11-06: [quotes](https://dhanhq.co/docs/v2/market-quote/), [intraday](https://dhanhq.co/docs/v2/historical-data/), [SDK time conversion](https://github.com/dhan-oss/DhanHQ-py/blob/main/src/dhanhq/dhanhq.py), [market feed](https://dhanhq.co/docs/v2/live-market-feed/). These references establish API behavior, not unrestricted storage/redistribution rights.
