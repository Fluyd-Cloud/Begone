import pytest

from begone.ranges import PatternSet, range_to_pattern, sanitize


@pytest.mark.parametrize(
    ("start", "end", "pattern"),
    [
        ("0187680000", "0187689999", "+3318768####"),
        ("0939080000", "0939080999", "+33939080###"),
        ("0187686887", "0187686887", "+33187686887"),
        ("0100000000", "0199999999", "+331########"),
        ("3115", "3115", "3115"),
    ],
)
def test_range_to_pattern(start: str, end: str, pattern: str) -> None:
    assert range_to_pattern(start, end) == pattern


def test_sanitize() -> None:
    assert sanitize("+33 1 62 ## ## ##") == "+33162######"
    assert sanitize("01.87.68-68 87") == "0187686887"


def test_pattern_set_covers_sub_patterns() -> None:
    patterns = PatternSet()
    patterns.add("+33162######")

    assert patterns.covers("+33162######")
    assert patterns.covers("+331620#####")
    assert patterns.covers("+33162123456")
    assert not patterns.covers("+3316#######")
    assert not patterns.covers("+33163######")
    # Same prefix, different number length.
    assert not patterns.covers("+33162#####")
