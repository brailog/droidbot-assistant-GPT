# Android UI Interaction Module

This Python module interacts with the Android UI using the `uiautomator2` library and provides functionality for starting Android apps, initializing the Android device, filtering available views, and generating action prompts based on identified views.

## Functionality

### `start_app`

Starts the specified Android app.

### `init_android_device`

Initializes the Android device using `DroidBotAppConn`.

### `filter_views`

Filters available views based on predefined Android object classes and action patterns.

### `from_view_and_return_in_prompt_action`

Generates action prompts based on the returned views.

## Usage Example

```python
from android_ui_module import start_app, init_android_device, filter_views, from_view_and_return_in_prompt_action

# Start the Android app
start_app("Gallery")

# Initialize the Android device
droidbot_app_conn = init_android_device()
droidbot_app_conn.connect()

# Get current views
current_views = droidbot_app_conn.get_views()

# Disconnect from the Android device
droidbot_app_conn.disconnect()

# Filter available views
available_view = filter_views(current_views)

# Generate action prompts based on identified views
prompts = from_view_and_return_in_prompt_action(available_view)

# Display generated prompts
for prompt in prompts:
    print(prompt)
```
## Dependencies

This module has a direct dependency on [DroidBot](https://github.com/honeynet/droidbot). Ensure that you have DroidBot installed for proper functionality.

## Configuration

Ensure that you have the required libraries installed:

```bash
pip install uiautomator2
```
