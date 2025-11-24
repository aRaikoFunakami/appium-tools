import asyncio
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from tools import appium_driver

async def main():
    # Set up options
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'uiautomator2'
    options.device_name = 'Android'
    options.app_package = 'com.android.settings'
    options.app_activity = '.Settings'
    options.language = 'en'
    options.locale = 'US'
    
    try:
        async with appium_driver(options) as driver:
            # Find and click battery element
            el = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Battery"]')
            el.click()
            
            print("Successfully clicked on Battery")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(main())