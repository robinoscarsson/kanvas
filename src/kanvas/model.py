"""Model module for the Kanvas graphics framework.

This module provides the Model class for pixel-based graphics rendering,
along with noise generation functions for procedural content creation.

The Model class maintains a framebuffer and provides drawing primitives:
    - pixel(): Set individual pixels
    - line(): Draw lines using Bresenham's algorithm (optimized for h/v lines)
    - rect(): Draw rectangles (outline or filled, with vectorized fill)
    - circle(): Draw circles (outline or filled, using vectorized operations)
    - clear(): Clear the framebuffer with a color

Noise functions for procedural generation:
    - noise(): 2D value noise (smooth pseudo-random values)
    - p_noise(): 2D Perlin gradient noise (organic patterns)
    - noise_array(): Vectorized 2D value noise for entire arrays
    - p_noise_array(): Vectorized 2D Perlin noise for entire arrays

Example usage:
    model = Model(800, 600)
    model.clear(0)  # Black background
    model.circle(400, 300, 50, 255, 0, 0, fill=True)  # Red filled circle
"""
from __future__ import annotations

import random

import numpy as np
import numpy.typing as npt

# Module-level noise cache to avoid regenerating tables every frame
_noise_cache: dict[tuple[str, int, int], list[float] | tuple[list[int], list[tuple[float, float]]]] = {}


def _get_noise_table(seed: int = 42, size: int = 256) -> list[float]:
    """Get or create a cached noise permutation table.
    
    Generates a deterministic random permutation table for value noise.
    The table is cached at module level to avoid regeneration.
    
    Args:
        seed: Random seed for deterministic generation.
        size: Size of the permutation table.
    
    Returns:
        Permutation table of random floats in [0.0, 1.0].
    """
    key = ('value', seed, size)
    if key not in _noise_cache:
        rng = random.Random(seed)
        _noise_cache[key] = [rng.random() for _ in range(size)]
    return _noise_cache[key]  # type: ignore[return-value]


def _get_gradient_table(seed: int = 42, size: int = 256) -> tuple[list[int], list[tuple[float, float]]]:
    """Get or create a cached gradient vector table for Perlin noise.
    
    Generates deterministic gradient vectors on a 2D grid.
    Uses unit vectors at various angles for smooth interpolation.
    
    Args:
        seed: Random seed for deterministic generation.
        size: Size of the gradient table.
    
    Returns:
        Tuple of (permutation table, gradient vectors list).
    """
    key = ('gradient', seed, size)
    if key not in _noise_cache:
        rng = random.Random(seed)
        # Generate permutation table (0 to size-1)
        perm = list(range(size))
        rng.shuffle(perm)
        # Double it to avoid overflow
        perm = perm + perm
        
        # Generate gradient vectors (unit vectors at various angles)
        gradients: list[tuple[float, float]] = []
        for i in range(size):
            angle = 2.0 * 3.141592653589793 * i / size
            gradients.append((
                float(np.cos(angle)),
                float(np.sin(angle))
            ))
        
        _noise_cache[key] = (perm, gradients)
    return _noise_cache[key]  # type: ignore[return-value]


def _smoothstep(t: float) -> float:
    """Smooth interpolation function (3t^2 - 2t^3).
    
    Provides smooth transitions between 0 and 1 with zero derivatives at endpoints.
    
    Args:
        t: Input value in [0.0, 1.0].
    
    Returns:
        Smoothed value in [0.0, 1.0].
    """
    return t * t * (3.0 - 2.0 * t)


def _fade(t: float) -> float:
    """Perlin's fade function (6t^5 - 15t^4 + 10t^3).
    
    Improved smoothstep with zero first and second derivatives at endpoints.
    
    Args:
        t: Input value in [0.0, 1.0].
    
    Returns:
        Smoothed value in [0.0, 1.0].
    """
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values.
    
    Args:
        a: Start value.
        b: End value.
        t: Interpolation factor in [0.0, 1.0].
    
    Returns:
        Interpolated value.
    """
    return a + t * (b - a)

def noise(x: float, y: float, seed: int = 42) -> float:
    """2D value noise function (fake Perlin / semi-Perlin).
    
    Generates smooth pseudo-random values based on input coordinates.
    Uses a grid of random values with smooth interpolation.
    Deterministic based on seed - same inputs always produce same outputs.
    
    Usage example:
        # Generate a grayscale noise field
        scale = 0.02
        for x in range(width):
            for y in range(height):
                value = noise(x * scale, y * scale)
                gray = int(value * 255)
                model.pixel(x, y, gray, gray, gray)
    
    Args:
        x: X coordinate.
        y: Y coordinate.
        seed: Random seed for deterministic generation.
    
    Returns:
        Noise value in [0.0, 1.0].
    """
    table = _get_noise_table(seed)
    size = len(table)
    
    # Integer grid coordinates
    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    x1 = x0 + 1
    y1 = y0 + 1
    
    # Fractional part for interpolation
    fx = x - x0
    fy = y - y0
    
    # Smooth the interpolation factor
    sx = _smoothstep(fx)
    sy = _smoothstep(fy)
    
    # Hash coordinates to table indices
    def hash2d(ix: int, iy: int) -> float:
        idx = (ix % size * 57 + iy % size * 113) % size
        return table[idx]
    
    # Get corner values
    v00 = hash2d(x0, y0)
    v10 = hash2d(x1, y0)
    v01 = hash2d(x0, y1)
    v11 = hash2d(x1, y1)
    
    # Bilinear interpolation
    v0 = _lerp(v00, v10, sx)
    v1 = _lerp(v01, v11, sx)
    return _lerp(v0, v1, sy)

def p_noise(x: float, y: float, seed: int = 42) -> float:
    """2D Perlin gradient noise function.
    
    Classic Perlin noise using gradient vectors on an integer grid.
    Computes dot products with distance vectors and interpolates smoothly.
    Deterministic based on seed - same inputs always produce same outputs.
    Produces more organic-looking patterns than value noise.
    
    Usage example:
        # Animated flowing noise
        time = frame * 0.01
        scale = 0.05
        for x in range(width):
            for y in range(height):
                value = p_noise(x * scale + time, y * scale)
                gray = int(value * 255)
                model.pixel(x, y, gray, gray, gray)
    
    Args:
        x: X coordinate.
        y: Y coordinate.
        seed: Random seed for deterministic generation.
    
    Returns:
        Noise value in [0.0, 1.0].
    """
    perm, gradients = _get_gradient_table(seed)
    size = len(gradients)
    
    # Integer grid coordinates
    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    x1 = x0 + 1
    y1 = y0 + 1
    
    # Fractional part (distance from x0, y0)
    fx = x - x0
    fy = y - y0
    
    # Fade curves for smooth interpolation
    u = _fade(fx)
    v = _fade(fy)
    
    # Hash coordinates to gradient indices
    def hash2d(ix: int, iy: int) -> int:
        return perm[(perm[ix % size] + iy) % size] % size
    
    # Get gradient vectors for each corner
    g00 = gradients[hash2d(x0, y0)]
    g10 = gradients[hash2d(x1, y0)]
    g01 = gradients[hash2d(x0, y1)]
    g11 = gradients[hash2d(x1, y1)]
    
    # Compute dot products with distance vectors
    d00 = g00[0] * fx + g00[1] * fy
    d10 = g10[0] * (fx - 1.0) + g10[1] * fy
    d01 = g01[0] * fx + g01[1] * (fy - 1.0)
    d11 = g11[0] * (fx - 1.0) + g11[1] * (fy - 1.0)
    
    # Bilinear interpolation
    d0 = _lerp(d00, d10, u)
    d1 = _lerp(d01, d11, u)
    result = _lerp(d0, d1, v)
    
    # Perlin noise typically outputs in [-1, 1], map to [0, 1]
    return (result + 1.0) * 0.5


def noise_array(
    x: npt.NDArray[np.floating[npt.NBitBase]] | npt.NDArray[np.integer[npt.NBitBase]],
    y: npt.NDArray[np.floating[npt.NBitBase]] | npt.NDArray[np.integer[npt.NBitBase]],
    seed: int = 42
) -> npt.NDArray[np.float64]:
    """Vectorized 2D value noise function for entire arrays.
    
    Computes value noise for entire 2D coordinate arrays at once using numpy
    vectorization. This is dramatically faster than calling noise() in a loop
    for each pixel.
    
    Usage example:
        # Generate a grayscale noise field efficiently
        scale = 0.02
        x_coords, y_coords = np.meshgrid(
            np.arange(width) * scale,
            np.arange(height) * scale,
            indexing='ij'
        )
        values = noise_array(x_coords, y_coords)
        gray = (values * 255).astype(np.uint8)
        model.fb[:, :, 0] = gray
        model.fb[:, :, 1] = gray
        model.fb[:, :, 2] = gray
    
    Args:
        x: Array of X coordinates (any shape).
        y: Array of Y coordinates (same shape as x).
        seed: Random seed for deterministic generation.
    
    Returns:
        Array of noise values in [0.0, 1.0] with same shape as input.
    """
    table = _get_noise_table(seed)
    table_arr = np.array(table)
    size = len(table)
    
    # Integer grid coordinates
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1
    
    # Fractional part for interpolation
    fx = x - x0
    fy = y - y0
    
    # Smooth the interpolation factor (vectorized smoothstep)
    sx = fx * fx * (3.0 - 2.0 * fx)
    sy = fy * fy * (3.0 - 2.0 * fy)
    
    # Hash coordinates to table indices (vectorized)
    def hash2d_vec(ix: npt.NDArray[np.int64], iy: npt.NDArray[np.int64]) -> npt.NDArray[np.float64]:
        idx = (ix % size * 57 + iy % size * 113) % size
        return table_arr[idx]
    
    # Get corner values
    v00 = hash2d_vec(x0, y0)
    v10 = hash2d_vec(x1, y0)
    v01 = hash2d_vec(x0, y1)
    v11 = hash2d_vec(x1, y1)
    
    # Bilinear interpolation (vectorized lerp)
    v0 = v00 + sx * (v10 - v00)
    v1 = v01 + sx * (v11 - v01)
    return v0 + sy * (v1 - v0)


def p_noise_array(
    x: npt.NDArray[np.floating[npt.NBitBase]] | npt.NDArray[np.integer[npt.NBitBase]],
    y: npt.NDArray[np.floating[npt.NBitBase]] | npt.NDArray[np.integer[npt.NBitBase]],
    seed: int = 42
) -> npt.NDArray[np.float64]:
    """Vectorized 2D Perlin gradient noise function for entire arrays.
    
    Computes Perlin noise for entire 2D coordinate arrays at once using numpy
    vectorization. This is dramatically faster than calling p_noise() in a loop
    for each pixel.
    
    Usage example:
        # Animated flowing noise efficiently
        time = frame * 0.01
        scale = 0.05
        x_coords, y_coords = np.meshgrid(
            np.arange(width) * scale + time,
            np.arange(height) * scale,
            indexing='ij'
        )
        values = p_noise_array(x_coords, y_coords)
        gray = (values * 255).astype(np.uint8)
        model.fb[:, :, 0] = gray
        model.fb[:, :, 1] = gray
        model.fb[:, :, 2] = gray
    
    Args:
        x: Array of X coordinates (any shape).
        y: Array of Y coordinates (same shape as x).
        seed: Random seed for deterministic generation.
    
    Returns:
        Array of noise values in [0.0, 1.0] with same shape as input.
    """
    perm, gradients = _get_gradient_table(seed)
    perm_arr = np.array(perm)
    grad_arr = np.array(gradients)  # Shape: (size, 2)
    size = len(gradients)
    
    # Integer grid coordinates
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1
    
    # Fractional part (distance from x0, y0)
    fx = x - x0
    fy = y - y0
    
    # Fade curves for smooth interpolation (vectorized)
    # Perlin's fade: 6t^5 - 15t^4 + 10t^3
    u = fx * fx * fx * (fx * (fx * 6.0 - 15.0) + 10.0)
    v = fy * fy * fy * (fy * (fy * 6.0 - 15.0) + 10.0)
    
    # Hash coordinates to gradient indices (vectorized)
    def hash2d_vec(ix: npt.NDArray[np.int64], iy: npt.NDArray[np.int64]) -> npt.NDArray[np.int64]:
        return perm_arr[(perm_arr[ix % size] + iy) % size] % size
    
    # Get gradient indices for each corner
    gi00 = hash2d_vec(x0, y0)
    gi10 = hash2d_vec(x1, y0)
    gi01 = hash2d_vec(x0, y1)
    gi11 = hash2d_vec(x1, y1)
    
    # Get gradient vectors (gx, gy components)
    g00_x, g00_y = grad_arr[gi00, 0], grad_arr[gi00, 1]
    g10_x, g10_y = grad_arr[gi10, 0], grad_arr[gi10, 1]
    g01_x, g01_y = grad_arr[gi01, 0], grad_arr[gi01, 1]
    g11_x, g11_y = grad_arr[gi11, 0], grad_arr[gi11, 1]
    
    # Compute dot products with distance vectors
    d00 = g00_x * fx + g00_y * fy
    d10 = g10_x * (fx - 1.0) + g10_y * fy
    d01 = g01_x * fx + g01_y * (fy - 1.0)
    d11 = g11_x * (fx - 1.0) + g11_y * (fy - 1.0)
    
    # Bilinear interpolation (vectorized lerp)
    d0 = d00 + u * (d10 - d00)
    d1 = d01 + u * (d11 - d01)
    result = d0 + v * (d1 - d0)
    
    # Perlin noise typically outputs in [-1, 1], map to [0, 1]
    return (result + 1.0) * 0.5


class Model:
    """A framebuffer model for pixel-based graphics rendering.
    
    The Model class provides a 2D framebuffer for storing and manipulating pixel data.
    It supports basic operations like clearing the screen and setting individual pixels
    with RGB color values.
    
    Attributes:
        w (int): Width of the framebuffer in pixels.
        h (int): Height of the framebuffer in pixels.
        fb (numpy.ndarray): 3D numpy array storing RGB pixel data with shape (width, height, 3).
    """
    
    def __init__(self, w: int, h: int) -> None:
        """Initialize a new Model with specified dimensions.
        
        Creates a framebuffer with the given width and height, initialized to black (0,0,0).
        
        Args:
            w: Width of the framebuffer in pixels.
            h: Height of the framebuffer in pixels.
        """
        self.w: int = w
        self.h: int = h
        self.fb: npt.NDArray[np.uint8] = np.zeros((w, h, 3), dtype=np.uint8)

    def clear(self, r: int, g: int | None = None, b: int | None = None) -> None:
        """Clear the entire framebuffer with a specified color.
        
        Sets all pixels in the framebuffer to the specified RGB color.
        If only the red component is provided, it will be used for all three
        color components (creating a grayscale color).
        
        Args:
            r: Red color component (0-255).
            g: Green color component (0-255). If None, uses the value of r.
            b: Blue color component (0-255). If None, uses the value of r.
        """
        if g is None:
            g = b = r
        self.fb[:] = (r, g, b)

    def pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """Set a single pixel to the specified RGB color.
        
        Sets the pixel at coordinates (x, y) to the given RGB color values.
        The operation is bounds-checked; pixels outside the framebuffer dimensions
        are ignored to prevent array index errors.
        
        Args:
            x: X-coordinate of the pixel (0 to width-1).
            y: Y-coordinate of the pixel (0 to height-1).
            r: Red color component (0-255).
            g: Green color component (0-255).
            b: Blue color component (0-255).
        """
        if 0 <= x < self.w and 0 <= y < self.h:
            self.fb[x, y] = (r, g, b)

    def line(self, x0: int, y0: int, x1: int, y1: int, r: int, g: int, b: int) -> None:
        """Draw a line between two points using Bresenham's line algorithm.
        
        Draws a line from point (x0, y0) to point (x1, y1) with the specified RGB color.
        Uses Bresenham's line algorithm for efficient rasterization. The line is clipped
        to the framebuffer boundaries to prevent out-of-bounds errors.
        
        For horizontal and vertical lines, uses optimized numpy slice assignment
        for better performance.
        
        Args:
            x0: X-coordinate of the starting point.
            y0: Y-coordinate of the starting point.
            x1: X-coordinate of the ending point.
            y1: Y-coordinate of the ending point.
            r: Red color component (0-255).
            g: Green color component (0-255).
            b: Blue color component (0-255).
        """
        # Optimized path for horizontal lines
        if y0 == y1:
            if x0 > x1:
                x0, x1 = x1, x0
            # Clip to framebuffer bounds
            if y0 < 0 or y0 >= self.h:
                return
            x_start = max(0, x0)
            x_end = min(self.w, x1 + 1)
            if x_start < x_end:
                self.fb[x_start:x_end, y0] = (r, g, b)
            return
        
        # Optimized path for vertical lines
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            # Clip to framebuffer bounds
            if x0 < 0 or x0 >= self.w:
                return
            y_start = max(0, y0)
            y_end = min(self.h, y1 + 1)
            if y_start < y_end:
                self.fb[x0, y_start:y_end] = (r, g, b)
            return
        
        # Bresenham's algorithm for diagonal lines
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy  # initial error

        while True:
            # bounds check to prevent crashes if coordinates are outside framebuffer
            if 0 <= x0 < self.w and 0 <= y0 < self.h:
                self.fb[x0, y0] = (r, g, b)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def rect(self, x: int, y: int, w: int, h: int, r: int, g: int, b: int, fill: bool = False) -> None:
        """Draw a rectangle with the specified position, size, and color.
        
        Draws a rectangle starting at position (x, y) with the given width and height.
        The rectangle can be drawn as either an outline (default) or filled based on
        the fill parameter. Uses the line() method to draw the outline and numpy
        slice assignment for efficient filling.
        
        Args:
            x: X-coordinate of the top-left corner.
            y: Y-coordinate of the top-left corner.
            w: Width of the rectangle in pixels.
            h: Height of the rectangle in pixels.
            r: Red color component (0-255).
            g: Green color component (0-255).
            b: Blue color component (0-255).
            fill: If True, fills the rectangle; if False, draws only the outline.
        """
        # outer frame (uses optimized horizontal/vertical line paths)
        self.line(x, y, x + w - 1, y, r, g, b)               # top
        self.line(x, y, x, y + h - 1, r, g, b)               # left
        self.line(x + w - 1, y, x + w - 1, y + h - 1, r, g, b)  # right
        self.line(x, y + h - 1, x + w - 1, y + h - 1, r, g, b)  # bottom

        if fill:
            # Optimized fill using numpy slice assignment
            # Calculate interior bounds with clipping
            x_start = max(0, x + 1)
            x_end = min(self.w, x + w - 1)
            y_start = max(0, y + 1)
            y_end = min(self.h, y + h - 1)
            
            if x_start < x_end and y_start < y_end:
                self.fb[x_start:x_end, y_start:y_end] = (r, g, b)

    def circle(self, cx: int, cy: int, radius: int, r: int, g: int, b: int, fill: bool = False) -> None:
        """Draw a circle with the specified center, radius, and color.
        
        Draws a circle centered at position (cx, cy) with the given radius and RGB color.
        The circle can be drawn as either an outline (default) or filled based on the
        fill parameter. Uses numpy vectorized operations with meshgrid for efficient
        distance calculations.
        
        Args:
            cx: X-coordinate of the circle's center.
            cy: Y-coordinate of the circle's center.
            radius: Radius of the circle in pixels.
            r: Red color component (0-255).
            g: Green color component (0-255).
            b: Blue color component (0-255).
            fill: If True, fills the circle; if False, draws only the outline.
        """
        r2 = radius * radius
        
        # Calculate bounding box with clipping to framebuffer
        x_start = max(0, cx - radius)
        x_end = min(self.w, cx + radius + 1)
        y_start = max(0, cy - radius)
        y_end = min(self.h, cy + radius + 1)
        
        # Early exit if circle is completely outside framebuffer
        if x_start >= x_end or y_start >= y_end:
            return
        
        # Create coordinate grids for the bounding box region
        # Using ogrid for memory efficiency (creates 1D arrays that broadcast)
        x_coords = np.arange(x_start, x_end)
        y_coords = np.arange(y_start, y_end)
        
        # Calculate squared distances from center using broadcasting
        # dx has shape (x_end - x_start,), dy has shape (y_end - y_start,)
        dx = x_coords - cx
        dy = y_coords - cy
        
        # dist2 will have shape (x_end - x_start, y_end - y_start) via broadcasting
        dist2 = dx[:, np.newaxis]**2 + dy[np.newaxis, :]**2
        
        if fill:
            # All points inside the circle
            mask = dist2 <= r2
        else:
            # Only points near the edge (tolerance band)
            mask = (dist2 >= r2 - radius) & (dist2 <= r2 + radius)
        
        # Apply color to masked pixels
        # Create a view of the relevant framebuffer region
        fb_region = self.fb[x_start:x_end, y_start:y_end]
        fb_region[mask] = (r, g, b)
