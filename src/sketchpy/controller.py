from . import view
import pygame

def handle_input():
    ev = view.poll_events()
    if ev["QUIT"] or pygame.K_ESCAPE in ev["KEYDOWN"]:
        return {"quit": True}
    return {"quit": False}