import time
import re
from openai_api.main import assistant_playground
from utils import save_to_pickle, load_from_pickle
from ast import literal_eval
from android.droidbot import get_screen_actions_options, droidbot_init, droidbot_close
from android.uiautomator2 import start_app, find_and_tap_widget, uiautomator2_connection, type_input

TAG = '[MAIN] | '
def _log(msg: str, tag=TAG) -> None:
    print(f'{tag} {msg}')

def list_of_android_steps() -> list[str]:
    prompt = input("What action do you want to do? > ")
    android_steps = assistant_playground(prompt, 'asst_MA7NF9enCfctZSe1yRTJaQ45')

   # android_steps = load_from_pickle("whatsapp_call_isabella_obj.pkl")
    list_of_steps = list()

    try:
        list_of_steps = android_steps[0].content[0].text.value.split('\n')
    except IndexError:
        _log("Unable to get the Android steps")

    return list_of_steps

def show_steps(steps: list[str]) -> None:
    _log('========== STEPS ==========')
    for step in steps:
        _log(step)

def main():
    TIME_BETWEEN_STEPS = 20
    device = uiautomator2_connection(setup=True)
    steps = list_of_android_steps()
    show_steps(steps)
    expected_num_steps = len(steps)
    for i, step in enumerate(steps):
        iteration = i+1
        step_lower = step.lower()
        _log(f' ===== START STEPS ITERATIONS {iteration}/{expected_num_steps} ===== ')
        step = step.split('##')[-1].strip(" ")
        _log(f'Current step: {i}#{step}')
        if 'open the' in step_lower:
            pattern = r'open the (\w+) app.'
            match = re.search(pattern, step_lower)
            if match:
                app_name = match.group(1)
                start_app(app_name)
            else:
                _log("[MAYBE BUG] No match found.")
        elif step:
            screen_options = get_screen_actions_options()
            _log(f'Numbers of screen options: {len(screen_options)}')
            if not screen_options:
                device.screen_on()
            prompt_options = "And the options are: "
            action = f'The Android action that need to be done is: {step}'
            prompt_options += ".\n".join(screen_options)
            chose_action = assistant_playground(f'{action}. {prompt_options}', 'asst_ddWK2VVGe0gYhX0JMC5KAbMx')
            _log('Prompt output:')
            _log(chose_action[0].content[0].text.value)
            try: # todo change the output handler
                chose_action = literal_eval(chose_action[0].content[0].text.value)
            except SyntaxError:
                chose_action = literal_eval(f'{dict(chose_action[0].content[0].text.value)}')

            _log(f' ===== REPORT ITERATION {iteration}/{expected_num_steps}===== ')
            _log(f'>>> CURRENT ACTION/STEP: {step}')
            # _log(f'>>> PROMPT OPTION: {prompt_options}')
            _log(f'>>> CHOSE ACTION: {chose_action}')

            if 'tap' in step_lower:
                find_and_tap_widget(chose_action)
            elif 'type' in step_lower:
                pattern = r'"([^"]*)"'
                matches = re.findall(pattern, step_lower)
                if matches:
                    _log(f'Typing: {matches[0]}')  # Output: Little one
                    type_input(matches[0])
            else:
                find_and_tap_widget(chose_action)
            _log(f'>>> WAIT {TIME_BETWEEN_STEPS}')
            time.sleep(TIME_BETWEEN_STEPS)


if __name__ == '__main__':
    main()
