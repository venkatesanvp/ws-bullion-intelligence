import hmac
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, File, Form, Header, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import and_, create_engine, or_, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

from .config import SCHEMA_REVISION, Settings
from .errors import APIError
from .ingestion import batch_data, ingest
from .models import (
    DataSource,
    ImportBatch,
    Instrument,
    Observation,
    QualityResult,
    Watchlist,
    WatchlistMember,
    now,
)
from .queries import find, series, series_meta
from .research import register_research
from .schemas import (
    ImportMetadata,
    InstrumentCreate,
    InstrumentPatch,
    MemberCreate,
    Qualification,
    SourceCreate,
    WatchlistCreate,
)
from .serialization import decode_cursor, digest, encode_cursor, plain

logger = logging.getLogger("bullion")
Basis = Literal["RAW_CLOSE", "PROVIDER_ADJUSTED", "UNKNOWN"]
Limit = Annotated[int, Query(ge=1, le=1000)]


class BodyLimitMiddleware:
    def __init__(self, app, max_bytes):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] in {"GET", "HEAD", "OPTIONS"}:
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > self.max_bytes:
                error = APIError(
                    413, "REQUEST_TOO_LARGE", "Upload exceeds the configured request bound."
                )
                return await JSONResponse(
                    error.payload(scope.get("state", {}).get("request_id", str(uuid4()))),
                    status_code=413,
                )(scope, receive, send)
            chunks.append(message)
            if not message.get("more_body", False):
                break
        iterator = iter(chunks)

        async def replay():
            try:
                return next(iterator)
            except StopIteration:
                return await receive()

        await self.app(scope, replay, send)


def schema_ready(engine):
    try:
        with engine.connect() as conn:
            return conn.scalar(text("SELECT version_num FROM alembic_version")) == SCHEMA_REVISION
    except SQLAlchemyError:
        return False


def get_db(request: Request):
    engine = request.app.state.engine
    if not schema_ready(engine):
        raise APIError(
            503, "DEPENDENCY_NOT_READY", "Database is unavailable or migrations are required."
        )
    with engine.connect() as conn:
        if request.method == "GET" or request.url.path == "/api/v1/comparisons":
            conn = conn.execution_options(isolation_level="REPEATABLE READ")
        with Session(bind=conn, expire_on_commit=False) as db:
            yield db


DB = Annotated[Session, Depends(get_db)]


def response(request, data, meta=None, status=200):
    info = {"request_id": request.state.request_id, "served_at": plain(now()), **(meta or {})}
    return JSONResponse(plain({"data": data, "meta": info}), status_code=status)


def paginated(request, db, statement, model, scope, cursor, limit):
    if cursor:
        last = UUID(
            decode_cursor(
                cursor, request.app.state.settings.local_app_token.get_secret_value(), scope
            )
        )
        statement = statement.where(model.id > last)
    rows = list(db.scalars(statement.order_by(model.id).limit(limit + 1)))
    more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = (
        encode_cursor(
            {"scope": scope, "last": str(rows[-1].id)},
            request.app.state.settings.local_app_token.get_secret_value(),
        )
        if more
        else None
    )
    return rows, {"next_cursor": next_cursor, "limit": limit}


def create_app(settings: Settings | None = None):
    settings = settings or Settings()
    engine = create_engine(
        settings.database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5}
    )

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.dispose()

    app = FastAPI(
        title="Bullion Intelligence Data Workbench",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.settings, app.state.engine = settings, engine
    app.add_middleware(BodyLimitMiddleware, max_bytes=settings.max_import_bytes + 65_536)

    @app.middleware("http")
    async def access_boundary(request: Request, call_next):
        started = time.monotonic()
        request.state.request_id = str(uuid4())
        try:
            host = urlsplit("http://" + request.headers.get("host", "")).hostname
        except ValueError:
            host = None
        error = None
        if host not in settings.allowed_hosts.split(","):
            error = APIError(400, "INVALID_HOST", "Only configured local hosts are allowed.")
        origin = request.headers.get("origin")
        if origin and origin not in settings.origins:
            error = APIError(403, "ORIGIN_NOT_ALLOWED", "Origin is not allowed.")
        public = request.url.path == "/api/v1/health/live" or request.method == "OPTIONS"
        if not public and error is None:
            auth = request.headers.get("authorization", "")
            supplied = auth[7:] if auth[:7].lower() == "bearer " else ""
            if not hmac.compare_digest(
                supplied.encode(), settings.local_app_token.get_secret_value().encode()
            ):
                error = APIError(401, "UNAUTHORIZED", "Enter the local application token.")
            elif (
                request.method not in {"GET", "HEAD", "OPTIONS"} and origin not in settings.origins
            ):
                error = APIError(
                    403, "ORIGIN_REQUIRED", "A configured local Origin is required for changes."
                )
        if error:
            result = JSONResponse(error.payload(request.state.request_id), status_code=error.status)
        else:
            try:
                result = await call_next(request)
            except Exception as exc:
                uncertain = (
                    request.method == "POST" and request.url.path == "/api/v1/import-batches"
                )
                failure = APIError(
                    503 if uncertain else 500,
                    "IMPORT_OUTCOME_UNKNOWN" if uncertain else "INTERNAL_ERROR",
                    "Resolve or retry the same request key."
                    if uncertain
                    else "The request could not be completed.",
                )
                logger.error(
                    json.dumps(
                        {
                            "event": failure.code,
                            "request_id": request.state.request_id,
                            "exception_type": type(exc).__name__,
                        }
                    )
                )
                result = JSONResponse(
                    failure.payload(request.state.request_id), status_code=failure.status
                )
        result.headers["X-Request-ID"] = request.state.request_id
        result.headers["Cache-Control"] = "no-store"
        result.headers["X-Content-Type-Options"] = "nosniff"
        logger.info(
            json.dumps(
                {
                    "event": "request",
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": result.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                }
            )
        )
        return result

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        expose_headers=["X-Request-ID"],
    )

    @app.exception_handler(APIError)
    async def api_error(request, exc):
        return JSONResponse(plain(exc.payload(request.state.request_id)), status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        details = [
            {"field": ".".join(str(x) for x in e["loc"]), "code": e["type"]} for e in exc.errors()
        ]
        return JSONResponse(
            APIError(
                422, "VALIDATION_ERROR", "Check the required fields and formats.", details
            ).payload(request.state.request_id),
            status_code=422,
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request, exc):
        return JSONResponse(
            APIError(
                409, "CONFLICT", "A record conflicts with an existing identity or constraint."
            ).payload(request.state.request_id),
            status_code=409,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        uncertain = request.method == "POST" and request.url.path == "/api/v1/import-batches"
        error = APIError(
            503,
            "IMPORT_OUTCOME_UNKNOWN" if uncertain else "DATABASE_UNAVAILABLE",
            "Resolve or retry the same request key before changing it."
            if uncertain
            else "Database is unavailable.",
            extra={"request_key": request.headers.get("idempotency-key")} if uncertain else {},
        )
        logger.error(json.dumps({"event": error.code, "request_id": request.state.request_id}))
        return JSONResponse(error.payload(request.state.request_id), status_code=503)

    router = APIRouter(prefix="/api/v1")

    @router.get("/health/live")
    def live(request: Request):
        return response(request, {"status": "alive"})

    @router.get("/health/ready")
    def ready(request: Request):
        if not schema_ready(engine):
            raise APIError(503, "DEPENDENCY_NOT_READY", "Database or schema is not ready.")
        return response(request, {"status": "ready", "schema_revision": SCHEMA_REVISION})

    @router.get("/instruments")
    def instruments(
        request: Request,
        db: DB,
        metal: Literal["GOLD", "SILVER"] | None = None,
        cursor: str | None = None,
        limit: Limit = 100,
    ):
        stmt = select(Instrument)
        if metal:
            stmt = stmt.where(Instrument.metal == metal)
        rows, page = paginated(
            request,
            db,
            stmt,
            Instrument,
            digest({"list": "instruments", "metal": metal}),
            cursor,
            limit,
        )
        return response(request, rows, {"page": page})

    @router.post("/instruments")
    def add_instrument(body: InstrumentCreate, request: Request, db: DB):
        with db.begin():
            item = Instrument(**body.model_dump())
            db.add(item)
            db.flush()
        return response(request, item, status=201)

    @router.patch("/instruments/{instrument_id}")
    def patch_instrument(instrument_id: UUID, body: InstrumentPatch, request: Request, db: DB):
        with db.begin():
            item = db.scalar(
                select(Instrument).where(Instrument.id == instrument_id).with_for_update()
            )
            if item is None:
                raise APIError(404, "NOT_FOUND", "Instrument not found.")
            changes = body.model_dump(exclude_unset=True)
            identity_changes = {
                k
                for k in changes
                if k in {"exchange", "symbol", "metal", "currency", "isin"}
                and getattr(item, k) != changes[k]
            }
            if identity_changes and db.scalar(
                select(Observation.id).where(Observation.instrument_id == item.id).limit(1)
            ):
                raise APIError(
                    409,
                    "IMMUTABLE_IDENTITY",
                    "A listing with accepted history cannot change financial identity.",
                )
            for key, value in changes.items():
                setattr(item, key, value)
            db.flush()
        return response(request, item)

    def watch_data(db, item):
        result = plain(item)
        result["members"] = [
            plain(x)
            for x in db.scalars(
                select(Instrument)
                .join(WatchlistMember, WatchlistMember.instrument_id == Instrument.id)
                .where(WatchlistMember.watchlist_id == item.id)
                .order_by(Instrument.symbol)
            )
        ]
        return result

    @router.get("/watchlists")
    def watchlists(request: Request, db: DB, cursor: str | None = None, limit: Limit = 100):
        rows, page = paginated(
            request, db, select(Watchlist), Watchlist, "watchlists", cursor, limit
        )
        return response(request, [watch_data(db, w) for w in rows], {"page": page})

    @router.post("/watchlists")
    def add_watchlist(body: WatchlistCreate, request: Request, db: DB):
        with db.begin():
            item = Watchlist(name=body.name)
            db.add(item)
            db.flush()
        return response(request, watch_data(db, item), status=201)

    @router.get("/watchlists/{watchlist_id}")
    def get_watchlist(watchlist_id: UUID, request: Request, db: DB):
        return response(request, watch_data(db, find(db, Watchlist, watchlist_id)))

    @router.patch("/watchlists/{watchlist_id}")
    def patch_watchlist(watchlist_id: UUID, body: WatchlistCreate, request: Request, db: DB):
        with db.begin():
            item = find(db, Watchlist, watchlist_id)
            item.name = body.name
            db.flush()
        return response(request, watch_data(db, item))

    @router.post("/watchlists/{watchlist_id}/members")
    def add_member(watchlist_id: UUID, body: MemberCreate, request: Request, db: DB):
        with db.begin():
            find(db, Watchlist, watchlist_id)
            find(db, Instrument, body.instrument_id)
            old = db.get(WatchlistMember, (watchlist_id, body.instrument_id))
            if old:
                return response(request, old)
            item = WatchlistMember(watchlist_id=watchlist_id, instrument_id=body.instrument_id)
            db.add(item)
            db.flush()
        return response(request, item, status=201)

    @router.delete("/watchlists/{watchlist_id}/members/{instrument_id}")
    def remove_member(watchlist_id: UUID, instrument_id: UUID, db: DB):
        with db.begin():
            find(db, Watchlist, watchlist_id)
            item = db.get(WatchlistMember, (watchlist_id, instrument_id))
            if item:
                db.delete(item)
        return Response(status_code=204)

    @router.get("/data-sources")
    def sources(request: Request, db: DB, cursor: str | None = None, limit: Limit = 100):
        rows, page = paginated(
            request, db, select(DataSource), DataSource, "data-sources", cursor, limit
        )
        return response(request, rows, {"page": page})

    @router.post("/data-sources")
    def add_source(body: SourceCreate, request: Request, db: DB):
        with db.begin():
            item = DataSource(
                label=body.label,
                contract_version=body.contract_version,
                profile=body.profile.model_dump(mode="json"),
            )
            db.add(item)
            db.flush()
        return response(request, item, status=201)

    @router.patch("/data-sources/{source_id}/qualification")
    def qualify(source_id: UUID, body: Qualification, request: Request, db: DB):
        with db.begin():
            item = db.scalar(select(DataSource).where(DataSource.id == source_id).with_for_update())
            if item is None:
                raise APIError(404, "NOT_FOUND", "Source not found.")
            if body.profile and body.profile.data_class != item.profile["data_class"]:
                raise APIError(
                    409,
                    "SOURCE_CLASS_IMMUTABLE",
                    "Register a separate source for a different data classification.",
                )
            item.qualification = body.qualification
            item.rights_evidence_ref = body.rights_evidence_ref
            item.permitted_uses = {
                **body.permitted_uses.model_dump(),
                "retention_review_ref": body.retention_review_ref,
            }
            item.reviewed_at = now()
            if body.profile:
                item.profile = body.profile.model_dump(mode="json")
            db.flush()
        return response(request, item, {"verification": "OWNER_RECORDED_NOT_THIRD_PARTY_VERIFIED"})

    @router.post("/import-batches")
    async def import_file(
        request: Request,
        db: DB,
        metadata_json: Annotated[str, Form(max_length=65_536)],
        file: Annotated[UploadFile, File()],
        idempotency_key: Annotated[UUID, Header()],
    ):
        filename = file.filename or ""
        if not filename.lower().endswith(".csv") or any(
            c in filename for c in ("/", chr(92), chr(0))
        ):
            raise APIError(
                415, "UNSUPPORTED_FILE_TYPE", "Upload a plain CSV filename, not a path or archive."
            )
        content = await file.read(settings.max_import_bytes + 1)
        await file.close()
        if len(content) > settings.max_import_bytes:
            raise APIError(413, "FILE_TOO_LARGE", "CSV exceeds the configured upload limit.")
        try:
            meta = ImportMetadata.model_validate_json(metadata_json)
        except ValidationError:
            raise APIError(
                422, "INVALID_METADATA", "Check the explicit CSV mapping and source profile."
            ) from None
        # All database work is synchronous and runs off the event loop.
        from starlette.concurrency import run_in_threadpool

        status, payload = await run_in_threadpool(
            ingest,
            db,
            content,
            filename,
            meta,
            idempotency_key,
            request.state.request_id,
            settings.max_import_rows,
        )
        return JSONResponse(plain(payload), status_code=status)

    @router.get("/import-batches")
    def batches(
        request: Request,
        db: DB,
        source_id: UUID | None = None,
        instrument_id: UUID | None = None,
        cursor: str | None = None,
        limit: Limit = 100,
    ):
        stmt = select(ImportBatch)
        if source_id:
            stmt = stmt.where(ImportBatch.source_id == source_id)
        if instrument_id:
            stmt = stmt.where(ImportBatch.instrument_id == instrument_id)
        scope = digest({"list": "batches", "source": source_id, "instrument": instrument_id})
        if cursor:
            last = decode_cursor(cursor, settings.local_app_token.get_secret_value(), scope)
            stamp = datetime.fromisoformat(last["submitted_at"].replace("Z", "+00:00"))
            key = UUID(last["id"])
            stmt = stmt.where(
                or_(
                    ImportBatch.submitted_at > stamp,
                    and_(ImportBatch.submitted_at == stamp, ImportBatch.id > key),
                )
            )
        rows = list(
            db.scalars(stmt.order_by(ImportBatch.submitted_at, ImportBatch.id).limit(limit + 1))
        )
        more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = (
            encode_cursor(
                {
                    "scope": scope,
                    "last": {"submitted_at": plain(rows[-1].submitted_at), "id": str(rows[-1].id)},
                },
                settings.local_app_token.get_secret_value(),
            )
            if more
            else None
        )
        return response(
            request,
            [batch_data(x) for x in rows],
            {"page": {"next_cursor": next_cursor, "limit": limit}},
        )

    @router.get("/import-batches/by-key/{request_key}")
    def batch_by_key(request_key: UUID, request: Request, db: DB):
        item = db.scalar(select(ImportBatch).where(ImportBatch.request_key == request_key))
        if item is None:
            raise APIError(404, "NOT_RECORDED", "No terminal outcome is recorded for this key.")
        return response(request, batch_data(item))

    @router.get("/import-batches/{batch_id}")
    def batch_by_id(batch_id: UUID, request: Request, db: DB):
        return response(request, batch_data(find(db, ImportBatch, batch_id)))

    @router.get("/import-batches/{batch_id}/issues")
    def issues(
        batch_id: UUID,
        request: Request,
        db: DB,
        severity: Literal["ERROR", "WARN", "INFO", "UNASSESSED"] | None = None,
        cursor: str | None = None,
        limit: Limit = 100,
    ):
        find(db, ImportBatch, batch_id)
        stmt = select(QualityResult).where(QualityResult.batch_id == batch_id)
        if severity:
            stmt = stmt.where(QualityResult.severity == severity)
        rows, page = paginated(
            request,
            db,
            stmt,
            QualityResult,
            digest({"batch": batch_id, "severity": severity}),
            cursor,
            limit,
        )
        return response(request, rows, {"page": page})

    def validate_range(start, end, interval):
        if interval != "1d":
            raise APIError(422, "UNSUPPORTED_INTERVAL", "Only daily observations are supported.")
        if start and end and start > end:
            raise APIError(422, "INVALID_RANGE", "Start date must be on or before end date.")

    @router.get("/instruments/{instrument_id}/history")
    def history(
        instrument_id: UUID,
        source_id: UUID,
        basis: Basis,
        request: Request,
        db: DB,
        start: date | None = None,
        end: date | None = None,
        interval: str = "1d",
        cursor: str | None = None,
        limit: Limit = 100,
        assessment_as_of: datetime | None = None,
    ):
        validate_range(start, end, interval)
        instrument, source = series(db, instrument_id, source_id)
        meta = series_meta(db, instrument, source, basis, start, end, assessment_as_of)
        scope = digest({"series": meta["series_ref"], "start": start, "end": end})
        stmt = select(Observation).where(
            Observation.instrument_id == instrument_id,
            Observation.source_id == source_id,
            Observation.interval == "1d",
            Observation.price_basis == basis,
        )
        if start:
            stmt = stmt.where(Observation.trading_date >= start)
        if end:
            stmt = stmt.where(Observation.trading_date <= end)
        if cursor:
            last = decode_cursor(cursor, settings.local_app_token.get_secret_value(), scope)
            day, key = date.fromisoformat(last["trading_date"]), UUID(last["id"])
            stmt = stmt.where(
                or_(
                    Observation.trading_date > day,
                    and_(Observation.trading_date == day, Observation.id > key),
                )
            )
        rows = list(
            db.scalars(stmt.order_by(Observation.trading_date, Observation.id).limit(limit + 1))
        )
        more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = (
            encode_cursor(
                {
                    "scope": scope,
                    "last": {"trading_date": plain(rows[-1].trading_date), "id": str(rows[-1].id)},
                },
                settings.local_app_token.get_secret_value(),
            )
            if more
            else None
        )
        meta["page"] = {"next_cursor": next_cursor, "limit": limit}
        return response(request, rows, meta)

    @router.get("/instruments/{instrument_id}/quality")
    def quality(
        instrument_id: UUID,
        source_id: UUID,
        basis: Basis,
        request: Request,
        db: DB,
        start: date | None = None,
        end: date | None = None,
        interval: str = "1d",
        assessment_as_of: datetime | None = None,
    ):
        validate_range(start, end, interval)
        instrument, source = series(db, instrument_id, source_id)
        return response(
            request, series_meta(db, instrument, source, basis, start, end, assessment_as_of)
        )

    register_research(router, get_db, response)
    app.include_router(router)
    return app


app = create_app()
