from kanvas import run
import math

def setup(model):
    model.clear(0)

def draw(model, frame, dt):
    model.clear(0)

    mid_y = model.h // 2
    offset = int(20 * math.sin(frame * 0.1))

    # En gul horisontell linje som svajar upp och ner
    model.line(
        0, 
        mid_y, 
        model.w, 
        mid_y + offset, 
        255, 255, 0,   # gul
    )

run(setup, draw, size=(640, 360), title="Oscillating Line Demo")
