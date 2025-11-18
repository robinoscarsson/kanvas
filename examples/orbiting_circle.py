from kanvas import run
import math

def setup(model):
    model.clear(0)

def draw(model, frame, dt):
    model.clear(0)

    cx = model.w // 2
    cy = model.h // 2

    # Bana (radie)
    radius = 80

    # Beräkna en position som rör sig i en cirkel
    x = cx + int(radius * math.cos(frame * 0.05))
    y = cy + int(radius * math.sin(frame * 0.05))

    # Rita en liten cyan prick
    model.circle(x, y, 10, 0, 200, 255)

    # Rita central punkt bara för estetiken
    model.circle(cx, cy, 3, 255, 255, 255)

run(setup, draw, size=(640, 360), title="Orbiting Circle Demo")
