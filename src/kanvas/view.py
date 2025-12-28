"""View module for the Kanvas graphics framework.

This module handles all display and rendering operations using pygame.
It provides functions for window management, framebuffer presentation,
event polling, and image saving.

Key functions:
    - create_window(): Initialize the display window
    - present_framebuffer(): Display a numpy array on screen
    - begin_frame()/end_frame(): Frame lifecycle management
    - poll_events(): Get input events from pygame
    - save_canvas_to_png(): Save the current canvas to a file
    - shutdown(): Clean up pygame resources

The module maintains internal state for the screen and canvas surfaces,
which are initialized by create_window() and used by other functions.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import numpy as np
import numpy.typing as npt
import pygame
import pygame.surfarray as sarr

_screen: pygame.Surface | None = None
_canvas: pygame.Surface | None = None

def create_window(width: int, height: int, title: str) -> None:
    """Create and initialize a pygame window with rendering surfaces.
    
    Initializes pygame, creates a display window with the specified dimensions,
    sets the window title, and creates both screen and canvas surfaces for rendering.
    The screen surface is the main display window, while the canvas surface is used
    for off-screen rendering before blitting to the screen.
    
    Args:
        width (int): The width of the window in pixels.
        height (int): The height of the window in pixels.
        title (str): The title to display in the window's title bar.
    """
    pygame.init()
    global _screen, _canvas
    _screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    _canvas = pygame.Surface((width, height))

def present_framebuffer(np_fb: npt.NDArray[np.uint8]) -> None:
    """Present a numpy framebuffer to the screen.
    
    Takes a numpy array representing pixel data and displays it on screen.
    The function first copies the numpy array pixels to the canvas surface,
    then blits the canvas to the main screen surface for display.
    
    Args:
        np_fb: A numpy array containing pixel data to be displayed.
               Should match the dimensions of the window created by create_window().
    """
    sarr.blit_array(_canvas, np_fb)
    _screen.blit(_canvas, (0, 0))

def begin_frame() -> None:
    """Begin a new frame for rendering.
    
    Pumps the pygame event queue to keep the window responsive.
    This should be called at the beginning of each frame in the main loop.
    """
    pass  # pygame.event.pump() is not strictly necessary here

def end_frame() -> None:
    """End the current frame and update the display.
    
    Flips the display buffer to show the rendered frame on screen.
    This should be called at the end of each frame in the main loop.
    """
    pygame.display.flip()

def poll_events() -> dict[str, bool | list[int]]:
    """Poll for pygame events and return them in a structured format.
    
    Retrieves all pending pygame events and organizes them into a dictionary
    containing quit events, key press events, and key release events.
    
    Returns:
        A dictionary containing event information with the following structure:
            - "QUIT" (bool): True if a quit event was detected, False otherwise
            - "KEYDOWN" (list[int]): List of pygame key codes for keys pressed this frame
            - "KEYUP" (list[int]): List of pygame key codes for keys released this frame
    """
    events = pygame.event.get()
    event_dict: dict[str, bool | list[int]] = {"QUIT": False, "KEYDOWN": [], "KEYUP": []}
    for event in events:
        if event.type == pygame.QUIT:
            event_dict["QUIT"] = True
        elif event.type == pygame.KEYDOWN:
            event_dict["KEYDOWN"].append(event.key)
        elif event.type == pygame.KEYUP:
            event_dict["KEYUP"].append(event.key)
    return event_dict

def save_canvas_to_png(filename: str | None = None) -> str:
    """Save the current canvas to a PNG file.
    
    Saves the current state of the canvas surface to a PNG image file.
    If no filename is provided, generates a timestamped filename automatically.
    
    Args:
        filename (str, optional): The filename to save to. If None, generates
                                a timestamped filename like "kanvas_YYYYMMDD_HHMMSS.png".
    
    Returns:
        str: The actual filename that was used for saving.
    
    Raises:
        pygame.error: If there's an error saving the surface.
        OSError: If there's an error creating directories or writing the file.
    """
    global _canvas
    
    if _canvas is None:
        raise RuntimeError("No canvas available to save. Call create_window() first.")
    
    # Generate filename if not provided
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if filename is None:
        filename = f"kanvas_{timestamp}.png"
    else:
        filename = f"{filename}_{timestamp}.png"

    
    # Create output directory in the current working directory
    # This works whether kanvas is installed from PyPI or used locally
    output_dir = os.path.join(os.getcwd(), "output")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Full path for the file
    filepath = os.path.join(output_dir, filename)
    
    # Save the canvas surface
    pygame.image.save(_canvas, filepath)
    
    return filepath

def shutdown() -> None:
    """Shutdown pygame and clean up resources.
    
    Properly closes pygame and releases all associated resources.
    This should be called when the application is terminating.
    """
    pygame.quit()