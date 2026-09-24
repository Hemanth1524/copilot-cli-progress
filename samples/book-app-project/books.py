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

    def load_books(self) -> None:
        """Load valid books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.books = []
            return
        except PermissionError:
            print(f"Error: permission denied while reading {DATA_FILE}.")
            self.books = []
            return
        except json.JSONDecodeError:
            print(f"Warning: {DATA_FILE} contains invalid JSON. Starting empty.")
            self.books = []
            return
        except OSError as error:
            print(f"Error: could not read {DATA_FILE}: {error}")
            self.books = []
            return

        if not isinstance(data, list):
            print(f"Warning: {DATA_FILE} must contain a JSON array. Starting empty.")
            self.books = []
            return

        valid_books = []
        for index, item in enumerate(data):
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("title"), str)
                or not isinstance(item.get("author"), str)
                or not isinstance(item.get("year"), int)
                or isinstance(item.get("year"), bool)
                or (
                    "read" in item
                    and not isinstance(item.get("read"), bool)
                )
            ):
                print(f"Warning: skipping malformed book at index {index}.")
                continue

            valid_books.append(
                Book(
                    title=item["title"],
                    author=item["author"],
                    year=item["year"],
                    read=item.get("read", False),
                )
            )

        self.books = valid_books

    def save_books(self) -> None:
        """Save the current book collection to JSON."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([asdict(b) for b in self.books], f, indent=2)
        except PermissionError as error:
            raise PermissionError(
                f"Permission denied while writing {DATA_FILE}."
            ) from error
        except OSError as error:
            raise OSError(f"Could not write {DATA_FILE}: {error}") from error

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
