"""
Kanvas - A minimalist creative-coding toolkit for Python.

Inspired by Processing/p5.js, Kanvas provides a simple setup()/draw() loop
pattern with a pixel-based drawing API for educational and creative coding.

Example:
    from kanvas import run, Model
    
    def setup(model: Model) -> None:
        model.clear(0)
    
    def draw(model: Model, frame: int, dt: float) -> None:
        model.circle(200, 200, 50, 255, 0, 0, fill=True)
    
    run(setup, draw, size=(400, 400), title="My Sketch")
"""

from kanvas.core import run, noLoop, loop, isLooping
from kanvas.model import Model, noise, p_noise, noise_array, p_noise_array
from kanvas.utils import map_range, constrain, lerp, dist, rgb_to_hsv, hsv_to_rgb

__version__ = "0.1.7"

__all__ = [
    # Core functions
    "run",
    "noLoop",
    "loop",
    "isLooping",
    # Model class
    "Model",
    # Noise functions
    "noise",
    "p_noise",
    "noise_array",
    "p_noise_array",
    # Utility functions
    "map_range",
    "constrain",
    "lerp",
    "dist",
    "rgb_to_hsv",
    "hsv_to_rgb",
    # Version
    "__version__",
]