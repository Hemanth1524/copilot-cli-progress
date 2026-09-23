import json
from dataclasses import dataclass, asdict
from typing import List, Optional, TypedDict

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


class BookStatistics(TypedDict):
    total_count: int
    read_count: int
    unread_count: int
    oldest_book: Optional[Book]
    newest_book: Optional[Book]


def get_book_statistics(books: List[Book]) -> BookStatistics:
    """Return reading and publication-year statistics for a list of books."""
    read_count = sum(book.read for book in books)
    oldest_book = min(books, key=lambda book: book.year, default=None)
    newest_book = max(books, key=lambda book: book.year, default=None)

    return {
        "total_count": len(books),
        "read_count": read_count,
        "unread_count": len(books) - read_count,
        "oldest_book": oldest_book,
        "newest_book": newest_book,
    }


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []

    def save_books(self):
        """Save the current book collection to JSON."""
        with open(DATA_FILE, "w") as f:
            json.dump([asdict(b) for b in self.books], f, indent=2)

    def add_book(self, title: str, author: str, year: int) -> Book:
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author."""
        return [b for b in self.books if b.author.lower() == author.lower()]
