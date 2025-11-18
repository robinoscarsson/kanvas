from kanvas import run
import math

def setup(model):
    model.clear(0)

def draw(model, frame, dt):
    model.clear(0)

    cx = model.w // 2
    cy = model.h // 2

    # Orbit (radius)
    radius = 80

    # Calculate a position that moves in a circle
    x = cx + int(radius * math.cos(frame * 0.05))
    y = cy + int(radius * math.sin(frame * 0.05))

    # Draw a small cyan dot
    model.circle(x, y, 10, 0, 200, 255)

    # Draw central point just for aesthetics
    model.circle(cx, cy, 3, 255, 255, 255)

run(setup, draw, size=(640, 360), title="Orbiting Circle Demo")
