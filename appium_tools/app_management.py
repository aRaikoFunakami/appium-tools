"""App management tools for Appium."""

import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_current_app() -> str:
    """Get the package name and activity of the currently running app.
    
    Returns:
        The current app package and activity information, or an error message
        
    Raises:
        ValueError: If driver is not initialized
        Exception: Any Appium-related exception
    """
    from .session import driver
    if not driver:
        raise ValueError("Driver is not initialized")
    
    current_package = driver.current_package
    current_activity = driver.current_activity
    logger.info(f"🔧 Current app: {current_package}/{current_activity}")
    return f"Current app package: {current_package}\nCurrent activity: {current_activity}"


@tool
def activate_app(app_id: str) -> str:
    """Activate (launch) an app by its package name.
    
    Args:
        app_id: The app package name to activate (e.g., "com.android.settings")
        
    Returns:
        A message indicating success or failure
        
    Raises:
        ValueError: If driver is not initialized
        Exception: Any Appium-related exception
    """
    from .session import driver
    if not driver:
        raise ValueError("Driver is not initialized")
    
    driver.activate_app(app_id)
    logger.info(f"🔧 Activated app: {app_id}")
    return f"Successfully activated app: {app_id}"


@tool
def terminate_app(app_id: str) -> str:
    """Terminate (force stop) an app by its package name.
    
    Args:
        app_id: The app package name to terminate (e.g., "com.android.settings")
        
    Returns:
        A message indicating success or failure
        
    Raises:
        ValueError: If driver is not initialized
        Exception: Any Appium-related exception
    """
    from .session import driver
    if not driver:
        raise ValueError("Driver is not initialized")
    
    result = driver.terminate_app(app_id)
    logger.info(f"🔧 Terminated app: {app_id}, result: {result}")
    return f"Successfully terminated app: {app_id} (result: {result})"


@tool
def list_apps() -> str:
    """List all installed apps on the device.
    
    Returns:
        A list of installed app package names, or an error message
        
    Raises:
        ValueError: If driver is not initialized
        Exception: Any Appium-related exception
    """
    from .session import driver
    if not driver:
        raise ValueError("Driver is not initialized")
    
    # Get list of installed packages using adb shell
    result = driver.execute_script("mobile: shell", {
        "command": "pm",
        "args": ["list", "packages"]
    })
    # Handle both dict and string responses
    if isinstance(result, dict):
        packages = result.get("stdout", "").strip()
    else:
        packages = str(result).strip()
    
    # Parse package names (format: "package:com.example.app")
    package_list = [line.replace("package:", "") for line in packages.split("\n") if line.startswith("package:")]
    logger.info(f"🔧 Found {len(package_list)} installed apps")
    logger.debug(f"🔧 Installed apps: {package_list}")
    return f"Installed apps ({len(package_list)}):\n" + "\n".join(package_list)
