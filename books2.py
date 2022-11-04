from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from uuid import UUID

from starlette import status
from starlette.responses import JSONResponse


class NegativeNumberException(Exception):
    def __init__(self, book_to_return):
        self.book_to_return = book_to_return


app = FastAPI()


class Book(BaseModel):
    id: UUID
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    rating: int = Field(..., ge=1, le=5)

    class Config:
        schema_extra = {
            "example": {
                "id": "6b9d6a1e-0f7b-4c8b-9e7f-6a5e6a5e6a5e",
                "title": "The Hitchhiker's Guide to the Galaxy",
                "author": "Douglas Adams",
                "description": "The Hitchhiker's Guide to the Galaxy is a science fiction comedy series created by "
                               "Douglas Adams.",
                "rating": 5
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)


BOOKS = []


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(exc: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content={
            "message": f"Book {exc.book_to_return} cannot be returned because it has a negative number of copies."},
    )


@app.get("/header")
async def read_header(random_header: Optional[str] = Header(None)):
    return {"random_header": random_header}


@app.post("/books/login")
async def books_login(book_id: UUID, password: str | None = Header(default=None),
                      username: str | None = Header(default=None)):
    if password == "test1234!" and username == "FastAPIUser":
        if not BOOKS:
            create_book_no_api()
        for book in BOOKS:
            if book.id == book_id:
                return book
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password",
                            headers={"X-Error": "Invalid username or password"})


@app.get("/")
async def get_books(book_to_return: Optional[int] = None):
    if not BOOKS:
        create_book_no_api()
    if book_to_return and len(BOOKS) >= book_to_return > 0:
        i = 1
        new_books = []
        while i <= book_to_return:
            new_books.append(BOOKS[i - 1])
            i += 1
        return new_books
    elif book_to_return and book_to_return < 0:
        raise NegativeNumberException(book_to_return)
    return BOOKS


@app.get("/{book_id}")
async def get_book(book_id: UUID):
    if not BOOKS:
        create_book_no_api()
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_not_found_exception()


@app.get("/{book_id}/no-rating", response_model=BookNoRating)
async def get_book_no_rating(book_id: UUID):
    if not BOOKS:
        create_book_no_api()
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise raise_item_not_found_exception()


@app.put("/{book_id}")
async def update_book(book_id: UUID, book: Book):
    if not BOOKS:
        create_book_no_api()
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS[i] = book
            return {"success": "Book updated"}
    raise raise_item_not_found_exception()


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def add_book(book: Book):
    BOOKS.append(book)
    return book


@app.delete("/{book_id}")
async def delete_book(book_id: UUID):
    if not BOOKS:
        create_book_no_api()
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            return {"success": "Book deleted"}
    raise raise_item_not_found_exception()


def create_book_no_api():
    book1 = Book(id=UUID("c2b2f7c3-2f3b-4b3a-8e7c-1a6b9c9d0b6a"),
                 title="The Hitchhiker's Guide to the Galaxy",
                 author="Douglas Adams",
                 description="The Hitchhiker's Guide to the Galaxy is a science fiction comedy series created by "
                             "Douglas Adams.",
                 rating=5)

    book2 = Book(id=UUID("c2b2f7c3-2f3b-4b3a-8e7c-1a6b9c9d0b6b"),
                 title="The Restaurant at the End of the Universe",
                 author="Douglas Adams",
                 description="The Restaurant at the End of the Universe is a science fiction comedy novel by Douglas "
                             "Adams.",
                 rating=5)

    book3 = Book(id=UUID("c2b2f7c3-2f3b-4b3a-8e7c-1a6b9c9d0b6c"),
                 title="Life, the Universe and Everything",
                 author="Douglas Adams",
                 description="Life, the Universe and Everything is a science fiction comedy novel by Douglas Adams.",
                 rating=5)

    book4 = Book(id=UUID("c2b2f7c3-2f3b-4b3a-8e7c-1a6b9c9d0b6d"),
                 title="So Long, and Thanks for All the Fish",
                 author="Douglas Adams",
                 description="So Long, and Thanks for All the Fish is a science fiction comedy novel by Douglas Adams.",
                 rating=5)

    BOOKS.append(book1)
    BOOKS.append(book2)
    BOOKS.append(book3)
    BOOKS.append(book4)


def raise_item_not_found_exception():
    return HTTPException(status_code=404, detail="Item not found", headers={"X-Error": "Cannot find item with that ID"})
