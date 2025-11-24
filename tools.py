from contextlib import asynccontextmanager
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from langchain.tools import tool

driver = None

@asynccontextmanager
async def appium_driver(options: UiAutomator2Options, appium_server_url: str = 'http://localhost:4723'):
    """Async context manager for initializing and managing the Appium driver.
    
    Args:
        options: UiAutomator2Options instance with driver configuration
        appium_server_url: URL of the Appium server (default: 'http://localhost:4723')
        
    Yields:
        The initialized webdriver instance
        
    Example:
        async with appium_driver(options) as driver:
            element = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Battery"]')
            element.click()
    """
    driver_instance = None
    try:
        driver_instance = webdriver.Remote(appium_server_url, options=options)
        global driver
        driver = driver_instance
        yield driver_instance
    finally:
        if driver_instance:
            driver_instance.quit()
            driver = None


@tool
def get_driver_status() -> str:
    """Get the current status of the Appium driver.
    
    Returns:
        A message indicating whether the driver is initialized or not
    """
    global driver
    if driver:
        return "Driver is initialized and ready"
    else:
        return "Driver is not initialized"


@tool
def find_element(by: str, value: str) -> str:
    """Find an element on the current screen using a locator strategy.
    
    Args:
        by: The locator strategy (e.g., "xpath", "id", "accessibility_id")
        value: The locator value to search for
        
    Returns:
        A message indicating success or failure of finding the element
    """
    global driver
    if driver:
        try:
            element = driver.find_element(by=by, value=value)
            print(f"Found element {element} by {by} with value {value}")
            return f"Successfully found element by {by} with value {value}"
        except Exception as e:
            return f"Failed to click element: {e}"
    else:
        return "Driver is not initialized"


@tool
def get_current_app() -> str:
    """Get the package name and activity of the currently running app.
    
    Returns:
        The current app package and activity information, or an error message
    """
    global driver
    if driver:
        try:
            current_package = driver.current_package
            current_activity = driver.current_activity
            print(f"Current app: {current_package}/{current_activity}")
            return f"Current app package: {current_package}\nCurrent activity: {current_activity}"
        except Exception as e:
            return f"Failed to get current app: {e}"
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
    global driver
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
    global driver
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
    global driver
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
def scroll_element(by: str, value: str, direction: str = "up") -> str:
    """Scroll within a scrollable element (like a list or scrollview).
    
    Args:
        by: The locator strategy (e.g., "xpath", "id", "accessibility_id")
        value: The locator value to find the scrollable element
        direction: Direction to scroll - "up", "down", "left", or "right" (default: "up")
        
    Returns:
        A message indicating success or failure of scrolling
        
    Examples:
        Scroll up in a list: scroll_element("id", "android:id/list", "up")
        Scroll down: scroll_element("xpath", "//*[@scrollable='true']", "down")
    """
    global driver
    if driver:
        try:
            element = driver.find_element(by=by, value=value)
            
            # Get element location and size
            location = element.location
            size = element.size
            
            # Calculate center point
            center_x = location['x'] + size['width'] // 2
            center_y = location['y'] + size['height'] // 2
            
            # Calculate swipe coordinates within the element
            if direction == "up":
                start_x = center_x
                start_y = location['y'] + size['height'] * 0.8
                end_x = center_x
                end_y = location['y'] + size['height'] * 0.2
            elif direction == "down":
                start_x = center_x
                start_y = location['y'] + size['height'] * 0.2
                end_x = center_x
                end_y = location['y'] + size['height'] * 0.8
            elif direction == "left":
                start_x = location['x'] + size['width'] * 0.8
                start_y = center_y
                end_x = location['x'] + size['width'] * 0.2
                end_y = center_y
            elif direction == "right":
                start_x = location['x'] + size['width'] * 0.2
                start_y = center_y
                end_x = location['x'] + size['width'] * 0.8
                end_y = center_y
            else:
                return f"Invalid direction: {direction}. Use 'up', 'down', 'left', or 'right'"
            
            # Perform swipe
            driver.swipe(int(start_x), int(start_y), int(end_x), int(end_y), 500)
            print(f"Scrolled {direction} in element found by {by} with value {value}")
            return f"Successfully scrolled {direction} in element"
        except Exception as e:
            return f"Failed to scroll element: {e}"
    else:
        return "Driver is not initialized"


@tool
def get_page_source() -> str:
    """Get the XML source of the current screen layout.
    
    Returns:
        The XML page source if successful, or an error message
    """
    global driver
    if driver:
        try:
            source = driver.page_source
            print(f"Page source retrieved successfully: {source}")
            return f"Page source retrieved successfully:\n{source}"
        except Exception as e:
            return f"Failed to get page source: {e}"
    else:
        return "Driver is not initialized"


@tool
def take_screenshot() -> str:
    """Take a screenshot of the current screen and return it as base64 string.
    
    Returns:
        The screenshot as a base64 encoded string that can be used by other tools, or an error message
    """
    global driver
    if driver:
        try:
            screenshot_base64 = driver.get_screenshot_as_base64()
            print("Screenshot taken successfully")
            return screenshot_base64
        except Exception as e:
            return f"Failed to take screenshot: {e}"
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
    global driver
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