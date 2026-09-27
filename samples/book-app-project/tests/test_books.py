import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import book_app
import books
from books import Book, BookCollection, get_book_statistics, get_book_titles


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


@pytest.mark.parametrize(
    ("title", "author", "year", "message"),
    [
        ("   ", "Author", 2024, "Title cannot be empty"),
        ("Title", "   ", 2024, "Author cannot be empty"),
        ("Title", "Author", 0, "Year must be greater than zero"),
        ("Title", "Author", -1, "Year must be greater than zero"),
    ],
)
def test_add_book_rejects_invalid_inputs(title, author, year, message):
    collection = BookCollection()

    with pytest.raises(ValueError, match=message):
        collection.add_book(title, author, year)

    assert collection.list_books() == []


def test_add_book_does_not_update_collection_when_save_fails(monkeypatch):
    collection = BookCollection()

    def fail_to_save(books=None):
        raise OSError("disk full")

    monkeypatch.setattr(collection, "save_books", fail_to_save)

    with pytest.raises(OSError, match="disk full"):
        collection.add_book("1984", "George Orwell", 1949)

    assert collection.books == []


def test_list_books_returns_a_copy():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)

    listed_books = collection.list_books()
    listed_books.clear()

    assert len(collection.books) == 1


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


def test_get_book_titles():
    books_list = [
        {"title": "New Book", "author": "Author Two", "year": 2020},
        {"title": "Old Book", "author": "Author One", "year": 1950},
    ]

    assert get_book_titles(books_list) == ["New Book", "Old Book"]


def test_get_book_titles_skips_missing_titles():
    books_list = [{"author": "Author"}, {"title": "Titled Book"}]

    assert get_book_titles(books_list) == ["Titled Book"]


def test_get_book_titles_empty_list():
    assert get_book_titles([]) == []


def test_find_book_by_title_is_case_insensitive():
    collection = BookCollection()
    expected_book = Book("Dune", "Frank Herbert", 1965)
    collection.books.append(expected_book)

    assert collection.find_book_by_title("dUnE") is expected_book


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


def test_handle_add_rejects_empty_title(monkeypatch, capsys):
    responses = iter(["   ", "Jane Austen", "1813"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    book_app.handle_add()

    output = capsys.readouterr().out
    assert "Title cannot be empty" in output
    assert "Book added successfully" not in output


def test_handle_add_rejects_empty_author(monkeypatch, capsys):
    responses = iter(["Pride and Prejudice", "   ", "1813"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    book_app.handle_add()

    output = capsys.readouterr().out
    assert "Author cannot be empty" in output
    assert "Book added successfully" not in output


def test_handle_add_rejects_negative_year(monkeypatch, capsys):
    responses = iter(["Pride and Prejudice", "Jane Austen", "-1813"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    book_app.handle_add()

    output = capsys.readouterr().out
    assert "Year must be greater than zero" in output
    assert "Book added successfully" not in output


def test_handle_add_handles_save_errors(monkeypatch, capsys):
    responses = {
        "Title: ": "Pride and Prejudice",
        "Author: ": "Jane Austen",
        "Year: ": "1813",
    }
    monkeypatch.setattr("builtins.input", lambda prompt="": responses[prompt])
    monkeypatch.setattr(book_app.collection, "add_book", Mock(side_effect=PermissionError("disk full")))

    book_app.handle_add()

    output = capsys.readouterr().out
    assert "could not save the book" in output
    assert "disk full" in output


def test_handle_search_displays_matching_book(monkeypatch, capsys):
    collection = BookCollection()
    expected_book = Book("Dune", "Frank Herbert", 1965)
    collection.books.append(expected_book)
    monkeypatch.setattr(book_app, "collection", collection)
    monkeypatch.setattr("builtins.input", lambda prompt="": " dune ")

    book_app.main(["search"])

    output = capsys.readouterr().out
    assert "Dune by Frank Herbert (1965)" in output


def test_handle_search_reports_no_matching_book(monkeypatch, capsys):
    monkeypatch.setattr(book_app, "collection", BookCollection())
    monkeypatch.setattr("builtins.input", lambda prompt="": "Unknown title")

    book_app.main(["search"])

    assert "No books found." in capsys.readouterr().out


def test_handle_search_rejects_empty_title(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt="": "   ")

    book_app.main(["search"])

    output = capsys.readouterr().out
    assert "Title cannot be empty" in output
    assert "No books found." not in output


def test_search_command_is_in_help(capsys):
    book_app.main(["help"])

    assert "search   - Search for a book by title" in capsys.readouterr().out
