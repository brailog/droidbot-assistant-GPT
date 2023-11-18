from openai_api.main import assistant_playground
from utils import save_to_pickle, load_from_pickle
from ast import literal_eval
from android.droidbot import get_screen_actions_options, droidbot_init, droidbot_close
from android.uiautomator2 import start_app, find_and_tap_widget, uiautomator2_connection

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
    for step in steps:
        _log(step)

def main():
    uiautomator2_connection(setup=True)
    steps = list_of_android_steps()[1:]
    show_steps(steps)
    for step in steps:
        step = step.split('##')[-1].strip(" ")
        _log('Current step: ', step)
        if 'open' in step.lower():
            start_app('Whatsapp')
        elif step and 'unlock' not in step.lower():
            screen_options = get_screen_actions_options()
            prompt_options = "And the options are: "
            action = f'The Android action that need to be done is: {step}'
            prompt_options += ".\n".join(screen_options)
            _log(f"Action >>> {action}")
            _log(f"prompt options >>> {prompt_options}")
            chose_action = assistant_playground(f'{action}. {prompt_options}', 'asst_ddWK2VVGe0gYhX0JMC5KAbMx')
            _log('Eval > ', chose_action[0].content[0].text.value)
            try:
                chose_action = literal_eval(chose_action[0].content[0].text.value)
            except SyntaxError:
                chose_action = literal_eval(f'{dict(chose_action[0].content[0].text.value)}')
            _log(f'Action chose >>> {chose_action}')
            find_and_tap_widget(chose_action)


if __name__ == '__main__':
    main()