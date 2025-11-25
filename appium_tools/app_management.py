"""App management tools for Appium."""

from langchain.tools import tool


@tool
def get_current_app() -> str:
    """Get the package name and activity of the currently running app.
    
    Returns:
        The current app package and activity information, or an error message
    """
    from .session import driver
    if driver:
        try:
            current_package = driver.current_package
            current_activity = driver.current_activity
            print(f"🔧 Current app: {current_package}/{current_activity}")
            return f"Current app package: {current_package}\nCurrent activity: {current_activity}"
        except Exception as e:
            return f"Failed to get current app: {e}"
    else:
        return "Driver is not initialized"


@tool
def activate_app(app_id: str) -> str:
    """Activate (launch) an app by its package name.
    
    Args:
        app_id: The app package name to activate (e.g., "com.android.settings")
        
    Returns:
        A message indicating success or failure
    """
    from .session import driver
    if driver:
        try:
            driver.activate_app(app_id)
            print(f"🔧 Activated app: {app_id}")
            return f"Successfully activated app: {app_id}"
        except Exception as e:
            return f"Failed to activate app: {e}"
    else:
        return "Driver is not initialized"


@tool
def terminate_app(app_id: str) -> str:
    """Terminate (force stop) an app by its package name.
    
    Args:
        app_id: The app package name to terminate (e.g., "com.android.settings")
        
    Returns:
        A message indicating success or failure
    """
    from .session import driver
    if driver:
        try:
            result = driver.terminate_app(app_id)
            print(f"🔧 Terminated app: {app_id}, result: {result}")
            return f"Successfully terminated app: {app_id} (result: {result})"
        except Exception as e:
            return f"Failed to terminate app: {e}"
    else:
        return "Driver is not initialized"


@tool
def list_apps() -> str:
    """List all installed apps on the device.
    
    Returns:
        A list of installed app package names, or an error message
    """
    from .session import driver
    if driver:
        try:
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
            print(f"🔧 Found {len(package_list)} installed apps")
            print(f"🔧 Installed apps: {package_list}")
            return f"Installed apps ({len(package_list)}):\n" + "\n".join(package_list)
        except Exception as e:
            return f"Failed to list apps: {e}"
    else:
        return "Driver is not initialized"
