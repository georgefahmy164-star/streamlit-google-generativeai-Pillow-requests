"""
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
