"""Controller module for the Kanvas graphics framework.

This module handles user input processing and translates raw pygame events
into application-level input states. It acts as the input layer in the
Model-View-Controller architecture.

Key functions:
    - handle_input(): Process events and return input state dictionary

The controller polls events from the view module and interprets them
as application commands (quit, save, etc.).
"""
from __future__ import annotations

import pygame

from . import view


def handle_input() -> dict[str, bool]:
    """Handle input events and return an input state dictionary.
    
    Processes pygame events and returns a dictionary with the current input state,
    including quit commands and save requests.
    
    Returns:
        Input state with the following keys:
            - "quit" (bool): True if the application should quit
            - "save" (bool): True if a save was requested (S key pressed)
    """
    ev = view.poll_events()
    input_state: dict[str, bool] = {"quit": False, "save": False}
    
    if ev["QUIT"] or pygame.K_ESCAPE in ev["KEYDOWN"]:  # type: ignore[operator]
        input_state["quit"] = True
    
    if pygame.K_s in ev["KEYDOWN"]:  # type: ignore[operator]
        input_state["save"] = True
    
    return input_state