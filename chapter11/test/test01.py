from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
)

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

response = client.beta.threads.messages.list(
    thread_id=thread.id,
    limit=1 # Get the last message
)
print(response)