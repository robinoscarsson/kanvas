import math
from kanvas import run

def setup(model):
    # Runs once at the beginning
    model.clear(0)  # black background

def draw(model, frame, dt):
    # Clear the background each frame
    model.clear(0)

    # Starting point for the trunk (bottom center of screen)
    start_x = model.w // 2
    start_y = model.h - 10

    # Base length of the trunk
    base_length = model.h // 3

    # Base angle: -90° (upward)
    base_angle = -math.pi / 2

    # Slight sway in the tree based on frame → the fractal "breathes"
    sway = 0.3 * math.sin(frame * 0.03)

    # Draw the tree
    draw_branch(
        model,
        start_x,
        start_y,
        base_length,
        base_angle + sway,
        depth=8,  # try 7–10 for different levels of detail
    )

def draw_branch(model, x, y, length, angle, depth):
    """Draws a branch and calls itself recursively for two new branches."""
    if depth <= 0 or length < 2:
        return

    # Calculate the end point of the branch
    x2 = x + int(math.cos(angle) * length)
    y2 = y + int(math.sin(angle) * length)

    # Color can depend on depth:
    # deeper levels = darker (trunk), shallow levels = greener (leaves)
    t = depth  # just to make the formula readable
    r = min(200, 40 + t * 15)
    g = min(255, 80 + (8 - t) * 25)
    b = 40

    model.line(x, y, x2, y2, r, g, b)

    # Next branch length
    next_length = int(length * 0.7)

    # Branching angle
    branch_angle = 0.6  # radians (~34°)

    # Left and right branch
    draw_branch(model, x2, y2, next_length, angle - branch_angle, depth - 1)
    draw_branch(model, x2, y2, next_length, angle + branch_angle, depth - 1)

# Run the sketch
if __name__ == "__main__":
    run(
        setup,
        draw,
        size=(640, 480),
        title="kanvas – Fractal Tree",
        target_fps=60,
    )
