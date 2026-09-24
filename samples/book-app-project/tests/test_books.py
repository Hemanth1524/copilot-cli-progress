import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import Book, BookCollection, get_book_statistics


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


def test_get_book_statistics():
    books_list = [
        Book("New Book", "Author Two", 2020, read=True),
        Book("Old Book", "Author One", 1950),
        Book("Middle Book", "Author Three", 2000),
    ]

    result = get_book_statistics(books_list)

    assert result["total_count"] == 3
    assert result["read_count"] == 1
    assert result["unread_count"] == 2
    assert result["oldest_book"] == books_list[1]
    assert result["newest_book"] == books_list[0]


def test_get_book_statistics_empty_list():
    result = get_book_statistics([])

    assert result == {
        "total_count": 0,
        "read_count": 0,
        "unread_count": 0,
        "oldest_book": None,
        "newest_book": None,
    }


def test_load_books_skips_malformed_records():
    with open(books.DATA_FILE, "w", encoding="utf-8") as data_file:
        data_file.write(
            '[{"title": "Valid", "author": "Author", "year": 2024},'
            '{"title": "Missing year", "author": "Author"}]'
        )

    collection = BookCollection()

    assert collection.list_books() == [Book("Valid", "Author", 2024)]


def test_load_books_handles_non_array_json(capsys):
    with open(books.DATA_FILE, "w", encoding="utf-8") as data_file:
        data_file.write('{"title": "Not a list"}')

    collection = BookCollection()

    assert collection.list_books() == []
    assert "must contain a JSON array" in capsys.readouterr().out


def test_load_books_reports_permission_errors(monkeypatch, capsys):
    def raise_permission_error(*args, **kwargs):
        raise PermissionError("read-only file")

    monkeypatch.setattr("builtins.open", raise_permission_error)

    collection = BookCollection()

    assert collection.list_books() == []
    assert "permission denied while reading" in capsys.readouterr().out


def test_save_books_reports_permission_errors(monkeypatch):
    collection = BookCollection()

    def raise_permission_error(*args, **kwargs):
        raise PermissionError("read-only file")

    monkeypatch.setattr("builtins.open", raise_permission_error)

    with pytest.raises(PermissionError, match="Permission denied while writing"):
        collection.save_books()
