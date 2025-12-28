"""Pytest fixtures for Kanvas test suite."""

import pytest

from kanvas.model import Model


@pytest.fixture
def model() -> Model:
    """Create a small Model instance for testing.
    
    Returns:
        A Model instance with 100x100 pixel dimensions.
    """
    return Model(100, 100)


@pytest.fixture
def small_model() -> Model:
    """Create a very small Model instance for detailed pixel testing.
    
    Returns:
        A Model instance with 10x10 pixel dimensions.
    """
    return Model(10, 10)