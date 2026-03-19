import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

app = FastAPI()

# ربط ملفات الصور (اللوجو) عشان تظهر في الموقع
# تأكد إن ملف logo.jpg موجود في نفس المجلد
# app.mount("/static", StaticFiles(directory="."), name="static")

client = OpenAI(api_key="ضع_مفتاحك_هنا")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    # هذا السطر يقرأ ملف الـ HTML اللي تعبنا فيه ويظهره لك
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat(message: str = Form(...)):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت جوزيف فهمي AI. واجهتك هولوغرافية 3D وأنت خبير في Battlegrounds والترجمة."},
                {"role": "user", "content": message}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"response": f"خطأ في الاتصال: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
