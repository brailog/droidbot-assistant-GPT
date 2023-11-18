import re

# APP NAME -> PACKAGE NAME
NAME_TO_PACKAGE = {
    "Gallery": "com.sec.android.gallery3d",
    "Camera": "com.sec.android.app.camera",
    "Whatsapp": "com.whatsapp",
}

# ANDROID ACTION MATCH
ACTIONS = [re.compile(r'search'), re.compile('options'), re.compile('content'), re.compile('btn'),
           re.compile('name'), re.compile('camera'), re.compile('tab'), re.compile('title')]

# ANDROID WIDGET CLASS MATCH
CLASS_ANDROID_OBJ = [re.compile('ImageButton'), re.compile('TextView'), re.compile('ImageView')]
