٦"""
تطبيق ذكاء اصطناعي متقدم باستخدام نموذج Transformer (GPT-2)
مع شرح للمفاهيم الأساسية في النماذج اللغوية الكبيرة.
"""

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import datetime
import webbrowser
import re

# --------------------------------------------------------------
# شرح المفاهيم المطلوبة (موجودة في التعليقات داخل الكود)
# --------------------------------------------------------------

class AIAssistantLLM:
    """
    مساعد ذكي يستخدم نموذج Transformer حقيقي.
    
    المفاهيم الأساسية:
    - Large Language Model (LLM): نموذج ضخم يُدرّب على كميات هائلة من النصوص.
    - Transformer: بنية تعتمد على آلية الانتباه (Attention) بدلاً من الشبكات المتكررة (RNN).
    - Parameters: القيم الرقمية التي يتعلمها النموذج أثناء التدريب (GPT-2 small يحتوي على 124 مليون معامل).
    - Python/C++: يكتب النموذج ببايثون للواجهة، بينما تكون العمليات الحسابية الثقيلة ب C++ (مثل PyTorch backend).
    - Frameworks (TensorFlow, JAX, PyTorch): أطر عمل لبناء النماذج.
    - Attention Mechanism: تسمح للنموذج بالتركيز على أجزاء معينة من المدخلات عند توليد كل كلمة.
    - RLHF (Reinforcement Learning from Human Feedback): أسلوب تدريب متقدم يجعل النموذج يتوافق مع تفضيلات البشر.
    - Frontend/API Client: يمكن ربط هذا المساعد بواجهة ويب أو تطبيق جوال عبر API.
    - The Engine: المحرك الأساسي (مثل PyTorch) الذي ينفذ العمليات الرياضية.
    - Request: طلب المستخدم الذي يمر عبر النموذج.
    - Self-Attention: آلية انتباه تربط بين مواقع مختلفة في نفس التسلسل.
    - Softmax: دالة رياضية تحول الدرجات إلى توزيع احتمالي.
    - Multi-Head Attention: عدة آليات انتباه تعمل بالتوازي لالتقاط أنواع مختلفة من العلاقات.
    - Training: عملية تحديث المعاملات بناءً على البيانات.
    - Layers: طبقات متعددة في الشبكة (مثل الطبقات المخفية).
    - Full Transformer: يتكون من Encoder وDecoder (في نماذج مثل GPT نستخدم فقط Decoder).
    - Encoder: يحول التسلسل المدخل إلى تمثيلات مستمرة.
    - Decoder: يولد التسلسل الناتج بناءً على تمثيلات الـ Encoder.
    - Residual Connections: وصلات تخطي تساعد على تدفق التدرجات عبر الطبقات العميقة.
    - Vanishing Gradient: مشكلة اختفاء التدرج في الشبكات العميقة، وتحلها Residual Connections.
    """

    def __init__(self, user_name):
        self.user_name = user_name
        self.running = True
        
        # تحميل النموذج والمحلل اللغوي (Tokenizer)
        print("جاري تحميل النموذج... (قد يستغرق بضع ثوانٍ)")
        self.model_name = "gpt2"  # يمكن تغييره إلى "gpt2-medium" أو "gpt2-large" إذا كان الجهاز قوياً
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
        
        # ضبط الرمز الخاص بالنهاية (EOS) لوقف التوليد
        self.eos_token_id = self.tokenizer.eos_token_id
        
        # وضع النموذج في وضع التقييم (بدون تدريب)
        self.model.eval()
        
        print(f"أهلاً {self.user_name}! أنا مساعدك الذكي (بنموذج GPT-2). اكتب 'وداعا' للخروج.")

    def generate_response(self, prompt, max_length=100, temperature=0.7):
        """
        توليد رد باستخدام النموذج.
        
        - prompt: النص المُدخل من المستخدم.
        - max_length: أقصى طول للرد (بما في ذلك prompt).
        - temperature: معامل التحكم في العشوائية (أقل = أكثر حرفية، أعلى = أكثر إبداعاً).
        """
        # ترميز النص إلى توكنات
        inputs = self.tokenizer.encode(prompt, return_tensors='pt')
        
        # توليد الرد
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,           # أخذ عينات عشوائية (وليس الأرجح دائماً)
                pad_token_id=self.eos_token_id,
                eos_token_id=self.eos_token_id,
                no_repeat_ngram_size=2,   # تجنب تكرار نفس العبارات
                top_p=0.9,                 # Nucleus sampling
                top_k=50                    # Top-k sampling
            )
        
        # فك الترميز إلى نص
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # إزالة الجزء المكرر من prompt إذا ظهر في الرد (يحدث أحياناً)
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        
        return response

    def handle_special_commands(self, user_input):
        """
        التعامل مع أوامر خاصة لا تحتاج إلى النموذج (مثل الوقت والتاريخ وفتح المواقع).
        """
        user_input_lower = user_input.lower()
        
        # الوقت
        if re.search(r'(كم الساعة|الساعة كم|الوقت)', user_input_lower):
            return f"الوقت الآن {datetime.datetime.now().strftime('%I:%M %p')}."
        
        # التاريخ
        elif re.search(r'(التاريخ|اليوم كم)', user_input_lower):
            return f"اليوم هو {datetime.datetime.now().strftime('%A, %d %B %Y')}."
        
        # فتح موقع ويب
        elif re.search(r'افتح (.*)', user_input_lower):
            match = re.search(r'افتح (.*)', user_input_lower)
            if match:
                site = match.group(1).strip()
                webbrowser.open(f"https://{site}.com")
                return f"جاري فتح {site}.com"
            else:
                return "ماذا تريد أن تفتح؟"
        
        # وداعاً (لإيقاف البرنامج)
        elif re.search(r'(وداعا|مع السلامة|باي)', user_input_lower):
            self.running = False
            return f"مع السلامة {self.user_name}! كان من الرائع التحدث معك."
        
        return None  # ليس أمراً خاصاً

    def run(self):
        """حلقة المحادثة الرئيسية"""
        while self.running:
            try:
                user_input = input(f"{self.user_name}: ").strip()
                if not user_input:
                    continue
                
                # التحقق من الأوامر الخاصة
                special_response = self.handle_special_commands(user_input)
                if special_response:
                    print(f"المساعد: {special_response}")
                    continue
                
                # استخدام النموذج لتوليد الرد
                print("المساعد: جاري التفكير...", end="", flush=True)
                response = self.generate_response(user_input)
                print(f"\rالمساعد: {response}")  # \r لمسح رسالة "جاري التفكير"
                
            except KeyboardInterrupt:
                print("\nالمساعد: تمت المقاطعة. إلى اللقاء!")
                break
            except Exception as e:
                print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    name = input("ما هو اسمك؟ ").strip()
    if not name:
        name = "صديقي"
    
    # إنشاء وتشغيل المساعد
    assistant = AIAssistantLLM(name)
    assistant.run()
"""
تطبيق Joseph Fahmey Ai - نسخة Gemini API الاحترافية
powered by Joseph Fahmey Ai
"""
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import datetime

# ======================================================
# الشعار الخاص بك
# ======================================================
def display_logo():
    logo = """
    ╔══════════════════════════════════════╗
    ║     powered by Joseph Fahmey Ai      ║
    ╚══════════════════════════════════════╝
    """
    print(logo)

# ======================================================
# إعدادات العميل
# ======================================================
# قم بتعيين مفتاح API كمتغير بيئة أو ضعه هنا (غير آمن للتوزيع)
# الأفضل: ضع المفتاح في متغير البيئة GEMINI_API_KEY
API_KEY = os.environ.get("GEMINI_API_KEY", "أدخل_مفتاحك_هنا")

# تهيئة العميل
client = genai.Client(api_key=API_KEY)

# النماذج المتاحة (اختر ما يناسبك)
TEXT_MODEL = "gemini-2.5-flash-preview"       # للردود السريعة
IMAGE_MODEL = "gemini-2.5-flash-image"        # لإنشاء وتحرير الصور

# ======================================================
# دوال المساعد
# ======================================================
def chat_with_gemini(prompt):
    """إرسال نص والحصول على رد نصي سريع"""
    try:
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"حدث خطأ: {e}"

def generate_image(prompt):
    """توليد صورة من وصف نصي"""
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        # البحث عن الصورة في الرد
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # حفظ الصورة
                image_data = part.inline_data.data
                image = Image.open(BytesIO(image_data))
                
                # إنشاء اسم ملف فريد
                filename = f"Joseph_AI_image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                image.save(filename)
                return f"✅ تم إنشاء الصورة وحفظها كـ: {filename}"
        
        return "لم يتم العثور على صورة في الرد."
    except Exception as e:
        return f"حدث خطأ أثناء توليد الصورة: {e}"

def multimodal_analysis(image_path, prompt):
    """تحليل صورة (رفعها) والإجابة عن أسئلة بشأنها"""
    try:
        # فتح الصورة
        image = Image.open(image_path)
        
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[prompt, image]  # نرسل الصورة والنص معاً
        )
        return response.text
    except Exception as e:
        return f"خطأ في التحليل: {e}"

# ======================================================
# الواجهة الرئيسية
# ======================================================
def main():
    display_logo()
    print("مرحباً بك في مساعد Joseph Fahmey Ai!")
    print("الأوامر المتاحة:")
    print("  - نص:       [رسالتك]")
    print("  - صورة:     اكتب 'صورة: وصف الصورة'")
    print("  - تحليل:    اكتب 'تحليل: مسار الصورة, سؤالك'")
    print("  - خروج:     وداعاً")
    print("-" * 50)

    while True:
        user_input = input("\nأنت: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ["وداعا", "مع السلامة", "باي", "خروج"]:
            print("المساعد: مع السلامة يا Joseph! كان من الرائع مساعدتك.")
            break
        
        # التعامل مع الأوامر الخاصة
        if user_input.startswith("صورة:"):
            # أمر توليد صورة
            prompt = user_input[5:].strip()
            print("المساعد: جاري إنشاء الصورة... (قد يستغرق 13-20 ثانية)")
            result = generate_image(prompt)
            print(f"المساعد: {result}")
            
        elif user_input.startswith("تحليل:"):
            # أمر تحليل صورة: تحليل: مسار/للملف, سؤالك
            parts = user_input[6:].strip().split(",", 1)
            if len(parts) == 2:
                img_path = parts[0].strip()
                question = parts[1].strip()
                print("المساعد: جاري تحليل الصورة...")
                result = multimodal_analysis(img_path, question)
                print(f"المساعد: {result}")
            else:
                print("المساعد: الصيغة الصحيحة: تحليل: مسار الصورة, سؤالك")
        
        else:
            # محادثة عادية
            print("المساعد: جاري التفكير...", end="", flush=True)
            response = chat_with_gemini(user_input)
            print(f"\rالمساعد: {response}")

if __name__ == "__main__":
    main()
    from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory

app = FastAPI()

# إعداد النموذج (يمكن استبداله بـ Llama 3 محلياً عبر Ollama)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key="YOUR_API_KEY")

# إعداد ذاكرة ذكية تلخص المحادثات الطويلة لتوفير الـ Tokens
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=1000)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

@app.post("/chat")
async def chat_endpoint(user_input: str):
    response = conversation.predict(input=user_input)
    return {"response": response}import os
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

# تحميل مفاتيح البيئة
load_dotenv()
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"

app = FastAPI(title="Professional AI Agent API")

# تعريف موديل البيانات للطلب
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = [] # لاستقبال تاريخ المحادثة من الفرونت إند

# إعداد الموديل مع تفعيل خاصية الـ Streaming
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    streaming=True
)

def build_prompt():
    """بناء الـ Prompt System الاحترافي"""
    return ChatPromptTemplate.from_messages([
        ("system", "أنت مساعد ذكاء اصطناعي متطور، خبير في البرمجة والتحليل. إجاباتك دقيقة، تقنية، وتستخدم لغة عربية سليمة."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

async def generate_ai_response(content: str, history: list) -> AsyncGenerator[str, None]:
    """دالة توليد الإجابة بنظام الـ Streaming كـ Generator"""
    prompt_template = build_prompt()
    
    # تحويل التاريخ من JSON إلى كائنات LangChain
    formatted_history = []
    for msg in history:
        if msg['role'] == 'user':
            formatted_history.append(HumanMessage(content=msg['content']))
        else:
            formatted_history.append(AIMessage(content=msg['content']))

    chain = prompt_template | llm

    # البدء في بث النتائج فور توليدها
    async for chunk in chain.astream({"input": content, "chat_history": formatted_history}):
        yield chunk.content

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """نقطة النهاية التي تدعم البث المباشر (SSE)"""
    return StreamingResponse(
        generate_ai_response(request.message, request.history),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. إعداد الإعدادات الأساسية
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 2. وظيفة معالجة الملفات وتحويلها لمتجهات (Indexing)
def ingest_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    # تقسيم النص لقطع صغيرة (Chunks) لسهولة البحث
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # تخزينها في قاعدة بيانات Vector DB (Chroma)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="./chroma_db")
    return vectorstore.as_retriever()

# 3. بناء الـ RAG Chain
def setup_rag_chain(retriever):
    system_prompt = (
        "أنت المساعد الذكي JOSEPH FAHMY Ai. "
        "استخدم قطع السياق التالية للإجابة على سؤال المستخدم. "
        "إذا لم تكن تعرف الإجابة من السياق، قل أنك لا تعرف. "
        "\n\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

# --- مثال على التشغيل ---
# افتراضاً أن لديك ملف باسم 'data.pdf'
retriever = ingest_pdf("data.pdf")
rag_chain = setup_rag_chain(retriever)

response = rag_chain.invoke({"input": "ما هي النقاط الرئيسية في هذا الملف؟"})
print(f"JOSEPH FAHMY Ai says: {response['answer']}")from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.tools.tavily_search import TavilySearchResults # أداة بحث إنترنت

# 1. الموديل الأساسي (المخ)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.5)

# 2. الذاكرة (تحفظ آخر 10 تفاعلات لضمان السياق)
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=10,
    return_messages=True
)

# 3. الأدوات (العضلات - مثل البحث في الإنترنت)
tools = [TavilySearchResults()] 

# 4. المساعد المتكامل (JOSEPH FAHMY Ai)
joseph_fahmy_ai = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True, # لمشاهدة كيف يفكر الموديل خلف الكواليس
    handle_parsing_errors=True
)

# تجربة المساعد
response = joseph_fahmy_ai.run(input="من هو جوزيف فهمي وما هي آخر أخباره في البرمجيات؟")
print(response)import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

class JosephFahmyAI:
    def __init__(self):
        # استخدام موديل flash للسرعة أو pro للدقة العالية
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)
        self.system_prompt = (
            "أنت JOSEPH FAHMY Ai، مساعد ذكاء اصطناعي فائق الذكاء. "
            "تتميز بالقدرة على تحليل الكود، الصور، وحل المشكلات المعقدة. "
            "أسلوبك تقني، دقيق، وودي في نفس الوقت."
        )

    def generate_response(self, user_input, chat_history, image_data=None):
        messages = [SystemMessage(content=self.system_prompt)]
        
        # إضافة تاريخ المحادثة للسياق
        for msg in chat_history:
            messages.append(msg)
            
        # إذا كان هناك صورة (Multimodal)
        if image_data:
            content = [{"type": "text", "text": user_input}, 
                       {"type": "image_url", "image_url": image_data}]
            messages.append(HumanMessage(content=content))
        else:
            messages.append(HumanMessage(content=user_input))
            
        response = self.model.invoke(messages)
        return response.contentimport streamlit as st
from backend import JosephFahmyAI
from PIL import Image

# إعدادات الصفحة
st.set_page_config(page_title="JOSEPH FAHMY Ai", page_icon="🤖", layout="wide")
st.title("🤖 JOSEPH FAHMY Ai")
st.markdown("---")

# تهيئة الموديل والذاكرة في الجلسة (Session State)
if "ai" not in st.session_state:
    st.session_state.ai = JosephFahmyAI()
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# شريط جانبي لرفع الصور
with st.sidebar:
    st.header("الوسائط")
    uploaded_file = st.file_uploader("ارفع صورة لتحليلها", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="الصورة المرفوعة", use_column_width=True)

# منطقة الإدخال (Chat Input)
if prompt := st.chat_input("كيف يمكن لـ JOSEPH FAHMY Ai مساعدتك اليوم؟"):
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد رد الذكاء الاصطناعي
    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير..."):
            # تحويل الصورة إذا وجدت
            img_data = None
            if uploaded_file:
                # كود مبسط لتحويل الصورة لـ Base64 أو مسار
                img_data = uploaded_file.getvalue() 
            
            # استدعاء المحرك
            response = st.session_state.ai.generate_response(prompt, [], img_data)
            st.markdown(response)
            
    # حفظ الرد في الذاكرة
    st.session_state.messages.append({"role": "assistant", "content": response})streamlit run app.py
