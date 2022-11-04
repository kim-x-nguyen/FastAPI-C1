from fastapi import FastAPI
from enum import Enum

app = FastAPI()

BOOKS = {
    1: {
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'year': 1997
    },
    2: {
        'title': 'Harry Potter and the Chamber of Secrets',
        'author': 'J. K. Rowling',
        'year': 1998
    },
    3: {
        'title': 'Harry Potter and the Prisoner of Azkaban',
        'author': 'J. K. Rowling',
        'year': 1999
    },
    4: {
        'title': 'Harry Potter and the Goblet of Fire',
        'author': 'J. K. Rowling',
        'year': 2000
    },
}

class DirectionName(str, Enum):
    north = 'north'
    south = 'south'
    east = 'east'
    west = 'west'

@app.get("/")
async def get_all_books():
    return BOOKS

@app.get("/books")
async def get_book(book_id: int):
    return BOOKS[book_id]

@app.get("/direction/{direction}")
async def get_direction(direction: DirectionName):
    if direction == DirectionName.north:
        return {"direction": "You are heading north"}
    elif direction == DirectionName.south:
        return {"direction": "You are heading south"}
    elif direction == DirectionName.east:
        return {"direction": "You are heading east"}
    elif direction == DirectionName.west:
        return {"direction": "You are heading west"}
    else:
        return {"direction": "You are lost"}


@app.get("/books/{book_name}")
async def get_book_by_name(book_name: str):
    for book_id in BOOKS:
        if BOOKS[book_id]['title'] == book_name:
            return BOOKS[book_id]
    return None

@app.post("/books")
async def create_book(book_title: str, book_author: str, book_year: int):
    book_id = max(BOOKS.keys()) + 1
    BOOKS[book_id] = {
        'title': book_title,
        'author': book_author,
        'year': book_year
    }
    return BOOKS[book_id]

@app.put("/books/{book_id}")
async def update_book(book_id: int, book_title: str, book_author: str, book_year: int):
    BOOKS[book_id] = {
        'title': book_title,
        'author': book_author,
        'year': book_year
    }
    return BOOKS[book_id]

@app.delete("/books")
async def delete_book(book_id: int):
    if book_id in BOOKS:
        del BOOKS[book_id]
        return True
    return False