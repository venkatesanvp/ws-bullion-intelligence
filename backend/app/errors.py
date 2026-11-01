from dataclasses import dataclass, field


@dataclass
class APIError(Exception):
    status: int
    code: str
    message: str
    details: list[dict] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    def payload(self, request_id: str):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "request_id": request_id,
                "details": self.details,
            },
            **self.extra,
        }
