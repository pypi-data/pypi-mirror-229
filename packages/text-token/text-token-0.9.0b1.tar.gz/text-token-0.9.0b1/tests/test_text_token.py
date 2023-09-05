import pytest
from text_token import register_token_code, text_token, token_library


def test_register_token_valid() -> None:
    """Test that a valid token can be registered."""
    register_token_code("E00000", "A test token")
    assert "E00000" in token_library


def test_register_token_invalid_prefix() -> None:
    """Test that an invalid token prefix cannot be registered."""
    with pytest.raises(ValueError):
        register_token_code("N00000", "A test token")


def test_register_token_invalid_length() -> None:
    """Test that an invalid token length cannot be registered."""
    with pytest.raises(ValueError):
        register_token_code("E0000", "A test token")


def test_register_token_invalid_number() -> None:
    """Test that an invalid token number cannot be registered."""
    with pytest.raises(ValueError):
        register_token_code("E-2354", "A test token")


def test_register_token_in_use() -> None:
    """Test that a token cannot be registered twice."""
    register_token_code("E00001", "A test token")
    with pytest.raises(ValueError):
        register_token_code("E00001", "A test token")


def test_text_token() -> None:
    """Test that a text_token can be created."""
    register_token_code("E00002", "A test token {test}")
    token: text_token = text_token({"E00002": {"test": "test value"}})
    assert token.code == "E00002"
    assert token.parameters == {"test": "test value"}
    assert str(token) == "E00002: A test token test value"
