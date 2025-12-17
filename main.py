import time
import re
from ast import literal_eval
from android.android_controller import Uiautomator2Interface, Widget
from pprint import pformat
from gemini_api.main import GeminiClient
from dataclasses import dataclass, field
import os
import shutil


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


TAG = "[MAIN] | "


def _log(msg: str, tag=TAG) -> None:
    print(f"{tag} {msg}")


def main():
    gemini_client = GeminiClient()
    android_client = Uiautomator2Interface()

    action_prompt_template = (
        """
Acessibility describe with app screen is this one and with action can be perform, with paths can navigate based on the widgets and activity information; Return only a tuple like ('JsonLike of selected Widget with attributes', 'action to do in the widget') to be able to help reach the goal and if you think the task is completed return 'None'.
User Goal: {user_goal}
Current Screen Widgets: {screen_widgets}
Current Android Activity: {android_activity}
        """
    )

    hunter_prompt_tempalte = (
        """
Based on the android information provided, explore the current open app with paths can navigate based on the widgets and activity information, also try tap in toogle non navigation widgets buttons; Return only a tuple like ('JsonLike of selected Widget with attributes', 'action to do in the widget') to be able to perform your choosed action. Use the history to change your idea when the same action did not work
User Goal: {user_goal}
Current Screen Widgets: {screen_widgets}
Current Android Activity: {android_activity}
    """
    )

    TIME_BETWEEN_STEPS = 5
    MAX_STEPS = 20
    LOST_TRACK_LIMIT = 3

    user_input = input(">>>> ")# "open the Contatos app, find the 'Dummy' contact and make a call"#"open the calculator and do 11 plus 34" #  #"open the calculator and do 10 plus 10"  # "Open the Play Store and install 'Clash of Clans' game"#"Play the playlist 'JJ' in Spotify" # input("What action do you want to do? > ")
    android_captures = []
    lost_track = 0
    PROMPT = action_prompt_template if user_input else hunter_prompt_tempalte

    if user_input:
        prompt_response = gemini_client.generate_text(
            f"Interpret and find the 'app' name to be open and perform the action in the current input: {user_input}. return only the app name (if need translete to portuguese-brasil camelcase) as a single string no other information or content."
        )
        app_name = prompt_response
        if "config" in app_name.lower():
            app_name = "Config."
        _log(app_name)

        android_client.search_for_app_via_app_tray(app_name)
        time.sleep(0.5)
        app_icon = android_client.find_widget(
            {"text": app_name, "resource_id": "com.sec.android.app.launcher:id/label"}
        )
        app_icon.tap()

    _log("1. Initialize Session Context")
    session = SessionContext(user_goal=user_input)

    _log("2. Start the execution loop")
    time.sleep(1)
    android_captures.append(android_client.take_screenshot_and_dump_ui())

    for i in range(MAX_STEPS):
        _log(f"===== STEP {i + 1}/{MAX_STEPS} =====")
        step_start_time = time.time()
        available_widgets = android_client.get_interactive_widgets()
        current_android_activity = android_client.get_current_activity()
        session.update_context(
            available_widgets,
            current_android_activity,
        )
        current_prompt = PROMPT.format(
            user_goal=session.user_goal,
            screen_widgets=pformat(session.current_screen_context),
            android_activity=session.current_activity,
        )

        session.history.append({"role": "user", "parts": [current_prompt]})

        prompt_response = gemini_client.create_chat_completion(
            session.history
        )

        session.history.append({"role": "model", "parts": [prompt_response]})

        prompt_response_literal = literal_eval(prompt_response)
        if prompt_response_literal and isinstance(prompt_response_literal, tuple):
            try:
                widget_attributes = literal_eval(prompt_response_literal[0])
            except ValueError:
                widget_attributes = prompt_response_literal[0] if isinstance(prompt_response_literal[0], dict) else None
            widget_action = prompt_response_literal[1]
        else:
            # No valid reponse from the API. Probably reach the goal.
            break

        if widget_attributes:
            if "tap" == widget_action or "click" == widget_action:
                _log(f'Widget to be pressed: {widget_attributes}')
                tap_widget = android_client.find_widget(widget_attributes)
                tap_widget.tap()
            if "type" in widget_action:
                _log(f'Type Action: {widget_attributes}')
                re_pattern = r"type (.+)"
                match = re.match(re_pattern, widget_action)
                if match:
                    content_to_type = match.group(1)
                type_widget = android_client.find_widget(widget_attributes)
                type_widget.type_text(content_to_type)
                android_client._press_back()
        else:
            _log('[WARNING] No widget to performa action')
            lost_track += 1
            if lost_track == LOST_TRACK_LIMIT:
                break

        android_captures.append(android_client.take_screenshot_and_dump_ui())
        step_end_time = time.time()
        _log(f"Step {i + 1} took {step_end_time - step_start_time:.2f} seconds.")
        time.sleep(TIME_BETWEEN_STEPS)

if __name__ == "__main__":
    main()
