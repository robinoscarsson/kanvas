import pygame

def create_window(width: int, height: int, title: str) -> None:
    """Create and initialize a pygame window.
    
    Initializes pygame, creates a display window with the specified dimensions,
    and sets the window title.
    
    Args:
        width (int): The width of the window in pixels.
        height (int): The height of the window in pixels.
        title (str): The title to display in the window's title bar.
    """
    pygame.init()
    pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)

def begin_frame() -> None:
    """Begin a new frame for rendering.
    
    Pumps the pygame event queue to keep the window responsive.
    This should be called at the beginning of each frame in the main loop.
    """
    pygame.event.pump()

def end_frame() -> None:
    """End the current frame and update the display.
    
    Flips the display buffer to show the rendered frame on screen.
    This should be called at the end of each frame in the main loop.
    """
    pygame.display.flip()

def poll_events() -> dict:
    """Poll for pygame events and return them in a structured format.
    
    Retrieves all pending pygame events and organizes them into a dictionary
    containing quit events, key press events, and key release events.
    
    Returns:
        dict: A dictionary containing event information with the following structure:
            - "QUIT" (bool): True if a quit event was detected, False otherwise
            - "KEYDOWN" (list): List of pygame key codes for keys pressed this frame
            - "KEYUP" (list): List of pygame key codes for keys released this frame
    """
    events = pygame.event.get()
    event_dict = {"QUIT": False, "KEYDOWN": [], "KEYUP": []}
    for event in events:
        if event.type == pygame.QUIT:
            event_dict["QUIT"] = True
        elif event.type == pygame.KEYDOWN:
            event_dict["KEYDOWN"].append(event.key)
        elif event.type == pygame.KEYUP:
            event_dict["KEYUP"].append(event.key)
    return event_dict

def shutdown() -> None:
    """Shutdown pygame and clean up resources.
    
    Properly closes pygame and releases all associated resources.
    This should be called when the application is terminating.
    """
    pygame.quit()