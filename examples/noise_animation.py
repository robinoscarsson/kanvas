from kanvas import run
from kanvas.model import noise, p_noise

def setup(model):
    """Initialize the canvas."""
    model.clear(0)

def draw(model, frame, dt):
    """Animate noise by adding time offset.
    
    This demonstrates how to create flowing noise patterns
    by shifting the noise coordinates over time.
    """
    model.clear(0)
    
    # Use frame counter as time offset
    time_offset = frame * 0.01
    scale = 0.05
    
    # Draw a vertical strip of animated noise in the center
    center_x = model.w // 2
    strip_width = 100
    
    for x in range(center_x - strip_width // 2, center_x + strip_width // 2):
        for y in range(model.h):
            # Add time to x coordinate for horizontal flow
            nx = x * scale + time_offset
            ny = y * scale
            
            # Use Perlin noise for smoother animation
            value = p_noise(nx, ny, seed=42)
            
            # Map to grayscale
            gray = int(value * 255)
            model.pixel(x, y, gray, gray, gray)
    
    # Draw reference lines
    model.line(center_x - strip_width // 2, 0, 
               center_x - strip_width // 2, model.h - 1, 
               255, 0, 0)
    model.line(center_x + strip_width // 2 - 1, 0, 
               center_x + strip_width // 2 - 1, model.h - 1, 
               255, 0, 0)

run(setup, draw, size=(400, 300), title="Animated Noise Flow")
