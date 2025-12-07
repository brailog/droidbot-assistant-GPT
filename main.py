import time
import re
from ast import literal_eval
from android.android_controller import Uiautomator2Interface, Widget
from pprint import pformat
from gemini_api.main import GeminiClient
from gemini_api.main import GeminiClient # Assuming this is your Gemini API client
from dataclasses import dataclass, field


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

#     action_prompt_template = (
#         """
# I want to choose if the is any new action to do in a Android Screen, the action can be in the OS (Press Back, Press Home), Screen (Swipe, Scroll) and Widget (Tap, type, scroll_to). Using two inforation:
# Android Screen Context:
# User Goal: {user_goal}
# Current Screen Widgets: {screen_widgets}
# Current Android Activity: {android_activity}
# If you are inside the expected app, search for a widget that may help reach the task goal, like search button to tap and search or a widget with a content description with a expected name

# AVAILABLE ACTIONS: "tap", "type, "swipe_down", "swipe_left", "swipe_right", "open_app", when no action is need "completed"

# Return a tuple with the information as follow: (<action_enviremnt (OS, SR, WD)>,<which action (home, back)>,<if needed witch widget>). If you understend that the already is completed return completed for all value
#         """
#     )

    action_prompt_template = (
        """
Acessibility describe with app screen is this one and with action can be perform, with paths can navigate based on the widgets and activity information; Return only a tuple like ('JsonLike of selected Widget with attributes', 'action to do in the widget') to be able to help reach the goal and if you think the task is completed return 'None'.
User Goal: {user_goal}
Current Screen Widgets: {screen_widgets}
Current Android Activity: {android_activity}
        """
    )

    TIME_BETWEEN_STEPS = 5
    MAX_STEPS = 20

    user_input = "open the Contatos app, find the 'Ana Santiago' contact and make a call"#"open the calculator and do 11 plus 34" #  #"open the calculator and do 10 plus 10"  # "Open the Play Store and install 'Clash of Clans' game"#"Play the playlist 'JJ' in Spotify" # input("What action do you want to do? > ")

    prompt_response = gemini_client.generate_text(
        f"Interpret and find the 'app' name to be open and perform the action in the current input: {user_input}.  return only the app name (if need translete to portuguese-brasil camelcase) as a single string no other information or content."
    )
    app_name = prompt_response
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
    for i in range(MAX_STEPS):
        _log(f"===== STEP {i + 1}/{MAX_STEPS} =====")
        step_start_time = time.time()
        available_widgets = android_client.get_interactive_widgets()
        current_android_activity = android_client.get_current_activity()
        session.update_context(
            available_widgets,
            current_android_activity,
        )
        current_prompt = action_prompt_template.format(
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
        _log(prompt_response_literal)
        if prompt_response_literal and isinstance(prompt_response_literal, tuple):
            widget_attributes = literal_eval(prompt_response_literal[0])
            widget_action = prompt_response_literal[1]
        else:
            # No valid reponse from the API. Probably reach the goal.
            break

        if "tap" == widget_action or "click" == widget_action:
            _log(f'Widget to be pressed: {widget_attributes}')
            tap_widget = android_client.find_widget(widget_attributes)
            tap_widget.tap()
        if "type" in widget_action:
            re_pattern = r"type (.+)"
            match = re.match(re_pattern, widget_action)
            if match:
                content_to_type = match.group(1)
            type_widget = android_client.find_widget(widget_attributes)
            type_widget.type_text(content_to_type)
            android_client._press_back()


        step_end_time = time.time()
        _log(f"Step {i + 1} took {step_end_time - step_start_time:.2f} seconds.")
        time.sleep(TIME_BETWEEN_STEPS)


if __name__ == "__main__":
    main()
