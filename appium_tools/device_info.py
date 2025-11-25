"""Device information tools for Appium."""

from langchain.tools import tool


@tool
def get_device_info() -> str:
    """Get comprehensive device information including model, Android version, display, battery, etc.
    
    Returns:
        A formatted string containing device information, or an error message
    """
    from .session import driver
    if driver:
        try:
            def shell(cmd, *args):
                result = driver.execute_script("mobile: shell", {
                    "command": cmd,
                    "args": list(args)
                })
                # Handle both dict and string responses
                if isinstance(result, dict):
                    return result.get("stdout", "").strip() if "stdout" in result else str(result)
                else:
                    return str(result).strip()

            info = {
                "model": shell("getprop", "ro.product.model"),
                "brand": shell("getprop", "ro.product.brand"),
                "device_name": shell("getprop", "ro.product.name"),
                "android_version": shell("getprop", "ro.build.version.release"),
                "sdk": shell("getprop", "ro.build.version.sdk"),
                "display_resolution": shell("wm", "size"),
                "density": shell("wm", "density"),
                "battery": shell("dumpsys", "battery"),
                "current_package": driver.current_package,
                "current_activity": driver.current_activity,
                "orientation": driver.orientation,
                "is_locked": driver.is_locked(),
            }
            
            output = "Device Information:\n"
            output += f"Model: {info['model']}\n"
            output += f"Brand: {info['brand']}\n"
            output += f"Device Name: {info['device_name']}\n"
            output += f"Android Version: {info['android_version']}\n"
            output += f"SDK: {info['sdk']}\n"
            output += f"Display: {info['display_resolution']}\n"
            output += f"Density: {info['density']}\n"
            output += f"Current Package: {info['current_package']}\n"
            output += f"Current Activity: {info['current_activity']}\n"
            output += f"Orientation: {info['orientation']}\n"
            output += f"Is Locked: {info['is_locked']}\n"
            output += f"Battery Info:\n{info['battery']}\n"
            
            print(f"Retrieved device information: {output}")
            return output
        except Exception as e:
            return f"Failed to get device info: {e}"
    else:
        return "Driver is not initialized"


@tool
def is_locked() -> str:
    """Check if the device screen is locked.
    
    Returns:
        A message indicating whether the device is locked or not
    """
    from .session import driver
    if driver:
        try:
            locked = driver.is_locked()
            print(f"Device locked status: {locked}")
            return f"Device is {'locked' if locked else 'unlocked'}"
        except Exception as e:
            return f"Failed to check lock status: {e}"
    else:
        return "Driver is not initialized"


@tool
def get_orientation() -> str:
    """Get the current screen orientation.
    
    Returns:
        The current orientation (PORTRAIT or LANDSCAPE)
    """
    from .session import driver
    if driver:
        try:
            orientation = driver.orientation
            print(f"Current orientation: {orientation}")
            return f"Current orientation: {orientation}"
        except Exception as e:
            return f"Failed to get orientation: {e}"
    else:
        return "Driver is not initialized"


@tool
def set_orientation(orientation: str) -> str:
    """Set the screen orientation.
    
    Args:
        orientation: The desired orientation - "PORTRAIT" or "LANDSCAPE"
        
    Returns:
        A message indicating success or failure
    """
    from .session import driver
    if driver:
        try:
            if orientation.upper() not in ["PORTRAIT", "LANDSCAPE"]:
                return "Invalid orientation. Use 'PORTRAIT' or 'LANDSCAPE'"
            
            driver.orientation = orientation.upper()
            print(f"Set orientation to: {orientation}")
            return f"Successfully set orientation to: {orientation}"
        except Exception as e:
            return f"Failed to set orientation: {e}"
    else:
        return "Driver is not initialized"
