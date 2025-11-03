from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.errors import (
    general_exception_handler,
    http_exception_handler,
    problem,
    validation_exception_handler,
)
from .core.security import sanitize_text, setup_rate_limiting

app = FastAPI(
    title="Suggestion Box API",
    description="Анонимная система предложений",
    version="1.0.0",
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

setup_rate_limiting(app)


@app.get("/health")
def health():
    return {"status": "ok"}


_DB = {"suggestions": [], "next_id": 1}


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return problem(
        status_code=exc.status,
        title=exc.code,
        detail=exc.message,
        error_type="/errors/business",
        instance=str(request.url),
    )


@app.post("/suggestions")
def create_suggestion(title: str, text: str):
    if not title or len(title) > 100:
        raise ApiError(
            code="validation_error", message="title must be 1..100 chars", status=422
        )

    if not text or len(text) > 2000:
        raise ApiError(
            code="validation_error", message="text must be 1..2000 chars", status=422
        )

    sanitized_title = sanitize_text(title, max_length=100)
    sanitized_text = sanitize_text(text, max_length=2000)

    suggestion = {
        "id": _DB["next_id"],
        "title": sanitized_title,
        "text": sanitized_text,
        "status": "pending",
        "user_id": "anonymous",
    }
    _DB["suggestions"].append(suggestion)
    _DB["next_id"] += 1
    return suggestion


@app.get("/suggestions")
def get_suggestions(status: str = None):
    suggestions = _DB["suggestions"]
    if status:
        suggestions = [s for s in suggestions if s["status"] == status]
    return suggestions


@app.get("/suggestions/{suggestion_id}")
def get_suggestion(suggestion_id: int):
    for suggestion in _DB["suggestions"]:
        if suggestion["id"] == suggestion_id:
            return suggestion
    raise HTTPException(status_code=404, detail="Suggestion not found")
