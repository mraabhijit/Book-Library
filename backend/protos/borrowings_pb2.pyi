import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protos import books_pb2 as _books_pb2
from protos import members_pb2 as _members_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BorrowRequest(_message.Message):
    __slots__ = ("book_id", "member_id", "due_date")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    DUE_DATE_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    member_id: int
    due_date: _timestamp_pb2.Timestamp
    def __init__(self, book_id: _Optional[int] = ..., member_id: _Optional[int] = ..., due_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class BorrowResponse(_message.Message):
    __slots__ = ("id", "book_id", "member_id", "due_date", "borrowed_date", "status", "returned_date", "book", "member")
    ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    DUE_DATE_FIELD_NUMBER: _ClassVar[int]
    BORROWED_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RETURNED_DATE_FIELD_NUMBER: _ClassVar[int]
    BOOK_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    id: int
    book_id: int
    member_id: int
    due_date: _timestamp_pb2.Timestamp
    borrowed_date: _timestamp_pb2.Timestamp
    status: str
    returned_date: _timestamp_pb2.Timestamp
    book: _books_pb2.Book
    member: _members_pb2.Member
    def __init__(self, id: _Optional[int] = ..., book_id: _Optional[int] = ..., member_id: _Optional[int] = ..., due_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., borrowed_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ..., returned_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., book: _Optional[_Union[_books_pb2.Book, _Mapping]] = ..., member: _Optional[_Union[_members_pb2.Member, _Mapping]] = ...) -> None: ...

class GetBorrowingsResponse(_message.Message):
    __slots__ = ("borrowings",)
    BORROWINGS_FIELD_NUMBER: _ClassVar[int]
    borrowings: _containers.RepeatedCompositeFieldContainer[BorrowResponse]
    def __init__(self, borrowings: _Optional[_Iterable[_Union[BorrowResponse, _Mapping]]] = ...) -> None: ...

class ReturnRequest(_message.Message):
    __slots__ = ("book_id", "member_id")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    member_id: int
    def __init__(self, book_id: _Optional[int] = ..., member_id: _Optional[int] = ...) -> None: ...

class ReturnResponse(_message.Message):
    __slots__ = ("id", "book_id", "member_id", "status", "returned_date", "book", "member")
    ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RETURNED_DATE_FIELD_NUMBER: _ClassVar[int]
    BOOK_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    id: int
    book_id: int
    member_id: int
    status: str
    returned_date: _timestamp_pb2.Timestamp
    book: _books_pb2.Book
    member: _members_pb2.Member
    def __init__(self, id: _Optional[int] = ..., book_id: _Optional[int] = ..., member_id: _Optional[int] = ..., status: _Optional[str] = ..., returned_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., book: _Optional[_Union[_books_pb2.Book, _Mapping]] = ..., member: _Optional[_Union[_members_pb2.Member, _Mapping]] = ...) -> None: ...

class GetBorrowRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMemberBorrowingsRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...
