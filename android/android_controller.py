import time
import xml.etree.ElementTree as ET
import uiautomator2 as u2
import os
import zipfile
import tempfile
from android.widget_object import Widget

TAG = '[UIAUTOMATOR2]'


def _log(msg: str, tag=TAG) -> None:
    print(f'[{tag}] | {msg}')

class Uiautomator2Interface:
    """A client for interacting with an Android device using uiautomator2."""

    def __init__(self, serial: str | None = None, setup: bool = False):
        """
        Initializes the uiautomator2 client and connects to the device.

        Args:
            serial (Optional[str]): The device serial number. If None, connects to the default device.
            setup (bool): If True, performs an initial setup on the device.
        """
        _log('Connecting to the Android device...')
        self.device = u2.connect(serial)
        if setup:
            self._initial_setup()
    
    def _press_back(self):
        """
        Press Back (should be a new class method in future)
        """
        self.device.press("back")

    def _initial_setup(self) -> None:
        """Performs initial setup on the device, like closing recent apps."""
        _log('Performing initial Android setup...')
        try:
            self.device.press('recent')
            time.sleep(1)
            w = self.device(text='Close all')
            if w.exists:
                w.click(5)
            self.device.press('home')
        except Exception as e:
            _log(f"[WARNING] Initial setup failed, pressing home. Error: {e}")
            self.device.press('home')

    def find_widget(self, widget_info: dict = None) -> Widget | None:
        """
        Finds a widget on the screen using uiautomator2 selectors.

        This method leverages uiautomator2's powerful selector engine to find a
        widget directly, which is more efficient than iterating through all widgets.
        If multiple widgets match the criteria, it returns the first one.

        Args:
            widget_info (dict, optional): A dictionary of selectors.
                                          Keys should match uiautomator2's selector arguments
                                          (e.g., 'text', 'resourceId', 'description').
            **kwargs: Alternatively, selectors can be passed as keyword arguments.

        Returns:
            Widget | None: A Widget object for the found element, or None if not found.
        """
        selector = {}
        if isinstance(widget_info, dict):
            selector = widget_info.copy()
        

        if 'content_description' in selector:
            selector['description'] = selector.pop('content_description')
        if 'resource_id' in selector:
            selector['resourceId'] = selector.pop('resource_id')
        if 'class_name' in selector:
            selector.pop('class_name')

        _log(f"Finding widget with selector: {selector}")
        widget_ui_object = self.device(**selector)

        if not widget_ui_object.exists:
            _log(f"[WARNING] Widget not found with selector: {selector}")
            return None

        info = widget_ui_object.info
        _log(f"Found widget with info: {info}")
        return Widget(ui_object=widget_ui_object, raw_attributes=info)

    def open_app_tray(self) -> None:
        """Opens the app tray by swiping up from the bottom of the screen."""
        _log("Opening app tray...")
        self.device.press("home")
        self.swipe_screen('up')

    def swipe_screen(self, direction: str) -> None:
        """
        Performs a swipe action on the screen.

        Args:
            direction (str): The direction to swipe ('up', 'down', 'left', 'right').
        """
        _log(f"Swiping screen {direction}")
        width, height = self.device.window_size()
        x_center = width / 2
        y_center = height / 2

        # Define swipe coordinates based on direction
        # Swiping 'up' means scrolling content up (finger moves from bottom to top)
        if direction.lower() == 'up':
            self.device.swipe(x_center, y_center * 1.5, x_center, y_center * 0.5)
        elif direction.lower() == 'down':
            self.device.swipe(x_center, y_center * 0.5, x_center, y_center * 1.5)
        elif direction.lower() == 'left':
            self.device.swipe(width * 0.8, y_center, width * 0.2, y_center)
        elif direction.lower() == 'right':
            self.device.swipe(width * 0.2, y_center, width * 0.8, y_center)
        else:
            _log(f"[WARNING] Invalid swipe direction: {direction}")

    def get_current_activity(self) -> str | None:
        """Gets the current foreground activity."""
        _log("Getting current activity...")
        try:
            current_app = self.device.app_current()
            return current_app.get('activity')
        except Exception as e:
            _log(f"[ERROR] Failed to get current activity: {e}")
            return None

    def search_for_app_via_app_tray(self, app_name: str) -> None:
        """
        Opens the app tray, searches for an app, and taps on it.

        Args:
            app_name (str): The name of the app to search for.
        """
        _log(f"Searching for and tapping app: {app_name}")
        self.open_app_tray()

        # Tap on the search bar (common resource IDs for Samsung and Pixel)
        # com.sec.android.app.launcher:id/search_src_text
        search_bar_info = {'resource_id': 'com.sec.android.app.launcher:id/app_search_edit_text_wrapper'}
        search_src_info = {'resource_id': 'com.sec.android.app.launcher:id/search_src_text'}
        search_bar_widget = self.find_widget(search_bar_info)
        if search_bar_widget:
            search_bar_widget.tap()
            time.sleep(0.5)
            search_src_widget = self.find_widget(search_src_info)
            search_src_widget.tap()
            time.sleep(0.5)
            search_src_widget.type_text(text=app_name)
            time.sleep(0.5)
            self.device.press("back")


    def get_interactive_widgets(self) -> list[Widget]:
        """
        Parses the screen's XML hierarchy to find all interactive widgets.

        Interactive widgets are determined by attributes like 'clickable',
        'long-clickable', 'checkable', and 'scrollable'.

        Returns:
            A list of Widget objects, where each object represents an
            interactive widget and contains its key attributes.
        """
        _log("Getting screen hierarchy to find interactive widgets...")
        try:
            xml_hierarchy = self.device.dump_hierarchy()
            root = ET.fromstring(xml_hierarchy)
            interactive_widgets = []

            for elem in root.iter('node'):
                attributes = elem.attrib
                is_interactive = (
                    attributes.get('clickable') == 'true' or
                    attributes.get('long-clickable') == 'true' or
                    attributes.get('checkable') == 'true' or
                    attributes.get('scrollable') == 'true'
                
                )
                is_visible = (attributes.get('visible-to-user') == 'true' and attributes.get('enabled') == 'true')
                is_with_text_descrip = (attributes.get('text') != '' or attributes.get('content-desc') != '')

                if (is_interactive or is_visible) and is_with_text_descrip:
                    ui_object = self.device(**{k: v for k, v in attributes.items() if k in ['text', 'resourceId', 'description', 'className'] and v})
                    widget = Widget(ui_object=ui_object, raw_attributes=attributes)
                    interactive_widgets.append(widget)

            _log(f"Found {len(interactive_widgets)} interactive widgets.")
            return interactive_widgets
        except Exception as e:
            _log(f"[ERROR] Failed to get and parse interactive widgets: {e}")
            return []

    def take_screenshot_and_dump_ui(self, filename_prefix: str = "screen_capture") -> str | None:
        """
        Takes a screenshot and dumps the UI hierarchy, then zips them into a single file.

        Args:
            filename_prefix (str): A prefix for the output filenames.

        Returns:
            str | None: The path to the created zip file, or None if an error occurred.
        """
        _log("Taking screenshot and dumping UI hierarchy...")
        temp_dir = None
        t = time.time()
        try:
            temp_dir = tempfile.mkdtemp()
            
            screenshot_file_path = os.path.join(temp_dir, f"{filename_prefix}.png")
            ui_dump_file_path = os.path.join(temp_dir, f"{filename_prefix}.xml")
            zip_output_path = f"{filename_prefix}_{t}.zip"

            pil_image = self.device.screenshot()
            if pil_image:
                pil_image.save(screenshot_file_path)
            else:
                _log("[WARNING] Screenshot capture returned None.")
                return None\

            xml_dump_content = self.device.dump_hierarchy()
            with open(ui_dump_file_path, 'w', encoding='utf-8') as f:
                f.write(xml_dump_content)

            with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(screenshot_file_path, os.path.basename(screenshot_file_path))
                zf.write(ui_dump_file_path, os.path.basename(ui_dump_file_path))

            zip_output_path = f"{temp_dir}/{zip_output_path}"
            _log(f"Screenshot and UI dump zipped to: {zip_output_path}")
            return zip_output_path

        except Exception as e:
            _log(f"[ERROR] Failed to capture screenshot and UI dump: {e}")
            return None


if __name__ == '__main__':
    from pprint import pprint as pp
    uii = Uiautomator2Interface()
    #uii.find_widget({'text': 'Agenda'}).tap()
#    pp(uii.get_interactive_widgets())
    zip_file = uii.take_screenshot_and_dump_ui("test_capture")
    if zip_file:
        _log(f"Generated zip file: {zip_file}")
