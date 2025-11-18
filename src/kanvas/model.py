import numpy as np

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
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy  # startfel

        while True:
            # bounds-koll så vi inte kraschar om användaren är utanför
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
        # yttre ram
        self.line(x, y, x + w - 1, y, r, g, b)               # topp
        self.line(x, y, x, y + h - 1, r, g, b)               # vänster
        self.line(x + w - 1, y, x + w - 1, y + h - 1, r, g, b)  # höger
        self.line(x, y + h - 1, x + w - 1, y + h - 1, r, g, b)  # botten

        if fill:
            # enkel fill: horisontella linjer mellan vänster/höger
            for yy in range(y + 1, y + h - 1):
                self.line(x + 1, yy, x + w - 2, yy, r, g, b)

    def circle(self, cx, cy, radius, r, g, b, fill=False):
        r2 = radius * radius

        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                dx = x - cx
                dy = y - cy
                dist2 = dx*dx + dy*dy

                if fill:
                    # alla punkter *inom* cirkeln
                    if dist2 <= r2:
                        if 0 <= x < self.w and 0 <= y < self.h:
                            self.pixel(x, y, r, g, b)
                else:
                    # bara punkter nära kanten (toleransband)
                    if r2 - radius <= dist2 <= r2 + radius:
                        if 0 <= x < self.w and 0 <= y < self.h:
                            self.pixel(x, y, r, g, b)
