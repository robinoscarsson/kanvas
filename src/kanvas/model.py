import numpy as np
import random

# Module-level noise cache to avoid regenerating tables every frame
_noise_cache = {}

def _get_noise_table(seed=42, size=256):
    """Get or create a cached noise permutation table.
    
    Generates a deterministic random permutation table for value noise.
    The table is cached at module level to avoid regeneration.
    
    Args:
        seed (int): Random seed for deterministic generation.
        size (int): Size of the permutation table.
    
    Returns:
        list: Permutation table of random floats in [0.0, 1.0].
    """
    key = ('value', seed, size)
    if key not in _noise_cache:
        rng = random.Random(seed)
        _noise_cache[key] = [rng.random() for _ in range(size)]
    return _noise_cache[key]

def _get_gradient_table(seed=42, size=256):
    """Get or create a cached gradient vector table for Perlin noise.
    
    Generates deterministic gradient vectors on a 2D grid.
    Uses unit vectors at various angles for smooth interpolation.
    
    Args:
        seed (int): Random seed for deterministic generation.
        size (int): Size of the gradient table.
    
    Returns:
        tuple: (permutation table, gradient vectors list)
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
        gradients = []
        for i in range(size):
            angle = 2.0 * 3.141592653589793 * i / size
            gradients.append((
                np.cos(angle),
                np.sin(angle)
            ))
        
        _noise_cache[key] = (perm, gradients)
    return _noise_cache[key]

def _smoothstep(t):
    """Smooth interpolation function (3t^2 - 2t^3).
    
    Provides smooth transitions between 0 and 1 with zero derivatives at endpoints.
    
    Args:
        t (float): Input value in [0.0, 1.0].
    
    Returns:
        float: Smoothed value in [0.0, 1.0].
    """
    return t * t * (3.0 - 2.0 * t)

def _fade(t):
    """Perlin's fade function (6t^5 - 15t^4 + 10t^3).
    
    Improved smoothstep with zero first and second derivatives at endpoints.
    
    Args:
        t (float): Input value in [0.0, 1.0].
    
    Returns:
        float: Smoothed value in [0.0, 1.0].
    """
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

def _lerp(a, b, t):
    """Linear interpolation between two values.
    
    Args:
        a (float): Start value.
        b (float): End value.
        t (float): Interpolation factor in [0.0, 1.0].
    
    Returns:
        float: Interpolated value.
    """
    return a + t * (b - a)

def noise(x, y, seed=42):
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
        x (float): X coordinate.
        y (float): Y coordinate.
        seed (int): Random seed for deterministic generation.
    
    Returns:
        float: Noise value in [0.0, 1.0].
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
    def hash2d(ix, iy):
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

def p_noise(x, y, seed=42):
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
        x (float): X coordinate.
        y (float): Y coordinate.
        seed (int): Random seed for deterministic generation.
    
    Returns:
        float: Noise value in [0.0, 1.0].
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
    def hash2d(ix, iy):
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
    
    def __init__(self, w: int, h: int):
        """Initialize a new Model with specified dimensions.
        
        Creates a framebuffer with the given width and height, initialized to black (0,0,0).
        
        Args:
            w (int): Width of the framebuffer in pixels.
            h (int): Height of the framebuffer in pixels.
        """
        self.w, self.h = w, h
        self.fb = np.zeros((w, h, 3), dtype=np.uint8)

    def clear(self, r: int, g: int = None, b: int = None):
        """Clear the entire framebuffer with a specified color.
        
        Sets all pixels in the framebuffer to the specified RGB color.
        If only the red component is provided, it will be used for all three
        color components (creating a grayscale color).
        
        Args:
            r (int): Red color component (0-255).
            g (int, optional): Green color component (0-255). If None, uses the value of r.
            b (int, optional): Blue color component (0-255). If None, uses the value of r.
        """
        if g is None: g = b = r
        self.fb[:] = (r, g, b)

    def pixel(self, x: int, y: int, r: int, g: int, b: int):
        """Set a single pixel to the specified RGB color.
        
        Sets the pixel at coordinates (x, y) to the given RGB color values.
        The operation is bounds-checked; pixels outside the framebuffer dimensions
        are ignored to prevent array index errors.
        
        Args:
            x (int): X-coordinate of the pixel (0 to width-1).
            y (int): Y-coordinate of the pixel (0 to height-1).
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
        """
        if 0 <= x < self.w and 0 <= y < self.h:
            self.fb[x, y] = (r, g, b)

    def line(self, x0, y0, x1, y1, r, g, b):
        """Draw a line between two points using Bresenham's line algorithm.
        
        Draws a line from point (x0, y0) to point (x1, y1) with the specified RGB color.
        Uses Bresenham's line algorithm for efficient rasterization. The line is clipped
        to the framebuffer boundaries to prevent out-of-bounds errors.
        
        Args:
            x0 (int): X-coordinate of the starting point.
            y0 (int): Y-coordinate of the starting point.
            x1 (int): X-coordinate of the ending point.
            y1 (int): Y-coordinate of the ending point.
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
        """
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy  # initial error

        while True:
            # bounds check to prevent crashes if coordinates are outside framebuffer
            if 0 <= x0 < self.w and 0 <= y0 < self.h:
                self.pixel(x0, y0, r, g, b)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def rect(self, x, y, w, h, r, g, b, fill=False):
        """Draw a rectangle with the specified position, size, and color.
        
        Draws a rectangle starting at position (x, y) with the given width and height.
        The rectangle can be drawn as either an outline (default) or filled based on
        the fill parameter. Uses the line() method to draw the outline and horizontal
        lines for filling.
        
        Args:
            x (int): X-coordinate of the top-left corner.
            y (int): Y-coordinate of the top-left corner.
            w (int): Width of the rectangle in pixels.
            h (int): Height of the rectangle in pixels.
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
            fill (bool, optional): If True, fills the rectangle; if False, draws only the outline. Defaults to False.
        """
        # outer frame
        self.line(x, y, x + w - 1, y, r, g, b)               # top
        self.line(x, y, x, y + h - 1, r, g, b)               # left
        self.line(x + w - 1, y, x + w - 1, y + h - 1, r, g, b)  # right
        self.line(x, y + h - 1, x + w - 1, y + h - 1, r, g, b)  # bottom

        if fill:
            # simple fill: horizontal lines between left/right edges
            for yy in range(y + 1, y + h - 1):
                self.line(x + 1, yy, x + w - 2, yy, r, g, b)

    def circle(self, cx, cy, radius, r, g, b, fill=False):
        """Draw a circle with the specified center, radius, and color.
        
        Draws a circle centered at position (cx, cy) with the given radius and RGB color.
        The circle can be drawn as either an outline (default) or filled based on the
        fill parameter. Uses a simple pixel-by-pixel approach with distance calculations
        to determine which pixels belong to the circle.
        
        Args:
            cx (int): X-coordinate of the circle's center.
            cy (int): Y-coordinate of the circle's center.
            radius (int): Radius of the circle in pixels.
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
            fill (bool, optional): If True, fills the circle; if False, draws only the outline. Defaults to False.
        """
        r2 = radius * radius

        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                dx = x - cx
                dy = y - cy
                dist2 = dx*dx + dy*dy

                if fill:
                    # all points *inside* the circle
                    if dist2 <= r2:
                        if 0 <= x < self.w and 0 <= y < self.h:
                            self.pixel(x, y, r, g, b)
                else:
                    # only points near the edge (tolerance band)
                    if r2 - radius <= dist2 <= r2 + radius:
                        if 0 <= x < self.w and 0 <= y < self.h:
                            self.pixel(x, y, r, g, b)
