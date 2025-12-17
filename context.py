from dataclasses import dataclass, field
from android.android_controller import Widget


@dataclass
class SessionContext:
    """Keeps track of the session state."""
    user_goal: str
    current_screen_context: list[Widget] = field(default_factory=list)
    current_activity: str | None = None
    next_action: tuple[str, Widget | None] | None = None
    history: list[dict[str, str]] = field(default_factory=list)

    def update_context(self, widgets: list[Widget], activity: str | None):
        """Updates the session context with the latest screen widgets and activity."""
        self.current_screen_context = widgets
        self.current_activity = activity