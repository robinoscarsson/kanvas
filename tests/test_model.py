"""Tests for the Model class and drawing primitives."""

import numpy as np
import pytest

from kanvas.model import Model


class TestModelInitialization:
    """Tests for Model initialization."""

    def test_model_initialization(self, model: Model) -> None:
        """Verify Model initializes with correct width, height, and framebuffer shape."""
        assert model.w == 100
        assert model.h == 100
        assert model.fb.shape == (100, 100, 3)
        assert model.fb.dtype == np.uint8

    def test_model_initialization_custom_size(self) -> None:
        """Verify Model can be created with custom dimensions."""
        model = Model(200, 150)
        assert model.w == 200
        assert model.h == 150
        assert model.fb.shape == (200, 150, 3)

    def test_model_initialized_to_black(self, model: Model) -> None:
        """Verify Model framebuffer is initialized to black (0, 0, 0)."""
        assert np.all(model.fb == 0)


class TestModelClear:
    """Tests for Model.clear() method."""

    def test_model_clear_rgb(self, model: Model) -> None:
        """Verify clear with RGB values sets all pixels to that color."""
        model.clear(255, 128, 64)
        assert np.all(model.fb[:, :, 0] == 255)
        assert np.all(model.fb[:, :, 1] == 128)
        assert np.all(model.fb[:, :, 2] == 64)

    def test_model_clear_grayscale(self, model: Model) -> None:
        """Verify clear with single value sets all channels to that value."""
        model.clear(128)
        assert np.all(model.fb[:, :, 0] == 128)
        assert np.all(model.fb[:, :, 1] == 128)
        assert np.all(model.fb[:, :, 2] == 128)

    def test_model_clear_black(self, model: Model) -> None:
        """Verify clear with 0 sets all pixels to black."""
        # First set to non-black
        model.clear(255)
        # Then clear to black
        model.clear(0)
        assert np.all(model.fb == 0)


class TestModelPixel:
    """Tests for Model.pixel() method."""

    def test_pixel_in_bounds(self, small_model: Model) -> None:
        """Verify pixel sets correct value at valid coordinates."""
        small_model.pixel(5, 5, 255, 128, 64)
        assert tuple(small_model.fb[5, 5]) == (255, 128, 64)

    def test_pixel_out_of_bounds_negative(self, small_model: Model) -> None:
        """Verify out-of-bounds negative pixels are ignored."""
        small_model.pixel(-1, 5, 255, 0, 0)
        small_model.pixel(5, -1, 255, 0, 0)
        # Framebuffer should remain unchanged (all zeros)
        assert np.all(small_model.fb == 0)

    def test_pixel_out_of_bounds_positive(self, small_model: Model) -> None:
        """Verify out-of-bounds positive pixels are ignored."""
        small_model.pixel(10, 5, 255, 0, 0)  # x == width
        small_model.pixel(5, 10, 255, 0, 0)  # y == height
        small_model.pixel(100, 100, 255, 0, 0)  # way out of bounds
        # Framebuffer should remain unchanged (all zeros)
        assert np.all(small_model.fb == 0)

    def test_pixel_corner_cases(self, small_model: Model) -> None:
        """Verify pixels at corners are set correctly."""
        small_model.pixel(0, 0, 255, 0, 0)  # top-left
        small_model.pixel(9, 0, 0, 255, 0)  # top-right
        small_model.pixel(0, 9, 0, 0, 255)  # bottom-left
        small_model.pixel(9, 9, 255, 255, 0)  # bottom-right
        
        assert tuple(small_model.fb[0, 0]) == (255, 0, 0)
        assert tuple(small_model.fb[9, 0]) == (0, 255, 0)
        assert tuple(small_model.fb[0, 9]) == (0, 0, 255)
        assert tuple(small_model.fb[9, 9]) == (255, 255, 0)


class TestModelLine:
    """Tests for Model.line() method."""

    def test_line_horizontal(self, small_model: Model) -> None:
        """Verify horizontal line drawing."""
        small_model.line(2, 5, 7, 5, 255, 0, 0)
        # Check that pixels from x=2 to x=7 at y=5 are set
        for x in range(2, 8):
            assert tuple(small_model.fb[x, 5]) == (255, 0, 0), f"Pixel at ({x}, 5) not set"
        # Check that adjacent pixels are not set
        assert tuple(small_model.fb[1, 5]) == (0, 0, 0)
        assert tuple(small_model.fb[8, 5]) == (0, 0, 0)

    def test_line_vertical(self, small_model: Model) -> None:
        """Verify vertical line drawing."""
        small_model.line(5, 2, 5, 7, 0, 255, 0)
        # Check that pixels from y=2 to y=7 at x=5 are set
        for y in range(2, 8):
            assert tuple(small_model.fb[5, y]) == (0, 255, 0), f"Pixel at (5, {y}) not set"
        # Check that adjacent pixels are not set
        assert tuple(small_model.fb[5, 1]) == (0, 0, 0)
        assert tuple(small_model.fb[5, 8]) == (0, 0, 0)

    def test_line_diagonal(self, small_model: Model) -> None:
        """Verify diagonal line drawing using Bresenham's algorithm."""
        small_model.line(0, 0, 9, 9, 0, 0, 255)
        # For a 45-degree diagonal, all points along the diagonal should be set
        for i in range(10):
            assert tuple(small_model.fb[i, i]) == (0, 0, 255), f"Pixel at ({i}, {i}) not set"

    def test_line_diagonal_steep(self, small_model: Model) -> None:
        """Verify steep diagonal line drawing."""
        small_model.line(0, 0, 3, 9, 255, 255, 0)
        # Start and end points should be set
        assert tuple(small_model.fb[0, 0]) == (255, 255, 0)
        assert tuple(small_model.fb[3, 9]) == (255, 255, 0)

    def test_line_reversed_coordinates(self, small_model: Model) -> None:
        """Verify line drawing works with reversed coordinates."""
        small_model.line(7, 5, 2, 5, 255, 0, 0)  # horizontal reversed
        for x in range(2, 8):
            assert tuple(small_model.fb[x, 5]) == (255, 0, 0)

    def test_line_out_of_bounds_clipped(self, small_model: Model) -> None:
        """Verify lines extending outside bounds are clipped."""
        small_model.line(-5, 5, 15, 5, 255, 0, 0)
        # Only pixels within bounds should be set
        for x in range(10):
            assert tuple(small_model.fb[x, 5]) == (255, 0, 0)


class TestModelRect:
    """Tests for Model.rect() method."""

    def test_rect_outline(self, small_model: Model) -> None:
        """Verify rectangle outline drawing."""
        small_model.rect(2, 2, 5, 4, 255, 0, 0, fill=False)
        
        # Top edge (y=2, x from 2 to 6)
        for x in range(2, 7):
            assert tuple(small_model.fb[x, 2]) == (255, 0, 0), f"Top edge at ({x}, 2) not set"
        
        # Bottom edge (y=5, x from 2 to 6)
        for x in range(2, 7):
            assert tuple(small_model.fb[x, 5]) == (255, 0, 0), f"Bottom edge at ({x}, 5) not set"
        
        # Left edge (x=2, y from 2 to 5)
        for y in range(2, 6):
            assert tuple(small_model.fb[2, y]) == (255, 0, 0), f"Left edge at (2, {y}) not set"
        
        # Right edge (x=6, y from 2 to 5)
        for y in range(2, 6):
            assert tuple(small_model.fb[6, y]) == (255, 0, 0), f"Right edge at (6, {y}) not set"
        
        # Interior should be empty
        assert tuple(small_model.fb[4, 3]) == (0, 0, 0)

    def test_rect_filled(self, small_model: Model) -> None:
        """Verify filled rectangle drawing."""
        small_model.rect(2, 2, 5, 4, 0, 255, 0, fill=True)
        
        # All pixels in the rectangle should be set
        for x in range(2, 7):
            for y in range(2, 6):
                assert tuple(small_model.fb[x, y]) == (0, 255, 0), f"Pixel at ({x}, {y}) not set"
        
        # Pixels outside should not be set
        assert tuple(small_model.fb[1, 3]) == (0, 0, 0)
        assert tuple(small_model.fb[7, 3]) == (0, 0, 0)


class TestModelCircle:
    """Tests for Model.circle() method."""

    def test_circle_outline(self, model: Model) -> None:
        """Verify circle outline drawing."""
        model.circle(50, 50, 20, 255, 0, 0, fill=False)
        
        # Check that center is not filled
        assert tuple(model.fb[50, 50]) == (0, 0, 0)
        
        # Check that some edge points are set (approximate due to rasterization)
        # Top of circle (approximately at y=30)
        edge_found = False
        for y in range(28, 33):
            if tuple(model.fb[50, y]) == (255, 0, 0):
                edge_found = True
                break
        assert edge_found, "Top edge of circle not found"

    def test_circle_filled(self, model: Model) -> None:
        """Verify filled circle drawing."""
        model.circle(50, 50, 10, 0, 255, 0, fill=True)
        
        # Center should be filled
        assert tuple(model.fb[50, 50]) == (0, 255, 0)
        
        # Points inside radius should be filled
        assert tuple(model.fb[55, 50]) == (0, 255, 0)  # 5 pixels right of center
        assert tuple(model.fb[50, 55]) == (0, 255, 0)  # 5 pixels down from center
        
        # Points outside radius should not be filled
        assert tuple(model.fb[50, 35]) == (0, 0, 0)  # 15 pixels up from center
        assert tuple(model.fb[65, 50]) == (0, 0, 0)  # 15 pixels right of center

    def test_circle_at_edge(self, model: Model) -> None:
        """Verify circle drawing at edge of framebuffer is clipped."""
        # Circle at corner - should not crash
        model.circle(0, 0, 20, 255, 0, 0, fill=True)
        # Just verify it doesn't crash and some pixels are set
        assert tuple(model.fb[0, 0]) == (255, 0, 0)

    def test_circle_outside_bounds(self, model: Model) -> None:
        """Verify circle completely outside bounds doesn't crash."""
        # Circle completely outside - should not crash
        model.circle(-100, -100, 10, 255, 0, 0, fill=True)
        # Framebuffer should remain unchanged
        assert np.all(model.fb == 0)