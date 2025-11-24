"""Element interaction tools for Appium."""

from langchain.tools import tool


@tool
def find_element(by: str, value: str) -> str:
    """Find an element on the current screen using a locator strategy.
    
    Args:
        by: The locator strategy (e.g., "xpath", "id", "accessibility_id")
        value: The locator value to search for
        
    Returns:
        A message indicating success or failure of finding the element
    """
    from .session import driver
    if driver:
        try:
            element = driver.find_element(by=by, value=value)
            print(f"Found element {element} by {by} with value {value}")
            return f"Successfully found element by {by} with value {value}"
        except Exception as e:
            return f"Failed to find element: {e}"
    else:
        return "Driver is not initialized"


@tool
def click_element(by: str, value: str) -> str:
    """Find and click an element on the current screen.
    
    Args:
        by: The locator strategy (e.g., "xpath", "id", "accessibility_id")
        value: The locator value to search for
        
    Returns:
        A message indicating success or failure of clicking the element
    """
    from .session import driver
    if driver:
        try:
            element = driver.find_element(by=by, value=value)
            element.click()
            print(f"Clicked element by {by} with value {value}")
            return f"Successfully clicked on element by {by} with value {value}"
        except Exception as e:
            return f"Failed to click element: {e}"
    else:
        return "Driver is not initialized"


@tool
def get_text(by: str, value: str) -> str:
    """Get the text content of an element on the screen.
    
    Args:
        by: The locator strategy (e.g., "xpath", "id", "accessibility_id")
        value: The locator value to search for
        
    Returns:
        The text content of the element, or an error message
    """
    from .session import driver
    if driver:
        try:
            element = driver.find_element(by=by, value=value)
            text = element.text
            print(f"Got text '{text}' from element by {by} with value {value}")
            return f"Element text: {text}"
        except Exception as e:
            return f"Failed to get text: {e}"
    else:
        return "Driver is not initialized"


@tool
def set_value(by: str, value: str, text: str) -> str:
    """Set the value/text of an input element (like a text field).
    
    Args:
        by: The locator strategy (e.g., "xpath", "id", "accessibility_id")
        value: The locator value to search for the input element
        text: The text to set in the input element
        
    Returns:
        A message indicating success or failure of setting the value
    """
    from .session import driver
    if driver:
        try:
            element = driver.find_element(by=by, value=value)
            element.clear()
            element.send_keys(text)
            print(f"Set value '{text}' to element by {by} with value {value}")
            return f"Successfully set value '{text}' to element"
        except Exception as e:
            return f"Failed to set value: {e}"
    else:
        return "Driver is not initialized"


@tool
def press_keycode(keycode: int) -> str:
    """Press an Android keycode (e.g., back button, home button, etc.).
    
    Args:
        keycode: The Android keycode to press (e.g., 4 for BACK, 3 for HOME, 82 for MENU)
        
    Returns:
        A message indicating success or failure of pressing the keycode
        
    Common keycodes:
        3 = HOME
        4 = BACK
        82 = MENU
        66 = ENTER
        67 = DEL (backspace)
    """
    from .session import driver
    if driver:
        try:
            driver.press_keycode(keycode)
            print(f"Pressed keycode {keycode}")
            return f"Successfully pressed keycode {keycode}"
        except Exception as e:
            return f"Failed to press keycode: {e}"
    else:
        return "Driver is not initialized"


@tool
def double_tap(by: str, value: str) -> str:
    """Double tap on an element on the screen.
    
    Args:
        by: The locator strategy (e.g., "xpath", "id", "accessibility_id")
        value: The locator value to search for
        
    Returns:
        A message indicating success or failure of double tapping the element
    """
    from .session import driver
    if driver:
        try:
            element = driver.find_element(by=by, value=value)
            # Double tap using actions API
            from appium.webdriver.common.touch_action import TouchAction
            action = TouchAction(driver)
            action.tap(element).perform()
            action.tap(element).perform()
            print(f"Double tapped element by {by} with value {value}")
            return f"Successfully double tapped on element by {by} with value {value}"
        except Exception as e:
            return f"Failed to double tap element: {e}"
    else:
        return "Driver is not initialized"
