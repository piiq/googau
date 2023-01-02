"""Test the sheets module."""

import pytest

# pylint: disable=import-outside-toplevel


@pytest.mark.parametrize(
    "sheets_class",
    [
        "WorkSheetObject",
        "SpreadSheetObject",
    ],
)
def test_import_sheets_module(sheets_class):
    """Test that the sheets module can be imported."""
    import googau.sheets as gs

    assert hasattr(gs, sheets_class)  # nosec
