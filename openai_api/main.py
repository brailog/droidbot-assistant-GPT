from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.thread_message import ThreadMessage
from openai.types.beta.threads.run import Run
from openai.pagination import SyncCursorPage


import time
import os
import asyncio
import pprint

TAG = '[DEBUG - OPENAI API] |'
assistant_key = os.environ.get("ASSISTANT_KEY")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def create_new_assistant(name: str, instructions: str, tools: list[dict], model: str) -> Assistant:
    _log(f'Creating assistant...')
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=tools,
        model=model
    )
    return assistant


def start_new_thread() -> Thread:
    _log(f'Creating new Thread')
    return client.beta.threads.create()


def attach_new_message_content_in_thread(thread: Thread, content="") -> ThreadMessage:
    _log(f'Attaching a new message to the Thread: {content}')
    return client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )


def run_thread(thread: Thread, assistant_id: str, instructions="") -> Run:
    _log(f'Running Thread: {thread.id}')
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant_id,
      instructions=instructions
    )

    return run


async def _thread_run_state(thread: Thread, run: Run, timeout=20) -> bool:
    _log(f'Requesting the Thread ({thread.id}) state')
    start = time.time()
    is_running = True
    while is_running and (time.time() - start < timeout):
        _log(f'Thread state: {is_running}')
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        is_running = run.status == 'in_progress'
        _log(f'object run state directly: {run.status}')
        await asyncio.sleep(3)


    return is_running


async def wait_for_condition(thread: Thread, run: Run,) -> SyncCursorPage[ThreadMessage]:
    _log(f'Wait for conditional for the thread ({thread.id})')
    # Start the request in the background
    request_task = asyncio.create_task(_thread_run_state(thread, run))
    done, pending = await asyncio.wait([request_task, asyncio.sleep(0)], return_when=asyncio.ALL_COMPLETED)

    _log(f'done : {done}')
    _log(f'pending : {pending}')
    _log(f'request task : {request_task}')

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    _log(f'messages data output: : {messages.data}')

    return messages


def _log(msg: str, tag=TAG) -> None:
    print(f'[{tag}] | {msg}')

def main():
    thread = start_new_thread()
    message = attach_new_message_content_in_thread(thread, "I need to solve the equation `3x + 11 = 14`. Can you help me?")
    run = run_thread(thread, assistant_key, "")

    prompt_output = asyncio.run(wait_for_condition(thread, run))
    pprint.pprint(prompt_output.data)

if __name__ == '__main__':
    main()