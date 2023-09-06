"""
Custom Exceptions for custom problems.

Helps to isolate some specific issues and customize the way they are handled, rather than leaning on the standard
Exception type or ValueError.

Works the same way that a typical Exception would.
"""


class SelectionOutOfRange(Exception):
    """
    Raised if a page selection is passed in that exceeds the maximum number of pages in the PDF.

    e.i. input = "1-7" but the total pages in the PDF is 5.
    """
    pass


class ReversedRange(Exception):
    """
    Raised in the event that a simple range is passed in where the start is bigger than the end.

    i.e. input = "10-5"

    Page range numbers must be in order from smallest >> largest.
    """
    pass


class UnbalancedPageRange(Exception):
    """
    Raised if the page range (start-end) where 'end' is a number that is higher
    than the numbers that follow it separated by a comma.

    i.e. input = "3-7, 4, 5"

    The numbers that follow are already covered by the preceding range.
    """
    pass


class NotZeroIndex(Exception):
    """
    Raised in the event that an annotator passes in a page range that includes "0" as a page number.
    Document page ranges coming from the DT are not a zero-index.
    """
    pass
