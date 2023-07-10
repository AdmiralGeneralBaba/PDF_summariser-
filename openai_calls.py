import openai
import os

class OpenAI : 
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY') 
    def open_ai_gpt_call(self, user_content, prompt=None): 
        if isinstance(user_content, list):  # checks if user_content is a list
            messages = user_content
            if prompt:
                messages.insert(0, {"role":"system", "content": prompt})
        else:
            messages = [{"role": "user", "content": user_content}]
            if prompt:
                messages.insert(0, {"role":"system", "content": prompt})

        completion  = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply_content = completion.choices[0].message.content
        return reply_content  # Returning the reply_content from the function
    def open_ai_gpt4_call(self, user_content, prompt=None) : 
            messages = [{"role": "user", "content": user_content}]
            if prompt:
                messages.insert(0, {"role":"system", "content": prompt})

            completion  = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=messages
            )

            reply_content = completion.choices[0].message.content

            return reply_content  # Returning the reply_content from the function7
    def open_ai_dalle_call_n1(self, inputPrompt) :
        response = openai.Image.create(
            prompt= inputPrompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
