from kanvas import run

def setup(model):
    model.clear(0)

def draw(model, frame, dt):
    model.clear(0)
    model.line(10, 10, model.w - 10, model.h - 10, 255, 255, 255)
    model.rect(20, 20, 100, 60, 255, 0, 0, fill=False)
    model.circle(model.w // 2, model.h // 2, 50, 0, 255, 0, fill=False)

run(setup, draw, size=(400, 300), title="Shapes Demo")