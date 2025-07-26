import enum
from fastapi import FastAPI, Query

from typing import Optional

from enum import Enum

app = FastAPI()

class SortingEnum(str, Enum):
    desc = "desc"
    asc  = "asc"

@app.get("/books/{book_id}")
async def get_books(book_id: int, sorting: Optional[SortingEnum] = None):
    return {
        "Book ID: ": book_id,
        "sorting": sorting
    }

@app.get("/books/{book_id}/year")
async def get_books_year(book_id: int, year: Optional[int] = None):
    return {
        "Book ID: " : book_id,
        "books": ["Book 01", "Book 02"] if year else ["All Books"],
    }