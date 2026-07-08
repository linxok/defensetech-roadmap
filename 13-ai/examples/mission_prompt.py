from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "Generate a 5 waypoint survey mission at lat 50.4, lon 30.5, alt 100m. Output JSON."
    }]
)
print(response.choices[0].message.content)
