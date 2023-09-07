from kelvin.app.filters import is_data_message
from kelvin.sdk.datatype import make_message


def test_is_data_message():
    m = make_message("raw.float32", "metric1", value=1.0)
    assert is_data_message(m)
