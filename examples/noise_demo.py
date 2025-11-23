from kanvas import run
from kanvas.model import noise, p_noise

def setup(model):
    """Initialize the canvas with a black background."""
    model.clear(0)
    
    # Generate noise field once during setup
    # Scale factor for noise coordinates (smaller = more zoomed out)
    scale = 0.02
    
    # Generate noise field pixel by pixel
    for x in range(model.w):
        for y in range(model.h):
            # Map pixel coordinates to noise space
            nx = x * scale
            ny = y * scale
            
            if x < model.w // 2:
                # Left half: value noise (smoother, simpler)
                value = noise(nx, ny, seed=42)
            else:
                # Right half: Perlin gradient noise (more organic)
                value = p_noise(nx, ny, seed=42)
            
            # Map [0.0, 1.0] to grayscale [0, 255]
            gray = int(value * 255)
            model.pixel(x, y, gray, gray, gray)

def draw(model, frame, dt):
    """Draw loop - nothing to update, noise is static."""
    # Static display - all rendering done in setup
    pass

run(setup, draw, size=(400, 300), title="Noise Demo: Value (L) vs Perlin (R)")
