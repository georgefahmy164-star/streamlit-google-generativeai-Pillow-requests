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
