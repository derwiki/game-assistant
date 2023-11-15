import time

import openai


prompt = """
Create a simple HTML and JavaScript based memory card flip game suitable for toddlers. All code should be in one file.
The game should include a 4x4 grid of cards that the player can click to flip over and reveal an animal emoji.
The grid should be responsively fit to the browser window and should use 95% of the viewport width and height.
The game needs to start with all cards face-side (i.e. emoji-side) down.
When two cards with the same emoji are flipped over consecutively, they remain visible (only if it is a correct match) and their backgrounds change to a pastel green.
When two cards with different emoji are flipped over, make the cards shake for 2 seconds and then flip them back to face down.
The game is won when all card pairs are successfully matched.
When the game is won, one at a time with a 0.25s delay between, change every emoji to a celebratory emoji
(choose 4 different celebration emojis, not just one).
"""


def extract_html_snippets(markdown_text):
    snippets = []
    lines = markdown_text.split("\n")
    inside_code_block = False
    current_snippet = []

    for line in lines:
        if line.strip() == "```html":
            inside_code_block = True
            current_snippet = []
        elif line.strip() == "```" and inside_code_block:
            inside_code_block = False
            snippets.append("\n".join(current_snippet))
            current_snippet = []
        elif inside_code_block:
            current_snippet.append(line)

    return snippets


def create_game():
    client = openai.OpenAI()
    assistant = client.beta.assistants.create(
        name="Game Code Generator",
        instructions="Create a simple HTML/JavaScript game for toddlers to be played on an iPad",
        model="gpt-4-1106-preview",
    )

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while run.status not in ("completed", "failed"):
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"run.status = {run.status}")

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    content = messages.data[0].content[0].text.value
    return extract_html_snippets(content)[0]


if __name__ == "__main__":
    with open("index.html", "w+") as f:
        f.write(create_game())
