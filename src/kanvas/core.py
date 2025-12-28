"""Core module for the Kanvas graphics framework.

This module provides the main application loop and control functions for
running Kanvas sketches. It handles window creation, frame timing, input
processing, and the setup/draw lifecycle similar to Processing/p5.js.

Key functions:
    - run(): Main entry point to start a Kanvas application
    - loop()/noLoop(): Control whether draw() is called each frame
    - isLooping(): Check if the draw loop is active

Example usage:
    from kanvas import run
    
    def setup(model):
        model.clear(0)
    
    def draw(model, frame_count, delta_ms):
        model.pixel(100, 100, 255, 255, 255)
    
    run(setup, draw, size=(800, 600), title="My Sketch")
"""
from __future__ import annotations

import time
from typing import Callable

from . import view, controller
from .model import Model

# Global flag to control the draw loop
_loop_enabled = True

def noLoop() -> None:
    """Stop the draw loop from running.
    
    Similar to p5.js noLoop(), this stops the draw() function from being
    called repeatedly. The application will continue to respond to input
    but draw() will no longer be executed each frame.
    """
    global _loop_enabled
    _loop_enabled = False


def loop() -> None:
    """Resume the draw loop.
    
    Similar to p5.js loop(), this resumes calling the draw() function
    each frame after it was stopped with noLoop().
    """
    global _loop_enabled
    _loop_enabled = True


def isLooping() -> bool:
    """Check if the draw loop is currently running.
    
    Returns:
        bool: True if draw() is being called each frame, False if stopped with noLoop()
    """
    return _loop_enabled


def run(
    setup: Callable[[Model], None],
    draw: Callable[[Model, int, float], None],
    target_fps: int = 60,
    size: tuple[int, int] = (640, 360),
    title: str = "kanvas",
) -> None:
    """Main application loop for kanvas.
    
    Args:
        setup: Function to call once at startup. Receives the Model instance.
        draw: Function to call each frame. Receives (model, frame_count, delta_ms).
        target_fps: Target frames per second (default: 60).
        size: Window size as (width, height) tuple (default: (640, 360)).
        title: Window title (default: "kanvas").
    """
    # Initialize application
    model = _initialize_application(setup, size, title)
    
    # Run main loop
    _run_main_loop(draw, model, target_fps, title)
    
    # Clean up
    view.shutdown()


def _initialize_application(
    setup: Callable[[Model], None],
    size: tuple[int, int],
    title: str,
) -> Model:
    """Initialize the application window and model.
    
    Args:
        setup: The setup function to call with the model.
        size: Window size as (width, height) tuple.
        title: Window title.
    
    Returns:
        The initialized Model instance.
    """
    view.create_window(*size, title=title)
    model = Model(size[0], size[1])
    setup(model)
    return model


def _run_main_loop(
    draw: Callable[[Model, int, float], None],
    model: Model,
    target_fps: int,
    title: str,
) -> None:
    """Run the main application loop.
    
    Args:
        draw: The draw function to call each frame.
        model: The Model instance to render to.
        target_fps: Target frames per second.
        title: Window title (used for save filename).
    """
    frame_timer = _FrameTimer(target_fps)
    frame_count = 0
    running = True
    
    while running:
        # Handle input and system events
        running = _handle_input_events(title)
        if not running:
            break
            
        # Update timing
        delta_ms = frame_timer.update()
        
        # Render frame
        _render_frame(draw, model, frame_count, delta_ms)
        
        frame_count += 1
        
        # Control frame rate
        frame_timer.limit_frame_rate()


def _handle_input_events(title: str) -> bool:
    """Handle input events and return whether to continue running.
    
    Args:
        title: Window title (used for save filename).
    
    Returns:
        True if the application should continue running, False to quit.
    """
    input_state = controller.handle_input()
    
    if input_state["quit"]:
        return False
        
    if input_state["save"]:
        _handle_save_request(title)
        
    return True


def _handle_save_request(title: str) -> None:
    """Handle save canvas request.
    
    Args:
        title: The title to use as the base filename.
    """
    try:
        filepath = view.save_canvas_to_png(filename=title)
        print(f"Image saved successfully to: {filepath}")
    except Exception as e:
        print(f"Error saving image: {e}")


def _render_frame(
    draw: Callable[[Model, int, float], None],
    model: Model,
    frame_count: int,
    delta_ms: float,
) -> None:
    """Render a single frame.
    
    Args:
        draw: The draw function to call.
        model: The Model instance to render to.
        frame_count: Current frame number.
        delta_ms: Time elapsed since last frame in milliseconds.
    """
    view.begin_frame()
    
    # Only call draw() if looping is enabled
    if _loop_enabled:
        draw(model, frame_count, delta_ms)
        
    view.present_framebuffer(model.fb)
    view.end_frame()


class _FrameTimer:
    """Helper class to manage frame timing and rate limiting.
    
    Attributes:
        frame_time: Target time per frame in seconds.
        last_time: Timestamp of the last frame update.
    """
    
    def __init__(self, target_fps: int) -> None:
        """Initialize the frame timer.
        
        Args:
            target_fps: Target frames per second.
        """
        self.frame_time: float = 1.0 / target_fps
        self.last_time: float = time.perf_counter()
        
    def update(self) -> float:
        """Update timing and return delta time in milliseconds.
        
        Returns:
            Time elapsed since last update in milliseconds.
        """
        now = time.perf_counter()
        delta_ms = (now - self.last_time) * 1000.0
        self.last_time = now
        return delta_ms
        
    def limit_frame_rate(self) -> None:
        """Sleep if necessary to maintain target frame rate."""
        elapsed = time.perf_counter() - self.last_time
        sleep_for = self.frame_time - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)