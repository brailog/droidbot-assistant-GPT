import time

import uiautomator2 as u2
from uiautomator2 import Device

TAG = '[UIAUTOMATOR2]'

from android import android_config

def _log(msg: str, tag=TAG) -> None:
    print(f'[{tag}] | {msg}')

def uiautomator2_connection(serial=None, setup=False) -> Device:
    _log('Connection with the Android device')
    device = u2.connect(serial)  # connect to device
    if setup:
        _log('Performing Android setup')
        try:
            device.press('recent')
            time.sleep(1)
            w = device(text='Close all')
            if w.exists:
                w.click(5)
            device.press('home')
        except:
            device.press('home')

    return device


def start_app(app_name: str) -> None:
    device = uiautomator2_connection()
    _log(f'Stating app: {app_name}')
    pkg = android_config.NAME_TO_PACKAGE.get(app_name)
    device.app_start(pkg)

def find_and_tap_widget(widget_info: dict) -> None:
    _log(f'Finding and tapping in the following widget: {widget_info}')
    text = widget_info.get('text') if widget_info.get('text') and widget_info.get('text') != "None" else None
    content_desc = widget_info.get('content_desc') if widget_info.get('content_desc') and widget_info.get('content_desc') != "None" else None
    resource_id = widget_info.get('resource_id') if widget_info.get('resource_id') and widget_info.get('resource_id') != "None" else None
    try:
        device = uiautomator2_connection()
        if content_desc and text:
            _log('Content and Text with ID')
            device(resourceId=resource_id, text=text, description=content_desc).click()
        elif content_desc:
            _log('Only Content with ID')
            device(resourceId=resource_id, description=content_desc).click()
        elif text:
            _log('Only text with ID')
            device(resourceId=resource_id, text=text).click()
        else:
            _log('Only ID')
            device(resourceId=resource_id).click()
    except:
        _log('[WARNING][BUGFIX] | Unable to find widget')

def type_input(text: str) -> None:
    device = uiautomator2_connection()
    device.shell(f'input text "{text}"')
    device.press('enter')


if __name__ == '__main__':
    pass