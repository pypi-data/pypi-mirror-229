import pytest
import sys


from dataclass_codec import decode, encode

if sys.version_info >= (3, 10):

    def test_python_310_union() -> None:
        assert decode(1, int | str) == 1
        assert decode("a", int | str) == "a"
        assert encode(1) == 1
        assert encode("a") == "a"

        # Test nullable
        assert decode(None, int | None) is None
        assert decode(None, int | str | None) is None

        with pytest.raises(TypeError):
            decode(None, int | str)

        decode(1, int | bool | bytes)
