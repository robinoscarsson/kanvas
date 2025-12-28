"""Tests for noise generation functions."""

import numpy as np
import pytest

from kanvas.model import noise, p_noise, noise_array, p_noise_array


class TestValueNoise:
    """Tests for the value noise function."""

    def test_noise_range(self) -> None:
        """Verify noise output is in [0, 1] range."""
        # Test many points to ensure range is respected
        for x in range(-10, 10):
            for y in range(-10, 10):
                value = noise(x * 0.1, y * 0.1)
                assert 0.0 <= value <= 1.0, f"noise({x * 0.1}, {y * 0.1}) = {value} out of range"

    def test_noise_deterministic(self) -> None:
        """Verify same seed produces same output."""
        seed = 42
        x, y = 1.5, 2.5
        
        value1 = noise(x, y, seed=seed)
        value2 = noise(x, y, seed=seed)
        
        assert value1 == value2, "Same inputs with same seed should produce identical output"

    def test_noise_different_seeds(self) -> None:
        """Verify different seeds produce different output."""
        x, y = 1.5, 2.5
        
        value1 = noise(x, y, seed=42)
        value2 = noise(x, y, seed=123)
        
        assert value1 != value2, "Different seeds should produce different output"

    def test_noise_continuity(self) -> None:
        """Verify noise is continuous (nearby points have similar values)."""
        x, y = 5.0, 5.0
        base_value = noise(x, y)
        
        # Small step should produce similar value
        nearby_value = noise(x + 0.01, y + 0.01)
        
        # The difference should be small for continuous noise
        assert abs(base_value - nearby_value) < 0.1, "Noise should be continuous"


class TestPerlinNoise:
    """Tests for the Perlin gradient noise function."""

    def test_p_noise_range(self) -> None:
        """Verify Perlin noise output is in [0, 1] range (after mapping from [-1, 1])."""
        # Test many points to ensure range is respected
        for x in range(-10, 10):
            for y in range(-10, 10):
                value = p_noise(x * 0.1, y * 0.1)
                assert 0.0 <= value <= 1.0, f"p_noise({x * 0.1}, {y * 0.1}) = {value} out of range"

    def test_p_noise_deterministic(self) -> None:
        """Verify same seed produces same output."""
        seed = 42
        x, y = 1.5, 2.5
        
        value1 = p_noise(x, y, seed=seed)
        value2 = p_noise(x, y, seed=seed)
        
        assert value1 == value2, "Same inputs with same seed should produce identical output"

    def test_p_noise_different_seeds(self) -> None:
        """Verify different seeds produce different output."""
        x, y = 1.5, 2.5
        
        value1 = p_noise(x, y, seed=42)
        value2 = p_noise(x, y, seed=123)
        
        assert value1 != value2, "Different seeds should produce different output"

    def test_p_noise_continuity(self) -> None:
        """Verify Perlin noise is continuous."""
        x, y = 5.0, 5.0
        base_value = p_noise(x, y)
        
        nearby_value = p_noise(x + 0.01, y + 0.01)
        
        assert abs(base_value - nearby_value) < 0.1, "Perlin noise should be continuous"


class TestNoiseArray:
    """Tests for vectorized noise array functions."""

    def test_noise_array_shape(self) -> None:
        """Verify noise_array returns correct shape."""
        x = np.arange(10).reshape(2, 5).astype(float)
        y = np.arange(10).reshape(2, 5).astype(float)
        
        result = noise_array(x, y)
        
        assert result.shape == (2, 5), f"Expected shape (2, 5), got {result.shape}"

    def test_noise_array_matches_scalar(self) -> None:
        """Verify noise_array matches scalar noise calls."""
        seed = 42
        x_vals = np.array([0.5, 1.5, 2.5])
        y_vals = np.array([0.5, 1.5, 2.5])
        
        array_result = noise_array(x_vals, y_vals, seed=seed)
        
        for i in range(len(x_vals)):
            scalar_result = noise(x_vals[i], y_vals[i], seed=seed)
            assert np.isclose(array_result[i], scalar_result, rtol=1e-10), \
                f"Array result {array_result[i]} != scalar result {scalar_result} at index {i}"

    def test_noise_array_range(self) -> None:
        """Verify noise_array output is in [0, 1] range."""
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        
        result = noise_array(x, y)
        
        assert np.all(result >= 0.0), "All values should be >= 0"
        assert np.all(result <= 1.0), "All values should be <= 1"

    def test_noise_array_2d_grid(self) -> None:
        """Verify noise_array works with 2D meshgrid."""
        x_coords, y_coords = np.meshgrid(
            np.arange(10) * 0.1,
            np.arange(10) * 0.1,
            indexing='ij'
        )
        
        result = noise_array(x_coords, y_coords)
        
        assert result.shape == (10, 10)
        assert np.all(result >= 0.0)
        assert np.all(result <= 1.0)


class TestPNoiseArray:
    """Tests for vectorized Perlin noise array functions."""

    def test_p_noise_array_shape(self) -> None:
        """Verify p_noise_array returns correct shape."""
        x = np.arange(10).reshape(2, 5).astype(float)
        y = np.arange(10).reshape(2, 5).astype(float)
        
        result = p_noise_array(x, y)
        
        assert result.shape == (2, 5), f"Expected shape (2, 5), got {result.shape}"

    def test_p_noise_array_matches_scalar(self) -> None:
        """Verify p_noise_array matches scalar p_noise calls."""
        seed = 42
        x_vals = np.array([0.5, 1.5, 2.5])
        y_vals = np.array([0.5, 1.5, 2.5])
        
        array_result = p_noise_array(x_vals, y_vals, seed=seed)
        
        for i in range(len(x_vals)):
            scalar_result = p_noise(x_vals[i], y_vals[i], seed=seed)
            assert np.isclose(array_result[i], scalar_result, rtol=1e-10), \
                f"Array result {array_result[i]} != scalar result {scalar_result} at index {i}"

    def test_p_noise_array_range(self) -> None:
        """Verify p_noise_array output is in [0, 1] range."""
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        
        result = p_noise_array(x, y)
        
        assert np.all(result >= 0.0), "All values should be >= 0"
        assert np.all(result <= 1.0), "All values should be <= 1"

    def test_p_noise_array_2d_grid(self) -> None:
        """Verify p_noise_array works with 2D meshgrid."""
        x_coords, y_coords = np.meshgrid(
            np.arange(10) * 0.1,
            np.arange(10) * 0.1,
            indexing='ij'
        )
        
        result = p_noise_array(x_coords, y_coords)
        
        assert result.shape == (10, 10)
        assert np.all(result >= 0.0)
        assert np.all(result <= 1.0)


class TestNoiseCaching:
    """Tests for noise table caching behavior."""

    def test_noise_cache_consistency(self) -> None:
        """Verify cached noise tables produce consistent results."""
        seed = 42
        
        # First call creates cache
        value1 = noise(1.0, 1.0, seed=seed)
        
        # Second call should use cache
        value2 = noise(1.0, 1.0, seed=seed)
        
        # Third call at different coordinates
        value3 = noise(2.0, 2.0, seed=seed)
        
        assert value1 == value2, "Cached results should be identical"
        assert value1 != value3, "Different coordinates should give different results"

    def test_p_noise_cache_consistency(self) -> None:
        """Verify cached Perlin noise tables produce consistent results."""
        seed = 42
        
        # Use non-integer coordinates to avoid Perlin noise returning 0.5 at grid points
        value1 = p_noise(1.5, 1.5, seed=seed)
        value2 = p_noise(1.5, 1.5, seed=seed)
        value3 = p_noise(2.7, 3.3, seed=seed)
        
        assert value1 == value2, "Cached results should be identical"
        assert value1 != value3, "Different coordinates should give different results"