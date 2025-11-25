"""Appium tools for LangChain integration."""

from .session import appium_driver, get_driver_status
from .interaction import find_element, click_element, set_value, get_text, press_keycode, double_tap
from .navigation import take_screenshot, scroll_element, get_page_source, scroll_to_element
from .app_management import get_current_app, activate_app, terminate_app, list_apps
from .device_info import get_device_info, is_locked, get_orientation, set_orientation

__all__ = [
    # Session
    "appium_driver",
    "get_driver_status",
    # Interaction
    "find_element",
    "click_element",
    "set_value",
    "get_text",
    "press_keycode",
    "double_tap",
    # Navigation
    "take_screenshot",
    "scroll_element",
    "get_page_source",
    "scroll_to_element",
    # App Management
    "get_current_app",
    "activate_app",
    "terminate_app",
    "list_apps",
    # Device Info
    "get_device_info",
    "is_locked",
    "get_orientation",
    "set_orientation",
    # Main function
    "appium_tools",
]


def appium_tools():
    """LangChain エージェント用の全Appiumツールリストを返す。
    
    Returns:
        list: LangChain BaseTool のリスト（19個のAppium自動化ツール）
    """
    return [
        get_driver_status,
        find_element,
        click_element,
        set_value,
        get_text,
        press_keycode,
        double_tap,
        take_screenshot,
        scroll_element,
        get_page_source,
        scroll_to_element,
        get_current_app,
        activate_app,
        terminate_app,
        list_apps,
        get_device_info,
        is_locked,
        get_orientation,
        set_orientation,
    ]
