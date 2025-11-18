from kanvas import run
import math

def setup(model):
    model.clear(0)

def draw(model, frame, dt):
    model.clear(0)

    mid_y = model.h // 2
    offset = int(20 * math.sin(frame * 0.1))

    # A yellow horizontal line that sways up and down
    model.line(
        0, 
        mid_y, 
        model.w, 
        mid_y + offset, 
        255, 255, 0,   # yellow
    )

run(setup, draw, size=(640, 360), title="Oscillating Line Demo")
