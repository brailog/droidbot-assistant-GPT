# OpenAI Assistant Module

This Python module interacts with the OpenAI API to create an Assistant and conduct conversations in a threaded manner. It offers functions to create an Assistant, start a new conversation thread, attach messages to the thread, run the thread with an OpenAI Assistant, and await the thread's completion. The module streamlines conversational interactions with the OpenAI API.

## Functions

### create_new_assistant

Creates a new OpenAI Assistant with specified attributes such as name, instructions, tools, and model.

### start_new_thread

Initiates a new conversation thread.

### attach_new_message_content_in_thread

Adds a new message to a designated conversation thread.

### run_thread

Executes a conversation thread with an OpenAI Assistant, allowing for additional instructions.

### wait_for_condition

Waits asynchronously for a conversation thread to conclude by monitoring its state.

## Usage Example

```python
from openai_assistant_module import create_new_assistant, start_new_thread, attach_new_message_content_in_thread, run_thread, wait_for_condition

# Create a new OpenAI Assistant
assistant = create_new_assistant(name="MyAssistant", instructions="Instructions for the Assistant", tools=[], model="text-davinci-002")

# Start a new conversation thread
thread = start_new_thread()

# Attach a user message to the thread
message = attach_new_message_content_in_thread(thread, "I need assistance with a question.")

# Run the thread with the OpenAI Assistant
run = run_thread(thread, assistant.id, instructions="Provide help with the user's question.")

# Wait for the thread to complete
messages = wait_for_condition(thread, run)

# Process and display the messages
for message in messages.data:
    print(message.content)
```

## Requirements

- Python 3.10.0
- The OpenAI Python library (`openai`)

## Configuration

Ensure that you have set the required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ASSISTANT_KEY`: Your Assistant key
