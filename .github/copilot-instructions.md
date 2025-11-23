# kanvas - AI Coding Assistant Instructions

## Project Overview
kanvas is a minimalist creative-coding toolkit (~200 lines) inspired by Processing/p5.js. It provides a simple setup/draw loop for educational pixel art and animations using pygame + numpy.

## Architecture (Clean MVC Pattern)

### Core Flow: `run()` → MVC Components
- **Entry Point**: `run(setup_func, draw_func, **kwargs)` in `core.py`
- **Model**: `model.py` - Framebuffer (`numpy.ndarray`) with drawing primitives
- **View**: `view.py` - pygame window/rendering with `pygame.surfarray`  
- **Controller**: `controller.py` - Input handling (ESC=quit, S=save)

### Key Files & Responsibilities
```
src/kanvas/
├── core.py         # Main loop orchestration, frame timing, loop control
├── model.py        # Framebuffer + drawing API (pixel, line, rect, circle)
├── view.py         # pygame surface management, PNG export
├── controller.py   # Event handling (quit/save only)
└── __init__.py     # Public API exports
```

## Critical Patterns

### Drawing API Convention
All drawing methods follow: `model.method(coords..., r, g, b, **kwargs)`
- Bounds checking: `0 <= x < model.w and 0 <= y < model.h`
- RGB values: 0-255 integers
- Framebuffer access: `model.fb[x, y] = (r, g, b)` (numpy uint8 array)

### Loop Control Global State
- `_loop_enabled` flag controls draw() execution (not window responsiveness)
- Functions: `noLoop()`, `loop()`, `isLooping()` - Processing-like API
- Frame counting independent of loop state

### Example Structure Pattern
```python
from kanvas import run

def setup(model):
    model.clear(30)  # grayscale shorthand

def draw(model, frame, dt):
    # frame = int counter, dt = delta milliseconds
    pass

run(setup, draw, size=(800, 600), title="Demo")
```

## Development Workflows

### Local Development
```bash
pip install -e .          # Install in editable mode
python examples/fractal_tree.py  # Run examples directly
```

### Testing Drawing Functions
- Use `examples/` directory for testing new features
- Output saved to `./output/` with timestamps
- No formal test suite - visual validation approach

### Adding Drawing Primitives
1. Add method to `Model` class in `model.py`
2. Follow bounds checking pattern: `if 0 <= x < self.w and 0 <= y < self.h:`
3. Use existing primitives when possible (e.g., `rect()` uses `line()`)
4. Document parameters with RGB color convention

## Dependencies & Constraints

### Core Dependencies
- **pygame**: Window management, event handling, surface operations
- **numpy**: Framebuffer storage (`dtype=np.uint8`)
- Python 3.9+ requirement

### Performance Considerations
- Pixel-level operations - not optimized for high-frequency drawing
- Bresenham's algorithm for lines (`model.line()`)
- Simple circle drawing with distance calculations
- Target 60 FPS with `_FrameTimer` class

## Project Philosophy
- **Educational first**: Readable code over performance
- **Minimal surface area**: ~200 lines total, hackable
- **Processing-inspired**: Familiar setup/draw paradigm
- **No magic**: Explicit control flow, no hidden globals (except loop state)

Prefer simple, explicit implementations over complex optimizations. The goal is understanding, not feature parity with Processing.