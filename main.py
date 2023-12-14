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

def send_prompt_to_assistent(prompt: str, assistant_key: str) -> str:
    android_steps = assistant_playground(prompt, assistant_key)

    try:
        list_of_steps = android_steps[0].content[0].text.value
    except IndexError:
        list_of_steps = ""
        _log("Unable to get the Android steps")

    return list_of_steps

def __match(prompt_step: str, regex_pattern: str, group=1) -> str:
    match = re.search(regex_pattern, prompt_step)
    if match:
          return match.group(group)


def __step_to_android_action_prompt(current_prompt_step: str, screen_options: list[str]) -> str:
    prompt_options = "And the options are: "
    action = f'The Android action that need to be done is: {current_prompt_step}'
    prompt_options += ".\n".join(screen_options)
    return f'{action}. {prompt_options}'


def __log_pprint_list(steps: list[str]) -> None:
    _log('========== STEPS ==========')
    for step in steps:
        _log(step)

def main():
    TIME_BETWEEN_STEPS = 20
    user_input = input("What action do you want to do? > ")
    device = uiautomator2_connection(setup=True)
    user_prompt_output = send_prompt_to_assistent(user_input, 'asst_MA7NF9enCfctZSe1yRTJaQ45').split('\n')
    expected_num_steps = len(user_prompt_output)
    __log_pprint_list(user_prompt_output)

    for i, step in enumerate(user_prompt_output):
        iteration = i+1
        current_prompt_step = step.lower()
        current_prompt_step = current_prompt_step.split('##')[-1].strip(" ")
        _log(f' ===== START STEPS ITERATIONS {iteration}/{expected_num_steps} ===== ')
        _log(f'Current step: {i}#{current_prompt_step}')
        if 'open the' in current_prompt_step:
            pattern = r'open the (\w+) app.'
            app_name = __match(current_prompt_step, pattern)
            start_app(app_name)
        elif current_prompt_step:
            screen_options = get_screen_actions_options()
            _log(f'Numbers of screen options: {len(screen_options)}')
            if not screen_options:
                device.screen_on()
            android_current_possible_action = __step_to_android_action_prompt(current_prompt_step, screen_options)
            send_prompt_to_assistent(android_current_possible_action, 'asst_ddWK2VVGe0gYhX0JMC5KAbMx')
            _log('Prompt output:')
            _log(android_current_possible_action)

            chose_action = literal_eval(android_current_possible_action) # todo improve!!!
            _log(f' ===== REPORT ITERATION {iteration}/{expected_num_steps}===== ')
            _log(f'>>> CURRENT ACTION/STEP: {current_prompt_step}')
            # _log(f'>>> PROMPT OPTION: {prompt_options}')
            _log(f'>>> CHOSE ACTION: {chose_action}')
            if 'tap' in current_prompt_step:
                find_and_tap_widget(chose_action)
            elif 'type' in current_prompt_step:
                pattern = r'"([^"]*)"'
                expected_text_type = __match(current_prompt_step, pattern)
                if expected_text_type:
                    _log(f'Typing: {expected_text_type}')   # MAYBE TO TYPE NEED TO CHANGE TO FINDALL!! stable version commit: 1647b3f6daa246c45b0a4a6986ae598eee797f7f
                    type_input(expected_text_type)
            else:
                find_and_tap_widget(chose_action)
            _log(f'>>> WAIT {TIME_BETWEEN_STEPS}')
            time.sleep(TIME_BETWEEN_STEPS)


if __name__ == '__main__':
    main()
