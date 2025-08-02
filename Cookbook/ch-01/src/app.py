import enum
from fastapi import FastAPI, Query, Request

from typing import Optional

from enum import Enum

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from schemas.book import Book, AdvancedBook

app = FastAPI()

map_errors = {
    'String should have at least 2 characters': 'Title must be at least 2-chars',
    'String should have at least 5 characters': 'Author must be at least 5-chars',
    'Input should be greater than or equal to 2000': 'Year must be between 2000 && 20000'
}


class SortingEnum(str, Enum):
    desc = "desc"
    asc = "asc"


@app.get("/books/{book_id}")
async def get_books(book_id: int, sorting: Optional[SortingEnum] = None):
    return {"id: ": book_id, "sorting": sorting}


@app.get("/books/{book_id}/year")
async def get_books_year(book_id: int, year: Optional[int] = None):
    return {
        "id: ": book_id,
        "books": ["Book 01", "Book 02"] if year else ["All Books"],
    }


@app.post("/books", response_model=Book)
async def create_book(book: Book):
    return {
        "title": book.title,
        "author": book.author,
        "year": "Nothing" if book.year == None else book.year,
    }


@app.post("/adv/books", response_model=Book)
async def create_advanced_book(book: AdvancedBook):
    return {
        "title": book.title,
        "author": book.author,
        "year": "Nothing" if book.year == None else book.year,
    }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, err: RequestValidationError):
    errors = []

    for error in err.errors():

        print(f"error is: {err.__dict__}")

        errors.append({
            "field": error["loc"][-1] if error["loc"] else "unknown",
            "message": map_errors.get(error["msg"], ''),
            "desc": error.get("description", ''),
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content=errors
    )