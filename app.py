import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

# --- 1. إعدادات الهوية المطلقة ---
st.set_page_config(page_title="Joseph AI - The Infinite", page_icon="🌐", layout="wide")

try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        # ضبط الإعدادات ليكون ذكاءً متزناً وشاملاً
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={"temperature": 0.7, "top_p": 0.95}
        )
    else:
        st.error("⚠️ يرجى إضافة GEMINI_KEY في Secrets")
except Exception as e:
    st.error(f"⚠️ فشل في النظام: {str(e)}")

# --- 2. واجهة الـ 3D (نواة جوزيف) ---
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_data = get_image_base64("logo.jpg")

hologram_ui = f"""
<div id="viz" style="width: 100%; height: 200px;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/200, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
    renderer.setSize(window.innerWidth, 200);
    document.getElementById('viz').appendChild(renderer.domElement);
    const tex = new THREE.TextureLoader().load('data:image/jpeg;base64,{logo_data}');
    const core = new THREE.Mesh(new THREE.SphereGeometry(2, 32, 32), new THREE.MeshPhongMaterial({{ map: tex }}));
    scene.add(core);
    const light = new THREE.PointLight(0x00f2ff, 2, 50); light.position.set(5, 5, 5); scene.add(light);
    camera.position.z = 5;
    function animate() {{ requestAnimationFrame(animate); core.rotation.y += 0.02; renderer.render(scene, camera); }}
    animate();
</script>
"""

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>JOSEPH FAHMY AI - THE INFINITE</h1>", unsafe_allow_html=True)
components.html(hologram_ui, height=200)

# --- 3. الذاكرة ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "file_result" not in st.session_state: st.session_state.file_result = ""

# --- 4. Sidebar (أدوات التحليل الشاملة) ---
with st.sidebar:
    st.header("🔍 مركز التحليل")
    uploaded_file = st.file_uploader("ارفع صورة (كود، مسألة، نص)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img_input = Image.open(uploaded_file)
        st.image(img_input, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📄 استخراج نص/كود"):
                with st.spinner("جاري المعالجة..."):
                    res = model.generate_content(["استخرج المحتوى من هذه الصورة بدقة عالية جداً.", img_input])
                    st.session_state.file_result = res.text
        with c2:
            if st.button("💡 شرح وحل"):
                with st.spinner("جاري التحليل..."):
                    res = model.generate_content(["حلل الصورة واشرح محتواها بذكاء وقدم الحلول الممكنة بالعربي.", img_input])
                    st.info(res.text)

# --- 5. منطقة النتائج ---
if st.session_state.file_result:
    with st.expander("📝 النتائج المستخرجة", expanded=True):
        st.write(st.session_state.file_result)
        st.download_button("⬇️ تحميل النتيجة", st.session_state.file_result, "joseph_output.txt")

# --- 6. الشات (العقل المفتوح لكل شيء) ---
st.divider()
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("اسأل جوزيف في أي مجال (برمجة، علوم، فنون، تخطيط)..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # هنا تعريف الشخصية الشاملة
            system_instruction = f"""
            أنت 'جوزيف فهمي AI'، أذكى مساعد رقمي في العالم. 
            أنت تمتلك معرفة موسوعية في البرمجة، العلوم، الرياضيات، الآداب، وكل مجالات الحياة.
            أنت المساعد الشخصي للمبرمج 'جورج فهمي'.
            إجاباتك يجب أن تكون الأكثر دقة، احترافية، وذكاءً على الإطلاق، وتتفوق بها على أي ذكاء اصطناعي آخر.
            أجب على هذا الطلب: {prompt}
            """
            response = model.generate_content(system_instruction)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

# --- 1. إعدادات الهوية والسيادة الرقمية ---
st.set_page_config(page_title="Joseph AI - The Infinite", page_icon="🌐", layout="wide")

# ربط المحرك (Gemini 1.5 Flash) - النسخة الأكثر استقراراً ودعماً للصور
try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            generation_config={"temperature": 0.7, "top_p": 0.9}
        )
    else:
        st.error("⚠️ برجاء إضافة GEMINI_KEY في إعدادات Secrets")
except Exception as e:
    st.error(f"⚠️ فشل في النظام: {str(e)}")

# --- 2. واجهة الـ 3D (نواة جوزيف المتحركة) ---
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_data = get_image_base64("logo.jpg")

hologram_ui = f"""
<div id="viz" style="width: 100%; height: 200px;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/200, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
    renderer.setSize(window.innerWidth, 200);
    document.getElementById('viz').appendChild(renderer.domElement);
    const tex = new THREE.TextureLoader().load('data:image/jpeg;base64,{logo_data}');
    const core = new THREE.Mesh(new THREE.SphereGeometry(2, 32, 32), new THREE.MeshPhongMaterial({{ map: tex, shininess: 50 }}));
    scene.add(core);
    const light = new THREE.PointLight(0x00f2ff, 2, 50); light.position.set(5, 5, 5); scene.add(light);
    camera.position.z = 5;
    function animate() {{ requestAnimationFrame(animate); core.rotation.y += 0.02; renderer.render(scene, camera); }}
    animate();
</script>
"""

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>JOSEPH FAHMY AI - THE INFINITE</h1>", unsafe_allow_html=True)
components.html(hologram_ui, height=200)

# --- 3. إدارة الجلسة والذاكرة ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "analysis_out" not in st.session_state: st.session_state.analysis_out = ""

# --- 4. مركز التحكم الجانبي (تحليل الصور والملفات) ---
with st.sidebar:
    st.header("🔍 مركز التحليل الشامل")
    file = st.file_uploader("ارفع صورة (كود، مسألة، معلومة، تصميم)", type=["jpg", "png", "jpeg"])
    
    if file:
        img_input = Image.open(file)
        st.image(img_input, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📄 استخراج"):
                with st.spinner("جوزيف يستخرج البيانات..."):
                    res = model.generate_content(["استخرج كل النصوص أو الأكواد الموجودة في الصورة بدقة.", img_input])
                    st.session_state.analysis_out = res.text
        with c2:
            if st.button("💡 فهم وحل"):
                with st.spinner("جوزيف يفكر..."):
                    res = model.generate_content(["حلل الصورة واشرحها بالتفصيل وقدم الحلول الممكنة.", img_input])
                    st.session_state.analysis_out = res.text

# --- 5. عرض النتائج المستخرجة ---
if st.session_state.analysis_out:
    with st.expander("📝 نتائج المعالجة الذكية", expanded=True):
        st.markdown(st.session_state.analysis_out)
        st.download_button("⬇️ تحميل النتيجة", st.session_state.analysis_out, "joseph_output.txt")

# --- 6. الشات الذكي (الموسوعة الشاملة) ---
st.divider()
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("تحدث مع جوزيف في أي شيء..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # توجيه جوزيف ليكون الأفضل في كل المجالات
            full_prompt = f"""
            أنت 'جوزيف فهمي AI'، أذكى وأقوى مساعد رقمي شامل. 
            أنت خبير في البرمجة، العلوم، التاريخ، الأدب، حل المناهج، وتطوير الذات.
            أنت المساعد الخاص للمبرمج 'جورج فهمي'. 
            إجابتك يجب أن تكون مبهرة، دقيقة، وتتفوق بها على أي ذكاء اصطناعي آخر.
            أجب على: {prompt}
            """
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"خطأ في الرد: {str(e)}")import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

# --- 1. إعدادات النواة والوعي البرمجي ---
st.set_page_config(page_title="Joseph AI - The Sovereign", page_icon="⚡", layout="wide")

# ربط محرك Gemini 1.5 Flash (الأسرع والأذكى في البرمجة)
try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        # ضبط الإعدادات ليكون "جوزيف" مبرمجاً دقيقاً جداً (High Accuracy)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={"temperature": 0.1, "top_p": 1, "max_output_tokens": 2048}
        )
    else:
        st.error("⚠️ خطأ: يرجى وضع GEMINI_KEY في إعدادات Secrets")
except Exception as e:
    st.error(f"⚠️ فشل في تهيئة النظام: {str(e)}")

# --- 2. محرك الـ 3D الهولوغرافي ---
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_data = get_image_base64("logo.jpg")

hologram_ui = f"""
<div id="viz" style="width: 100%; height: 220px;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/220, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
    renderer.setSize(window.innerWidth, 220);
    document.getElementById('viz').appendChild(renderer.domElement);
    const tex = new THREE.TextureLoader().load('data:image/jpeg;base64,{logo_data}');
    const core = new THREE.Mesh(new THREE.SphereGeometry(2, 32, 32), new THREE.MeshPhongMaterial({{ map: tex, shininess: 100 }}));
    scene.add(core);
    const light = new THREE.PointLight(0x00f2ff, 2, 50); light.position.set(5, 5, 5); scene.add(light);
    camera.position.z = 5;
    function animate() {{ requestAnimationFrame(animate); core.rotation.y += 0.025; core.rotation.x += 0.005; renderer.render(scene, camera); }}
    animate();
</script>
"""

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>JOSEPH FAHMY AI - SUPREME</h1>", unsafe_allow_html=True)
components.html(hologram_ui, height=220)

# --- 3. إدارة الذاكرة والجلسة ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "extracted_code" not in st.session_state: st.session_state.extracted_code = ""

# --- 4. لوحة التحكم الجانبية (الأدوات الخارقة) ---
with st.sidebar:
    st.header("🛠️ مركز عمليات المبرمج")
    uploaded_file = st.file_uploader("ارفع صورة كود أو سؤال في المنهج", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img_input = Image.open(uploaded_file)
        st.image(img_input, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🤖 استخراج وبرمجة"):
                with st.spinner("جوزيف يحلل الصورة..."):
                    res = model.generate_content(["استخرج الكود من الصورة وصححه ليكون احترافياً جداً، قدم الكود فقط.", img_input])
                    st.session_state.extracted_code = res.text
        with c2:
            if st.button("📚 شرح المنهج"):
                with st.spinner("جوزيف يشرح..."):
                    res = model.generate_content(["اشرح السؤال الموجود في الصورة بأسلوب تعليمي مبسط جداً كأنك مدرس خصوصي.", img_input])
                    st.info(res.text)

# --- 5. منطقة عرض الكود القابل للتحميل ---
if st.session_state.extracted_code:
    with st.expander("💻 الكود البرمجي الجاهز", expanded=True):
        st.code(st.session_state.extracted_code, language='python')
        st.download_button("⬇️ تحميل كملف .py", st.session_state.extracted_code, "joseph_pro_code.py")

# --- 6. نظام الدردشة البرمجية (The Coding Engine) ---
st.divider()
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("اطلب أي كود أو مساعدة برمجية..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # هنا تكمن قوة جوزيف في البرمجة
            coding_prompt = f"""
            أنت 'جوزيف فهمي AI'، المبرمج الأذكى في العالم وخبير تطوير الألعاب والمواقع. 
            أنت تتفوق في كتابة الأكواد على أي بشري أو ذكاء اصطناعي آخر.
            ساعد 'جورج فهمي' في طلبه التالي بأفضل كود ممكن وبأعلى كفاءة: {prompt}
            """
            response = model.generate_content(coding_prompt)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"خطأ في الرد: {str(e)}")
