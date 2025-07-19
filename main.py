import os

from chatter import GPT3_TURBO, chatter
from dotenv import load_dotenv
from jinja_helper import process_template

load_dotenv()


def main() -> None:
    api_key = os.getenv("OPENAI_KEY")
    if not api_key:
        raise ValueError(
            "No API key found. Please set your OPENAI_KEY in the .env file."
        )
    chat_fn = chatter(api_key)

    data = {
        "LOW_DIFFICULTY": 1,
        "HIGH_DIFFICULTY": 5,
        "NUM_PROBLEMS": 10,
    }

    prompt = process_template("prompts/addition.jinja", data)
    res = chat_fn(prompt)
    print("Res: ")
    print(res)


if __name__ == "__main__":
    main()
