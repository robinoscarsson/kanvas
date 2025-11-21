import time

from . import view, controller
from .model import Model

# Global flag to control the draw loop
_loop_enabled = True

def noLoop():
    """Stop the draw loop from running.
    
    Similar to p5.js noLoop(), this stops the draw() function from being
    called repeatedly. The application will continue to respond to input
    but draw() will no longer be executed each frame.
    """
    global _loop_enabled
    _loop_enabled = False

def loop():
    """Resume the draw loop.
    
    Similar to p5.js loop(), this resumes calling the draw() function
    each frame after it was stopped with noLoop().
    """
    global _loop_enabled
    _loop_enabled = True

def isLooping():
    """Check if the draw loop is currently running.
    
    Returns:
        bool: True if draw() is being called each frame, False if stopped with noLoop()
    """
    return _loop_enabled

def run(setup, draw, target_fps=60, size=(640, 360), title="kanvas"):
    """Main application loop for kanvas.
    
    Args:
        setup: Function to call once at startup
        draw: Function to call each frame
        target_fps: Target frames per second (default: 60)
        size: Window size as (width, height) tuple (default: (640, 360))
        title: Window title (default: "kanvas")
    """
    # Initialize application
    model = _initialize_application(setup, size, title)
    
    # Run main loop
    _run_main_loop(draw, model, target_fps, title)
    
    # Clean up
    view.shutdown()


def _initialize_application(setup, size, title):
    """Initialize the application window and model."""
    view.create_window(*size, title=title)
    model = Model(size[0], size[1])
    setup(model)
    return model


def _run_main_loop(draw, model, target_fps, title):
    """Run the main application loop."""
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


def _handle_input_events(title):
    """Handle input events and return whether to continue running."""
    input_state = controller.handle_input()
    
    if input_state["quit"]:
        return False
        
    if input_state["save"]:
        _handle_save_request(title)
        
    return True


def _handle_save_request(title):
    """Handle save canvas request."""
    try:
        filepath = view.save_canvas_to_png(filename=title)
        print(f"Image saved successfully to: {filepath}")
    except Exception as e:
        print(f"Error saving image: {e}")


def _render_frame(draw, model, frame_count, delta_ms):
    """Render a single frame."""
    view.begin_frame()
    
    # Only call draw() if looping is enabled
    if _loop_enabled:
        draw(model, frame_count, delta_ms)
        
    view.present_framebuffer(model.fb)
    view.end_frame()


class _FrameTimer:
    """Helper class to manage frame timing and rate limiting."""
    
    def __init__(self, target_fps):
        self.frame_time = 1.0 / target_fps
        self.last_time = time.perf_counter()
        
    def update(self):
        """Update timing and return delta time in milliseconds."""
        now = time.perf_counter()
        delta_ms = (now - self.last_time) * 1000.0
        self.last_time = now
        return delta_ms
        
    def limit_frame_rate(self):
        """Sleep if necessary to maintain target frame rate."""
        elapsed = time.perf_counter() - self.last_time
        sleep_for = self.frame_time - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)