import openai
from console_window import ConsoleWindow

import game_config
import helpers

max_openai_calls_retries = 3

initialized = False

def openai_call(
    prompt: str,
    model: str = None,
    temperature: float = 0.5,
    max_tokens: int = 100,
):
    global initialized    
    if not initialized:
        openai.api_key = game_config.get_string("openapi_key")        
        initialized = True

    if not model:
        model = game_config.get_string("openapi_model")
    if not model:
        model = "gpt-3.5-turbo"
    global openai_calls_retried
    if not model.startswith("gpt-"):
        # Use completion API
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text.strip()
    else:
        # Use chat completion API
        messages=[{"role": "user", "content": prompt}]
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None,
            )
            openai_calls_retried = 0
            return response.choices[0].message.content.strip()
        except Exception as e:
            # try again
            if openai_calls_retried < max_openai_calls_retries:
                openai_calls_retried += 1
                print(f"Error calling OpenAI. Retrying {openai_calls_retried} of {max_openai_calls_retries}...")
                return openai_call(prompt, model, temperature, max_tokens)
            
def openapi_create_room(room_id: str, direction: str, description: str):
    # first we get the information about the room we are in
    room = helpers.get_room(room_id)
    # write a prompt that provides information about the current room, also provide description passed into this function to get the new room title and room description in json format
    prompt = f"Write a description for the room to the {direction} of {room.name} with the description {room.description}. If appropriate, mention the existing room in the description.\n\nHere is some additional user provided information about the new room. {description}\n\n"
    new_room = openai_call(prompt)
    ConsoleWindow.instance.print(f"Creating room: {new_room}\n")