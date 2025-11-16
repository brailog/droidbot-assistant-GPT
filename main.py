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

    def update_context(self, widgets: list[Widget], activity: str | None):
        """Updates the session context with the latest screen widgets and activity."""
        self.current_screen_context = widgets
        self.current_activity = activity


TAG = '[MAIN] | '
def _log(msg: str, tag=TAG) -> None:
    print(f'{tag} {msg}')

def _match_app_name(user_goal: str) -> str | None:
    """Extracts the app name from the user's goal using regex."""
    match = re.search(r'open(?: the)? (.*?) (?:app)?$|launch(?: the)? (.*?) (?:app)?$', user_goal, re.IGNORECASE)
    if match:
        # Return the first non-None captured group
        return next((g for g in match.groups() if g is not None), None)
    return None

def main():
    gemini_client = GeminiClient()
    android_client = Uiautomator2Interface()

    action_prompt_template = (
        """
I want to choose if the is any new action to do in a Android Screen, the action can be in the OS (Press Back, Press Home), Screen (Swipe, Scroll) and Widget (Tap, type, scroll_to). Using two inforation:
Android Screen Context:
User Goal: {user_goal}
Current Screen Widgets: {screen_widgets}
Current Android Activity: {android_activity}

AVAILABLE ACTIONS: "tap", "type, "swipe_down", "swipe_left", "swipe_right", "open_app", when no action is need "completed"

Return a tuple with the information as follow: (<action_enviremnt (OS, SR, WD)>,<which action (home, back)>,<if needed witch widget>). If you understend that the already is completed return completed for all value
        """
    )
    TIME_BETWEEN_STEPS = 5
    MAX_STEPS = 1

    user_input = "Open the Play Store app" # input("What action do you want to do? > ")

    prompt_response = gemini_client.generate_text(f"Read, interpret and find the 'app' name to perform the action in the current input: {user_input}.  return only the app name as a single string no other information or content.")
    app_name = prompt_response

    android_client.search_for_app_via_app_tray(app_name)
    app_icon = android_client.find_widget({'text':app_name, 'resource_id': 'com.sec.android.app.launcher:id/label'})
    app_icon.tap()

    _log('1. Initialize Session Context')
    session = SessionContext(user_goal=user_input)

    _log('2. Start the execution loop')
    time.sleep(1)
    for i in range(MAX_STEPS):
        _log(f'===== STEP {i + 1}/{MAX_STEPS} =====')
        step_start_time = time.time()
        session.update_context(
        android_client.get_interactive_widgets(),
        android_client.get_current_activity()
        )
        cur_step = action_prompt_template.format(user_goal=session.user_goal, screen_widgets=session.current_screen_context, android_activity=session.current_activity)
        _log(f' CUR TEP  ==== {cur_step}' )
        prompt_response = gemini_client.generate_text(prompt=action_prompt_template.format(user_goal=session.user_goal, screen_widgets=session.current_screen_context, android_activity=session.current_activity), code_markdown_remove=True)

        _log(prompt_response)
        

        step_end_time = time.time()
        _log(f"Step {i + 1} took {step_end_time - step_start_time:.2f} seconds.")


if __name__ == '__main__':
    main()
