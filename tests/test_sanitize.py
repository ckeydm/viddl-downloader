from viddl.utils.sanitize import sanitize_filename


def test_basic():
    assert sanitize_filename('Hello: World?') == "Hello_ World_"


def test_illegal_chars():
    assert "/" not in sanitize_filename("a/b\\c:d*e?f\"g<h>i|j")
    assert "<" not in sanitize_filename("a<b")


def test_empty():
    assert sanitize_filename("") == "untitled"


def test_reserved():
    assert sanitize_filename("CON").startswith("_")
    assert sanitize_filename("con").startswith("_")


def test_trailing_dots():
    assert sanitize_filename("name...") == "name"


def test_length():
    long = "a" * 500
    out = sanitize_filename(long)
    assert len(out) <= 180