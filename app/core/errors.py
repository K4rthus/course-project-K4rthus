from typing import Any, Dict, Optional
from uuid import uuid4
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from pydantic import BaseModel


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    correlation_id: Optional[str] = None
    instance: Optional[str] = None


def problem(
    status_code: int,
    title: str,
    detail: str = None,
    error_type: str = "about:blank",
    instance: str = None,
    extras: Dict[str, Any] = None
) -> JSONResponse:
    correlation_id = str(uuid4())
    problem_data = ProblemDetails(
        type=error_type,
        title=title,
        status=status_code,
        detail=detail,
        correlation_id=correlation_id,
        instance=instance
    )
    
    if extras:
        problem_data_dict = problem_data.model_dump()
        problem_data_dict.update(extras)
    else:
        problem_data_dict = problem_data.model_dump()
    
    return JSONResponse(
        status_code=status_code,
        content=problem_data_dict,
        headers={"Content-Type": "application/problem+json"}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return problem(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        title="Validation Error",
        detail="One or more validation errors occurred",
        error_type="/errors/validation",
        instance=str(request.url)
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        error_type = "/errors/not_found"
        title = "Not Found"
    else:
        error_type = "/errors/http"
        title = exc.detail
    
    return problem(
        status_code=exc.status_code,
        title=title,
        detail=exc.detail,
        error_type=error_type,
        instance=str(request.url)
    )


async def general_exception_handler(request: Request, exc: Exception):
    detail = "An internal server error occurred" 
    
    return problem(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title="Internal Server Error",
        detail=detail,
        error_type="/errors/server",
        instance=str(request.url)
    )