"""
Entry point for running Kanvas as a module: python -m kanvas

Provides a simple demo or help information.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    """Main entry point for the kanvas CLI."""
    parser = argparse.ArgumentParser(
        prog="kanvas",
        description="Kanvas - A minimalist creative-coding toolkit for Python",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a simple demo sketch",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information",
    )
    
    args = parser.parse_args()
    
    if args.version:
        from kanvas import __version__
        print(f"kanvas {__version__}")
        return 0
    
    if args.demo:
        _run_demo()
        return 0
    
    # Default: show help
    parser.print_help()
    return 0


def _run_demo() -> None:
    """Run a simple demo sketch showing basic Kanvas features."""
    from kanvas import run, Model
    import math
    
    def setup(model: Model) -> None:
        model.clear(30, 30, 40)
    
    def draw(model: Model, frame: int, dt: float) -> None:
        model.clear(30, 30, 40)
        
        # Draw animated circles
        cx, cy = model.w // 2, model.h // 2
        for i in range(5):
            angle = frame * 0.02 + i * (2 * math.pi / 5)
            x = int(cx + math.cos(angle) * 80)
            y = int(cy + math.sin(angle) * 80)
            r = int(127 + 127 * math.sin(frame * 0.05 + i))
            g = int(127 + 127 * math.sin(frame * 0.05 + i + 2))
            b = int(127 + 127 * math.sin(frame * 0.05 + i + 4))
            model.circle(x, y, 30, r, g, b, fill=True)
        
        # Draw center circle
        model.circle(cx, cy, 20, 255, 255, 255, fill=True)
    
    run(setup, draw, size=(400, 400), title="Kanvas Demo")


if __name__ == "__main__":
    sys.exit(main())