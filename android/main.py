import re
import uiautomator2 as u2
from droidbot.adapter.droidbot_app import DroidBotAppConn
from utils import timeit

ACTIONS = [re.compile(r'search'), re.compile('options'), re.compile('content'), re.compile('btn'),
           re.compile('name'), re.compile('camera'), re.compile('tab'), re.compile('title')]
CLASS_ANDROID_OBJ = [re.compile('ImageButton'), re.compile('TextView'), re.compile('ImageView')]


d = u2.connect()  # connect to device

NAME_TO_PACKAGE = {
    "Gallery": "com.sec.android.gallery3d",
    "Camera": "com.sec.android.app.camera",
    "Whatsapp": "com.whatsapp",
}

TAG = '[DEBUG - ANDROID] |'


def start_app(app_name: str) -> None:  # Open
    _log(f'Stating app {app_name}')
    pkg = NAME_TO_PACKAGE.get(app_name)
    d.app_start(pkg)


def init_android_device() -> DroidBotAppConn:
    _log(f'Android Setup')
    droidbot_app_conn = DroidBotAppConn()
    droidbot_app_conn.set_up()
    return droidbot_app_conn


@timeit
def filter_views(view_options: list) -> list[dict]:
    _log(f'Performing view filter...')
    available_view = list()
    for view in view_options:
        for possible_android_obj in CLASS_ANDROID_OBJ:
            if possible_android_obj.findall(view.get('class')):
                for possible_action in ACTIONS:
                    content = __if_none_then_str(view.get('content_description'))
                    resource_id = __if_none_then_str(view.get('resource_id'))
                    text = __if_none_then_str(view.get('text'))
                    if (view.get('visible') and resource_id and (content or text) and
                            (possible_action.findall(resource_id) or possible_action.findall(content))):
                        available_view.append(view)
    _log(f'After filter find {len(available_view)} possible widgets to interactive')
    return available_view


def from_view_and_return_in_prompt_action(view_options: list[dict]) -> list[str]:
    _log(f'Generating action prompts based on returned views')
    prompts_action = []
    for view in view_options:
        text, resource_id, cont_desc, android_class = __get_view_info(view)
        prompt = (f'Founded a {android_class.split(".")[-1]} widget with the content description: '
                  f'{cont_desc}, text: {text} and resource_id: {resource_id}')
        prompts_action.append(prompt)

    return prompts_action


def __get_view_info(view: dict) -> tuple[str, str, str, str]:
    return view.get('text'), view.get('resource_id'), view.get('content_description'), view.get('class')


def __if_none_then_str(string: str) -> str:
    return string.lower() if string else ""


def _log(msg: str, tag=TAG) -> None:
    print(f'[{tag}] | {msg}')


if __name__ == '__main__':
    droidbot_app_conn = init_android_device()
    droidbot_app_conn.connect()
    current_views = droidbot_app_conn.get_views()
    # pprint.pprint(current_views)
    droidbot_app_conn.disconnect()
    available_view = filter_views(current_views)
    # pprint.pprint(available_view)
    p = from_view_and_return_in_prompt_action(available_view)
    for prompt in p:
        print(prompt)
