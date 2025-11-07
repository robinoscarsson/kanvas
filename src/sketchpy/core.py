import time

from . import view, controller

def run(setup, draw, target_fps=60, size=(640, 360), title="SketchPy"):
    view.create_window(*size, title=title)

    setup()

    running = True
    last = time.perf_counter()
    frameCount = 0
    frame_time = 1.0 / target_fps

    while running:
        input_state = controller.handle_input()
        if input_state["quit"]:
            running = False

        now = time.perf_counter()
        delta_ms = (now - last) * 1000.0
        last = now

        view.begin_frame()
        draw(frameCount, delta_ms)   # callback
        view.end_frame()

        frameCount += 1

        # enkel frame cap
        elapsed = time.perf_counter() - now
        sleep_for = frame_time - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)

    view.shutdown()