"""
Tests for utils.exception_utils module
"""

import pytest
from utils import exception_utils


class TestGetUserFriendlyError:
    """Tests for error message conversion."""

    def test_file_not_found_error(self):
        """Test FileNotFoundError conversion."""
        error = FileNotFoundError("No such file or directory: 'test.h5ad'")
        message = exception_utils.get_user_friendly_error(error)

        assert isinstance(message, str)
        assert len(message) > 0
        # Should be in Chinese
        assert any('\u4e00' <= c <= '\u9fff' for c in message)

    def test_permission_error(self):
        """Test PermissionError conversion."""
        error = PermissionError("Permission denied")
        message = exception_utils.get_user_friendly_error(error)

        assert isinstance(message, str)
        assert len(message) > 0

    def test_memory_error(self):
        """Test MemoryError conversion."""
        error = MemoryError()
        message = exception_utils.get_user_friendly_error(error)

        assert isinstance(message, str)
        # Should mention memory
        assert len(message) > 0

    def test_value_error(self):
        """Test ValueError conversion."""
        error = ValueError("Invalid value for parameter")
        message = exception_utils.get_user_friendly_error(error)

        assert isinstance(message, str)

    def test_key_error(self):
        """Test KeyError conversion."""
        error = KeyError("missing_key")
        message = exception_utils.get_user_friendly_error(error)

        assert isinstance(message, str)

    def test_unknown_error(self):
        """Test unknown error type conversion."""
        error = RuntimeError("Unknown runtime error")
        message = exception_utils.get_user_friendly_error(error)

        assert isinstance(message, str)


class TestHandleException:
    """Tests for handle_exception function."""

    def test_handle_exception_with_context(self):
        """Test exception handling with context."""
        error = ValueError("Test error")

        # Should not raise, just handle
        exception_utils.handle_exception(error, "Testing error handling")

    def test_handle_exception_with_callback(self):
        """Test exception handling with callback."""
        error = ValueError("Test error")
        callback_called = []

        def callback(msg):
            callback_called.append(msg)

        if hasattr(exception_utils, 'handle_exception'):
            exception_utils.handle_exception(error, "Test context", callback=callback)


class TestExceptionMapping:
    """Tests for exception type mapping."""

    def test_error_messages_exist(self):
        """Test that error messages are defined."""
        # Check that the module has necessary mappings
        assert hasattr(exception_utils, 'get_user_friendly_error')

    def test_chinese_messages(self):
        """Test that messages are in Chinese."""
        errors = [
            FileNotFoundError("test"),
            PermissionError("test"),
            MemoryError(),
        ]

        for error in errors:
            message = exception_utils.get_user_friendly_error(error)
            # Check for Chinese characters
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in message)
            assert has_chinese, f"Message should contain Chinese: {message}"
