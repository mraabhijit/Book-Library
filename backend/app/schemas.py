from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    description: str | None = None
    is_available: bool = True


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    description: str | None = None


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    description: str | None = None
    is_available: bool | None = None


class MemberBase(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class MemberCreate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)
    phone: str | None = Field(default=None, min_length=10, max_length=10)


class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class MemberUpdate(MemberBase): ...


class BorrowRequest(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)
    due_date: datetime | None = None


class BorrowResponse(BorrowRequest):
    id: int
    borrowed_date: datetime
    status: str = "borrowed"
    returned_date: datetime | None = None
    book: BookResponse
    member: MemberResponse


class ReturnRequest(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)


class ReturnResponse(ReturnRequest):
    id: int
    status: str = "returned"
    book: BookResponse
    member: MemberResponse
    returned_date: datetime


class StaffCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=200)
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    password: str = Field(min_length=8)


class StaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str
