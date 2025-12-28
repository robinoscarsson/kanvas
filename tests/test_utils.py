"""Tests for utility functions."""

import pytest

from kanvas.utils import map_range, constrain, lerp, dist, rgb_to_hsv, hsv_to_rgb


class TestMapRange:
    """Tests for the map_range function."""

    def test_map_range(self) -> None:
        """Verify value mapping from one range to another."""
        # Map 5 from [0, 10] to [0, 100]
        result = map_range(5, 0, 10, 0, 100)
        assert result == 50.0

    def test_map_range_inverse(self) -> None:
        """Verify inverse mapping (target range is reversed)."""
        # Map 5 from [0, 10] to [100, 0] (inverted)
        result = map_range(5, 0, 10, 100, 0)
        assert result == 50.0

    def test_map_range_start(self) -> None:
        """Verify mapping at start of range."""
        result = map_range(0, 0, 10, 0, 100)
        assert result == 0.0

    def test_map_range_end(self) -> None:
        """Verify mapping at end of range."""
        result = map_range(10, 0, 10, 0, 100)
        assert result == 100.0

    def test_map_range_negative(self) -> None:
        """Verify mapping with negative ranges."""
        result = map_range(0, -10, 10, 0, 100)
        assert result == 50.0

    def test_map_range_outside_source(self) -> None:
        """Verify mapping extrapolates outside source range."""
        result = map_range(15, 0, 10, 0, 100)
        assert result == 150.0


class TestConstrain:
    """Tests for the constrain function."""

    def test_constrain_within_range(self) -> None:
        """Verify value within range is unchanged."""
        result = constrain(50, 0, 100)
        assert result == 50

    def test_constrain_below_range(self) -> None:
        """Verify value below range is clamped to minimum."""
        result = constrain(-10, 0, 100)
        assert result == 0

    def test_constrain_above_range(self) -> None:
        """Verify value above range is clamped to maximum."""
        result = constrain(150, 0, 100)
        assert result == 100

    def test_constrain_at_minimum(self) -> None:
        """Verify value at minimum is unchanged."""
        result = constrain(0, 0, 100)
        assert result == 0

    def test_constrain_at_maximum(self) -> None:
        """Verify value at maximum is unchanged."""
        result = constrain(100, 0, 100)
        assert result == 100

    def test_constrain_negative_range(self) -> None:
        """Verify constrain works with negative ranges."""
        result = constrain(-50, -100, -10)
        assert result == -50
        
        result = constrain(0, -100, -10)
        assert result == -10


class TestLerp:
    """Tests for the lerp (linear interpolation) function."""

    def test_lerp_start(self) -> None:
        """Verify lerp at 0 returns start value."""
        result = lerp(0, 100, 0)
        assert result == 0.0

    def test_lerp_end(self) -> None:
        """Verify lerp at 1 returns end value."""
        result = lerp(0, 100, 1)
        assert result == 100.0

    def test_lerp_middle(self) -> None:
        """Verify lerp at 0.5 returns midpoint."""
        result = lerp(0, 100, 0.5)
        assert result == 50.0

    def test_lerp_quarter(self) -> None:
        """Verify lerp at 0.25 returns quarter point."""
        result = lerp(0, 100, 0.25)
        assert result == 25.0

    def test_lerp_negative_values(self) -> None:
        """Verify lerp works with negative values."""
        result = lerp(-100, 100, 0.5)
        assert result == 0.0

    def test_lerp_extrapolate(self) -> None:
        """Verify lerp extrapolates beyond [0, 1]."""
        result = lerp(0, 100, 1.5)
        assert result == 150.0
        
        result = lerp(0, 100, -0.5)
        assert result == -50.0


class TestDist:
    """Tests for the dist (distance) function."""

    def test_dist_same_point(self) -> None:
        """Verify distance to same point is 0."""
        result = dist(5, 5, 5, 5)
        assert result == 0.0

    def test_dist_horizontal(self) -> None:
        """Verify horizontal distance."""
        result = dist(0, 0, 10, 0)
        assert result == 10.0

    def test_dist_vertical(self) -> None:
        """Verify vertical distance."""
        result = dist(0, 0, 0, 10)
        assert result == 10.0

    def test_dist_diagonal(self) -> None:
        """Verify diagonal distance (3-4-5 triangle)."""
        result = dist(0, 0, 3, 4)
        assert result == 5.0

    def test_dist_negative_coordinates(self) -> None:
        """Verify distance with negative coordinates."""
        result = dist(-3, -4, 0, 0)
        assert result == 5.0

    def test_dist_symmetric(self) -> None:
        """Verify distance is symmetric."""
        d1 = dist(0, 0, 3, 4)
        d2 = dist(3, 4, 0, 0)
        assert d1 == d2


class TestRgbToHsv:
    """Tests for RGB to HSV color conversion."""

    def test_rgb_to_hsv_red(self) -> None:
        """Verify pure red converts correctly."""
        h, s, v = rgb_to_hsv(255, 0, 0)
        assert h == 0.0
        assert s == 1.0
        assert v == 1.0

    def test_rgb_to_hsv_green(self) -> None:
        """Verify pure green converts correctly."""
        h, s, v = rgb_to_hsv(0, 255, 0)
        assert h == 120.0
        assert s == 1.0
        assert v == 1.0

    def test_rgb_to_hsv_blue(self) -> None:
        """Verify pure blue converts correctly."""
        h, s, v = rgb_to_hsv(0, 0, 255)
        assert h == 240.0
        assert s == 1.0
        assert v == 1.0

    def test_rgb_to_hsv_white(self) -> None:
        """Verify white converts correctly."""
        h, s, v = rgb_to_hsv(255, 255, 255)
        assert h == 0.0  # Hue is undefined for white, typically 0
        assert s == 0.0
        assert v == 1.0

    def test_rgb_to_hsv_black(self) -> None:
        """Verify black converts correctly."""
        h, s, v = rgb_to_hsv(0, 0, 0)
        assert h == 0.0  # Hue is undefined for black, typically 0
        assert s == 0.0
        assert v == 0.0

    def test_rgb_to_hsv_gray(self) -> None:
        """Verify gray converts correctly."""
        h, s, v = rgb_to_hsv(128, 128, 128)
        assert h == 0.0  # Hue is undefined for gray
        assert s == 0.0
        assert pytest.approx(v, rel=0.01) == 128 / 255


class TestHsvToRgb:
    """Tests for HSV to RGB color conversion."""

    def test_hsv_to_rgb_red(self) -> None:
        """Verify pure red converts correctly."""
        r, g, b = hsv_to_rgb(0, 1.0, 1.0)
        assert r == 255
        assert g == 0
        assert b == 0

    def test_hsv_to_rgb_green(self) -> None:
        """Verify pure green converts correctly."""
        r, g, b = hsv_to_rgb(120, 1.0, 1.0)
        assert r == 0
        assert g == 255
        assert b == 0

    def test_hsv_to_rgb_blue(self) -> None:
        """Verify pure blue converts correctly."""
        r, g, b = hsv_to_rgb(240, 1.0, 1.0)
        assert r == 0
        assert g == 0
        assert b == 255

    def test_hsv_to_rgb_white(self) -> None:
        """Verify white converts correctly."""
        r, g, b = hsv_to_rgb(0, 0.0, 1.0)
        assert r == 255
        assert g == 255
        assert b == 255

    def test_hsv_to_rgb_black(self) -> None:
        """Verify black converts correctly."""
        r, g, b = hsv_to_rgb(0, 0.0, 0.0)
        assert r == 0
        assert g == 0
        assert b == 0

    def test_hsv_to_rgb_yellow(self) -> None:
        """Verify yellow converts correctly."""
        r, g, b = hsv_to_rgb(60, 1.0, 1.0)
        assert r == 255
        assert g == 255
        assert b == 0

    def test_hsv_to_rgb_cyan(self) -> None:
        """Verify cyan converts correctly."""
        r, g, b = hsv_to_rgb(180, 1.0, 1.0)
        assert r == 0
        assert g == 255
        assert b == 255

    def test_hsv_to_rgb_magenta(self) -> None:
        """Verify magenta converts correctly."""
        r, g, b = hsv_to_rgb(300, 1.0, 1.0)
        assert r == 255
        assert g == 0
        assert b == 255


class TestRgbHsvRoundtrip:
    """Tests for RGB -> HSV -> RGB roundtrip conversion."""

    def test_rgb_hsv_roundtrip_red(self) -> None:
        """Verify RGB -> HSV -> RGB roundtrip for red."""
        original = (255, 0, 0)
        h, s, v = rgb_to_hsv(*original)
        result = hsv_to_rgb(h, s, v)
        assert result == original

    def test_rgb_hsv_roundtrip_green(self) -> None:
        """Verify RGB -> HSV -> RGB roundtrip for green."""
        original = (0, 255, 0)
        h, s, v = rgb_to_hsv(*original)
        result = hsv_to_rgb(h, s, v)
        assert result == original

    def test_rgb_hsv_roundtrip_blue(self) -> None:
        """Verify RGB -> HSV -> RGB roundtrip for blue."""
        original = (0, 0, 255)
        h, s, v = rgb_to_hsv(*original)
        result = hsv_to_rgb(h, s, v)
        assert result == original

    def test_rgb_hsv_roundtrip_arbitrary(self) -> None:
        """Verify RGB -> HSV -> RGB roundtrip for arbitrary color."""
        original = (128, 64, 192)
        h, s, v = rgb_to_hsv(*original)
        result = hsv_to_rgb(h, s, v)
        # Allow small rounding differences due to integer conversion
        assert abs(result[0] - original[0]) <= 1
        assert abs(result[1] - original[1]) <= 1
        assert abs(result[2] - original[2]) <= 1

    def test_rgb_hsv_roundtrip_white(self) -> None:
        """Verify RGB -> HSV -> RGB roundtrip for white."""
        original = (255, 255, 255)
        h, s, v = rgb_to_hsv(*original)
        result = hsv_to_rgb(h, s, v)
        assert result == original

    def test_rgb_hsv_roundtrip_black(self) -> None:
        """Verify RGB -> HSV -> RGB roundtrip for black."""
        original = (0, 0, 0)
        h, s, v = rgb_to_hsv(*original)
        result = hsv_to_rgb(h, s, v)
        assert result == original