import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
import argparse
from call_function import available_functions, call_function
import sys

def main(): 
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise RuntimeError("Api Key is missing")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("user_prompt",type=str, help="User prompt")
    args = parser.parse_args()

    messages = [
        {"role":"system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    user_prompt = f"User prompt: {args.user_prompt}"
    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions)
        if response.usage is None:
            raise RuntimeError("Failed API Request")
        prompt_tokens = f"Prompt tokens: {response.usage.prompt_tokens}"
        response_tokens = f"Response tokens: {response.usage.completion_tokens}"
        message = response.choices[0].message
        messages.append(message)
        response_prompt = f"Response: {message.content}"
        if args.verbose: 
            print(user_prompt)
            print(prompt_tokens)
            print(response_tokens)
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(tool_call, args.verbose)
                if not result_message.get("content"):
                    raise Exception("No function results")
                messages.append(result_message)
                if args.verbose:
                    print(f"-> {result_message['content']}")
        else:
            print(response_prompt)
            break
    else:
        print("Hit the max number of iterations")
        sys.exit(1)

if __name__ == "__main__":
    main()

