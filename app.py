from fastapi import FastAPI, Form
from openai import OpenAI
import os

app = FastAPI()
client = OpenAI(api_key="ضع_مفتاحك_هنا")

@app.post("/chat")
async def chat(message: str = Form(...)):
    # دمج سياق مشاريعك (Battlegrounds & Translator) في الـ System Prompt
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "أنت جوزيف فهمي AI، النسخة النهائية. خبير في برمجة الألعاب وترجمة النصوص."},
            {"role": "user", "content": message}
        ]
    )
    return {"response": response.choices[0].message.content}
