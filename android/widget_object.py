import uiautomator2 as u2

TAG = '[WIDGET OBJECT]'
def _log(msg: str, tag=TAG) -> None:
    print(f'[{tag}] | {msg}')

    
class Widget:
    """Represents an interactive UI widget and provides methods to interact with it."""
    def __init__(self, ui_object: u2.UiObject, raw_attributes: dict[str, any]):
        self.ui_object = ui_object
        self.raw_attributes = raw_attributes
        self.text: str | None = raw_attributes.get('text')
        self.resource_id: str | None = raw_attributes.get('resourceId') or raw_attributes.get('resource-id')
        self.content_description: str | None = raw_attributes.get('content-desc')
        self.class_name: str | None = raw_attributes.get('class')
        self.bounds: str | None = raw_attributes.get('bounds')
        self.clickable: bool = raw_attributes.get('clickable') == 'true'
        self.long_clickable: bool = raw_attributes.get('long-clickable') == 'true'
        self.checkable: bool = raw_attributes.get('checkable') == 'true'
        self.scrollable: bool = raw_attributes.get('scrollable') == 'true'
        self.is_password: bool = raw_attributes.get('password') == 'true'

    def __repr__(self) -> str:
        return (f"Widget(text='{self.text}', resource_id='{self.resource_id}', "
                f"content_description='{self.content_description}', class_name='{self.class_name}')")

    def tap(self) -> None:
        """Taps on this widget."""
        _log(f"Tapping on widget: {self}")
        self.ui_object.click()

    def type_text(self, text: str) -> None:
        """Types text into this widget."""
        _log(f"Typing '{text}' into widget: {self}")
        self.ui_object.set_text(text)
