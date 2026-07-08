import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class Prompt(BaseModel):
    prompt: str

@app.post('/generate')
async def generate(prompt: Prompt):
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': 'You are a drone mission planner. Generate a JSON mission with waypoints.'},
            {'role': 'user', 'content': prompt.prompt}
        ]
    )
    return {'mission': response.choices[0].message.content}
