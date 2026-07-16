from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response format.
    Har API iska use karegi taaki frontend ko
    consistent structure mile.

    Example:
    {
        "success": true,
        "message": "User created",
        "data": { ...user data... }
    }
    """
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """
    List endpoints ke liye — page number, total count ke saath.
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class ErrorResponse(BaseModel):
    """
    Error response format.
    """
    success: bool = False
    message: str
    detail: Optional[str] = None