"""Laptop actions through pyautogui. Moving the mouse to a screen corner aborts (pyautogui fail-safe)."""


def run_laptop_action(action):
    import pyautogui
    pyautogui.FAILSAFE = True
    if action == "scroll_down":
        pyautogui.scroll(-400)
    elif action == "scroll_up":
        pyautogui.scroll(400)
    else:  # key combination like "ctrl+tab" or "alt+f4"
        pyautogui.hotkey(*action.split("+"))
