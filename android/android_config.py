import re

# APP NAME -> PACKAGE NAME
NAME_TO_PACKAGE = {
    "gallery": "com.sec.android.gallery3d",
    "galeria": "com.sec.android.gallery3d",
    "camera": "com.sec.android.app.camera",
    "whatsapp": "com.whatsapp",
}

# ANDROID ACTION MATCH
ACTIONS = [re.compile(r'search'), re.compile('options'), re.compile('content'), re.compile('btn'),
           re.compile('name'), re.compile('camera'), re.compile('tab'), re.compile('title'), re.compile('preview')]

# ANDROID WIDGET CLASS MATCH
CLASS_ANDROID_OBJ = [re.compile('ImageButton'), re.compile('TextView'), re.compile('ImageView'), re.compile('FrameLayout')]
