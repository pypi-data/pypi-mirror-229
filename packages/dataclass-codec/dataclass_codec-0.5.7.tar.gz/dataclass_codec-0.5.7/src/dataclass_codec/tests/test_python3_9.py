import sys


from dataclasses import dataclass

from dataclass_codec import decode, encode

if sys.version_info >= (3, 9):

    def test_dataclass() -> None:
        @dataclass
        class Foo:
            a: int
            b: int

        assert decode({"a": 1, "b": 2}, Foo) == Foo(1, 2)
        assert encode(Foo(1, 2)) == {"a": 1, "b": 2}

    def test_python_39_dict() -> None:
        assert decode({"a": 1, "b": 2}, dict[str, int]) == {"a": 1, "b": 2}
        assert encode({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_python_39_list() -> None:
        assert decode([1, 2, 3], list[int]) == [1, 2, 3]
        assert encode([1, 2, 3]) == [1, 2, 3]

    def test_python_39_tuple() -> None:
        assert decode((1, 2, 3), tuple[int, int, int]) == (1, 2, 3)
        assert encode((1, 2, 3)) == [1, 2, 3]
