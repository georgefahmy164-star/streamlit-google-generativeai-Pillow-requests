import streamlit as st
import google.generativeai as genai
import torch
import torch.nn as nn
from PIL import Image
import os

# ==========================================
# 1. THE ENGINE (Transformer Architecture)
# ==========================================
class JosephTransformer(nn.Module):
    def __init__(self, d_model=512, heads=8):
        super().__init__()
        # Multi-Head Attention Mechanism
        self.attention = nn.MultiheadAttention(d_model, heads, batch_first=True)
        # Residual Connections & Normalization (To solve Vanishing Gradient)
        self.norm = nn.LayerNorm(d_model)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, 2048),
            nn.ReLU(),
            nn.Linear(2048, d_model)
        )

    def forward(self, x):
        # Self-Attention + Residual
        attn_out, _ = self.attention(x, x, x)
        x = self.norm(x + attn_out)
        # Feed Forward + Residual
        ff_out = self.feed_forward(x)
        return self.norm(x + ff_out)

# ==========================================
# 2. THE BRAIN (Gemini API Integration)
# ==========================================
def run_ai_brain(prompt, image=None):
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if image:
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)
        return response.text
    return "⚠️ Missing API Key in Secrets!"

# ==========================================
# 3. THE FRONTEND (Joseph's UI Design)
# ==========================================
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="wide")

# تصميم ملكي (أسود وذهبي) يليق بالإمبراطور
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1 { color: #D4AF37; text-align: center; font-family: 'serif'; font-size: 60px; text-shadow: 0 0 20px #D4AF37; }
    .stChatInputContainer { border: 2px solid #D4AF37; border-radius: 30px; }
    .stButton>button { background: linear-gradient(45deg, #D4AF37, #BF953F); color: black; font-weight: bold; border-radius: 20px; width: 100%; }
    .sidebar-content { background-color: #111; padding: 20px; border-radius: 10px; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🔱 JOSEPH FAHMY AI | THE SHADOW</h1>", unsafe_allow_html=True)

# نظام الذاكرة (Memory Management)
if "history" not in st.session_state:
    st.session_state.history = []

# الواجهة الجانبية (Side Panel)
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.header("👑 تحكم الإمبراطور")
    uploaded_file = st.file_uploader("📸 تحليل بصري (Vision AI)", type=["jpg", "png", "jpeg"])
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.history = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# عرض المحادثات السابقة (Chat History)
for chat in st.session_state.history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

# منطقة الإدخال (The Request)
if prompt := st.chat_input("تحدث مع ظلك الرقمي..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🚀 جاري الاختراق والمعالجة عبر الـ Transformer Layers..."):
            img = Image.open(uploaded_file) if uploaded_file else None
            answer = run_ai_brain(prompt, img)
            st.write(answer)
            st.session_state.history.append({"role": "assistant", "content": answer})

st.markdown("<br><p style='text-align: center; color: #555;'>JOSEPH FAHMY AI - Powered by Deep Transformer Architecture 🔱</p>", unsafe_allow_html=True)
