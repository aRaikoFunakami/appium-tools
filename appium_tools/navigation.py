"""Navigation and screen inspection tools for Appium."""

import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def take_screenshot() -> str:
    """Take a screenshot of the current screen and return it as base64 string.
    
    Returns:
        The screenshot as a base64 encoded string that can be used by other tools, or an error message
    """
    from .session import driver
    if driver:
        try:
            screenshot_base64 = driver.get_screenshot_as_base64()
            logger.info("🔧 Screenshot taken successfully")
            return screenshot_base64
        except Exception as e:
            return f"Failed to take screenshot: {e}"
    else:
        return "Driver is not initialized"


@tool
def get_page_source() -> str:
    """Get the XML source of the current screen layout.
    
    Returns:
        The XML page source if successful, or an error message
    """
    from .session import driver
    if driver:
        try:
            source = driver.page_source
            logger.info(f"🔧 Page source retrieved successfully: {source[:100]}...")  # Print first 100 chars for brevity    
            return f"Page source retrieved successfully:\n{source}"
        except Exception as e:
            return f"Failed to get page source: {e}"
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
    from .session import driver
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
            logger.info(f"🔧 Scrolled {direction} in element found by {by} with value {value}")
            return f"Successfully scrolled {direction} in element"
        except Exception as e:
            return f"Failed to scroll element: {e}"
    else:
        return "Driver is not initialized"


@tool
def scroll_to_element(by: str, value: str, scrollable_by: str = "xpath", scrollable_value: str = "//*[@scrollable='true']") -> str:
    """Scroll within a scrollable container until an element is visible.
    
    Args:
        by: The locator strategy for the target element (e.g., "xpath", "id", "accessibility_id")
        value: The locator value for the target element
        scrollable_by: The locator strategy for the scrollable container (default: "xpath")
        scrollable_value: The locator value for the scrollable container (default: "//*[@scrollable='true']")
        
    Returns:
        A message indicating success or failure of scrolling to the element
    """
    from .session import driver
    if driver:
        try:
            # Try to find the element first
            max_scrolls = 10
            for i in range(max_scrolls):
                try:
                    element = driver.find_element(by=by, value=value)
                    if element.is_displayed():
                        logger.info(f"🔧 Found element by {by} with value {value} after {i} scrolls")
                        return f"Successfully scrolled to element by {by} with value {value}"
                except Exception:
                    pass
                
                # Scroll down
                scrollable = driver.find_element(by=scrollable_by, value=scrollable_value)
                location = scrollable.location
                size = scrollable.size
                center_x = location['x'] + size['width'] // 2
                start_y = location['y'] + size['height'] * 0.8
                end_y = location['y'] + size['height'] * 0.2
                driver.swipe(int(center_x), int(start_y), int(center_x), int(end_y), 500)
            
            return f"Failed to find element by {by} with value {value} after {max_scrolls} scrolls"
        except Exception as e:
            return f"Failed to scroll to element: {e}"
    else:
        return "Driver is not initialized"
