import re
import traceback
from .classification_exceptions import SelectionOutOfRange, ReversedRange, UnbalancedPageRange, NotZeroIndex


"""
Functionality for parsing the page ranges for 'MULTIPLE' document classification scenarios.

Who knows what the annotators will enter, so we account for all of the basic scenarios via RegEx.
"""


def parse_page_range(page_range: str, max_pages: int):
    """
    Parses the page range coming from the annotator for a multi-classification segment.
    """
    func = parse_page_range.__name__
    try:
        page_range = re.sub(" ", "", page_range)
        print(f"[{func}] input={page_range}")
        if bool(re.compile(r"(\d+|\d)-(\d+|\d)((,(\d+|\d))+)").search(page_range)):
            """
            Example: input = '1-5, 8, 9, 11'
            """
            res = re.compile(r"(\d+|\d)-(\d+|\d)((,(\d+|\d))+)").search(page_range)
            if res is not None:
                print(f"[{func}] option 1 matched")
                start = int(res.group(1))
                end = int(res.group(2))
                others_ = res.group(3)
                others = others_.split(",")
                others = [int(i) for i in others if bool(re.compile(r"\d+|\d").search(i))]
                print(f"start={start}; end={end}; others={others}")

                nums = others.copy()
                nums.extend([start, end])
                highest = max(nums)
                if highest > max_pages:
                    raise SelectionOutOfRange(
                        f"The page range selection exceeds the maximum number of pages; {highest} > {max_pages}")

                if start > end:
                    raise ReversedRange(f"Out of order; {start} is bigger than {end}")

                if start < max(others) <= end:
                    raise UnbalancedPageRange(f"The largest comma-separated-value {max(others)} is included in the range {start}-{end}")

                for num in others:
                    if start < num <= end:
                        raise UnbalancedPageRange(f"Comma-separated-value {num} is included in the range {start}-{end}")

                if start == 0 or 0 in others:
                    raise NotZeroIndex("Page ranges and indexes do not include '0'")

                return True, {
                    'range_start': start,
                    'range_end': end,
                    'singles': sorted(others)
                }, ""

        elif bool(re.compile(r"(((\d+|\d),)+)(\d+|\d)-(\d+|\d)").search(page_range)):
            """
            Example: input = '1, 2, 4-7'
            """
            res = re.compile(r"(((\d+|\d),)+)(\d+|\d)-(\d+|\d)").search(page_range)
            if res is not None:
                print(f"[{func}] option 2 matched")
                start = int(res.group(4))
                end = int(res.group(5))
                others_ = res.group(1)
                others = others_.split(",")
                others = [int(i) for i in others if bool(re.compile(r"\d+|\d").search(i))]
                print(f"start={start}; end={end}; others={others}")

                nums = others.copy()
                nums.extend([start, end])
                highest = max(nums)
                if highest > max_pages:
                    raise SelectionOutOfRange(
                        f"The page range selection exceeds the maximum number of pages; {highest} > {max_pages}")

                if start > end:
                    raise ReversedRange(f"Out of order; {start} is bigger than {end}")

                if start < max(others) <= end:
                    raise UnbalancedPageRange(f"The largest comma-separated-value {max(others)} is included in the range {start}-{end}")

                for num in others:
                    if start < num <= end:
                        raise UnbalancedPageRange(f"Comma-separated-value {num} is included in the range {start}-{end}")

                if start == 0 or 0 in others:
                    raise NotZeroIndex("Page ranges and indexes do not include '0'")

                return True, {
                    'range_start': start,
                    'range_end': end,
                    'singles': sorted(others)
                }, ""

        elif bool(re.compile(r"(\d+|\d)-(\d+|\d)").search(page_range)):
            """
            Example: input = '1-3'
            """
            res = re.compile(r"(\d+|\d)-(\d+|\d)").search(page_range)
            if res is not None:
                print(f"[{func}] option 3 matched")
                start = int(res.group(1))
                end = int(res.group(2))
                print(f"start={start}; end={end}")

                if start > end:
                    raise ReversedRange(f"Out of order; {start} is bigger than {end}")

                if end > max_pages:
                    raise SelectionOutOfRange(
                        f"The page range selection exceeds the maximum number of pages; {end} > {max_pages}")

                if start == 0:
                    raise NotZeroIndex("Page ranges and indexes do not include '0'")

                if start == end:
                    print(f"{start} == {end}")
                    return 200, {
                        'range_start': None,
                        'range_end': None,
                        'singles': [start],
                        'error': None
                    }

                return True, {
                    'range_start': start,
                    'range_end': end,
                    'singles': []
                }, ""

        elif bool(re.compile(r"(((\d+|\d),?)+)").search(page_range)):
            """
            Example: input = '1, 2, 3'
            """
            res = re.compile(r"(((\d+|\d),?)+)").search(page_range)
            if res is not None:
                print(f"[{func}] option 4 matched")
                others_ = res.group(1)
                others = others_.split(",")
                others = [int(i) for i in others if bool(re.compile(r"\d+|\d").search(i))]
                print(f"others={others}")

                highest = max(others)
                if highest > max_pages:
                    raise SelectionOutOfRange(
                        f"The page range selection exceeds the maximum number of pages; {highest} > {max_pages}")

                if 0 in others:
                    raise NotZeroIndex("Page ranges and indexes do not include '0'")

                return True, {
                    'range_start': None,
                    'range_end': None,
                    'singles': sorted(others)
                }, ""

        elif bool(re.compile(r"(\d+|\d)").search(page_range)):
            res = re.compile(r"(\d+|\d)").search(page_range)
            if res is not None:
                print(f"[{func}] option 5 matched")
                start = int(res.group(1))
                print(f"single start={start}")

                if start > max_pages:
                    raise SelectionOutOfRange(
                        f"The page range selection exceeds the maximum number of pages; {start} > {max_pages}")

                if start == 0:
                    raise NotZeroIndex("Page ranges and indexes do not include '0'")

                return True, {
                    'range_start': None,
                    'range_end': None,
                    'singles': [start]
                }, ""

    except UnbalancedPageRange as ub:
        print(f"[INPUT ERROR] UnbalancedPageRange ==> {ub}")
        return False, {
            'range_start': None,
            'range_end': None,
            'singles': []
        }, f"UnbalancedPageRange ==> {ub}"
    except SelectionOutOfRange as sor:
        print(f"[INPUT ERROR] SelectionOutOfRange ==> {sor}")
        return False, {
            'range_start': None,
            'range_end': None,
            'singles': []
        }, f"SelectionOutOfRange ==> {sor}"
    except ReversedRange as rr:
        print(f"[INPUT ERROR] ReversedRange ==> {rr}")
        return False, {
            'range_start': None,
            'range_end': None,
            'singles': []
        }, f"ReversedRange ==> {rr}"
    except NotZeroIndex as nzi:
        print(f"[INPUT ERROR] NotZeroIndex ==> {nzi}")
        return False, {
            'range_start': None,
            'range_end': None,
            'singles': []
        }, f"NotZeroIndex ==> {nzi}"
    except Exception as e:
        print(f"[ERROR] {func} Error ==> {e}")
        traceback.print_exc()
        return False, {
            'range_start': None,
            'range_end': None,
            'singles': []
        }, f"{e}"
