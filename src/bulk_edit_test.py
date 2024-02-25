from dataclasses import dataclass
from typing import List, Optional

from src.bulk_edit import validate_and_parse_ranges
from src.sheet import Range


@dataclass
class TestCase:
    query: str
    expected: Optional[List[Range]]
    error: Optional[str]


testcases = [
    TestCase(
        query="0",
        expected=[Range(start=0, end=1)],
        error=None,
    ),
    TestCase(
        query="0:2",
        expected=[Range(start=0, end=2)],
        error=None,
    ),
    TestCase(
        query="-1:0",
        expected=None,
        error="Pattern '-1:0' does not match a valid index or range.",
    ),
    TestCase(
        query="0:-1",
        expected=None,
        error="Pattern '0:-1' does not match a valid index or range.",
    ),
    TestCase(
        query="a:0",
        expected=None,
        error="Pattern 'a:0' does not match a valid index or range.",
    ),
    TestCase(
        query="0:a",
        expected=None,
        error="Pattern '0:a' does not match a valid index or range.",
    ),
    TestCase(
        query="",
        expected=[Range(None, None)],
        error=None,
    ),
    TestCase(
        query=":5",
        expected=[Range(None, 5)],
        error=None,
    ),
    TestCase(
        query="5:",
        expected=[Range(5, None)],
        error=None,
    ),
    TestCase(
        query="0,2",
        expected=[Range(0, 1), Range(2, 3)],
        error=None,
    ),
    TestCase(
        query=" :10",
        expected=[Range(None, 10)],
        error=None,
    ),
    TestCase(
        query=":10 ",
        expected=[Range(None, 10)],
        error=None,
    ),
    TestCase(
        query=":5,,",
        expected=[Range(None, 5)],
        error=None,
    ),
    TestCase(
        query=":2,4:6,8:",
        expected=[Range(None, 2), Range(4, 6), Range(8, None)],
        error=None,
    ),
]

for testcase in testcases:
    print(f"Query {testcase.query}")
    success = True
    try:
        result = validate_and_parse_ranges(testcase.query)
        if testcase.expected is None:
            success = False
            print(f"FAIL: expected error not result; got '{result}'")
        elif result != testcase.expected:
            success = False
            print(f"FAIL: result '{result}' does not equal expected '{testcase.expected}'")
    except Exception as e:
        if testcase.error is None:
            success = False
            print(f"FAIL: did not except any error; got '{str(e)}'")
        elif str(e) != testcase.error:
            success = False
            print(f"FAIL: error '{str(e)}' does not equal expected error '{testcase.error}'")
    if success:
        print("SUCCESS")
