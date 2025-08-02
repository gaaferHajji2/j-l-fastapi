import enum
from fastapi import FastAPI, Query

from typing import Optional

from enum import Enum

from schemas.book import Book, AdvancedBook

app = FastAPI()


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
