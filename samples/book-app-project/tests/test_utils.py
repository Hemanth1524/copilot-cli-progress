import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_book_details


def test_get_book_details_rejects_empty_title(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "   ")

    with pytest.raises(ValueError, match="Book title cannot be empty"):
        get_book_details()
