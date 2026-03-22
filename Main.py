from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import threading
import time
import random
from datetime import datetime
from ai_model import analyzer
from email_config import EmailAlert

app = FastAPI(title="Network Guardian")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect('network.db')
    conn.row_factory = sqlite3.Row
    return conn

# ========== DATABASE INIT ==========
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ip TEXT,
            status TEXT,
            threat_level TEXT,
            cpu_usage INTEGER,
            memory_usage INTEGER,
            last_seen TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_name TEXT,
            message TEXT,
            severity TEXT,
            timestamp TEXT,
            is_resolved INTEGER
        )
    ''')
    
    # Insert default user if not exists
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('admin', 'admin123', 'admin'))
    
    # Insert sample devices if empty
    cursor.execute("SELECT COUNT(*) FROM devices")
    if cursor.fetchone()[0] == 0:
        devices = [
            ('Main Router', '192.168.1.1', 'online', 'low', 45, 60, 'Just now'),
            ('Firewall-01', '192.168.1.100', 'online', 'medium', 78, 82, '2 mins ago'),
            ('DNS Server', '192.168.1.53', 'under_attack', 'high', 95, 98, 'Just now'),
            ('Web Server', '192.168.1.60', 'online', 'low', 34, 45, '1 min ago'),
            ('Database Server', '192.168.1.50', 'offline', 'low', 0, 0, '5 mins ago'),
            ('Mail Server', '192.168.1.70', 'online', 'low', 23, 38, '3 mins ago'),
        ]
        cursor.executemany('''
            INSERT INTO devices (name, ip, status, threat_level, cpu_usage, memory_usage, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', devices)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

init_db()

# ========== TRAFFIC MONITOR WITH EMAIL ==========
class TrafficMonitor:
    def __init__(self):
        self.email = EmailAlert()
        self.thresholds = {'normal': 100, 'high': 300, 'critical': 500}
    
    def monitor_loop(self):
        while True:
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, ip FROM devices")
                devices = cursor.fetchall()
                
                for device in devices:
                    # Simulate traffic (replace with real SNMP in production)
                    traffic = random.randint(50, 600)
                    
                    if traffic > self.thresholds['critical']:
                        self.email.send_alert(
                            device_name=device['name'],
                            threat_type="CRITICAL TRAFFIC SPIKE",
                            root_cause=f"Traffic: {traffic} req/sec (Normal: {self.thresholds['normal']})",
                            severity="HIGH",
                            traffic=f"{traffic} req/sec"
                        )
                        # AI Auto-Resolve mechanism
                        cursor.execute("UPDATE devices SET threat_level='high', status='blocked' WHERE id=?", (device['id'],))
                        cursor.execute('''
                            INSERT INTO alerts (device_name, message, severity, timestamp, is_resolved)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (device['name'], f"🤖 AI Auto-Resolved: Blocked Critical Traffic Spike ({traffic} req/s)", 
                              'high', datetime.now().strftime("%I:%M %p"), 1))
                    
                    elif traffic > self.thresholds['high']:
                        # Removing email alert for MEDIUM risk; just update the level internally
                        cursor.execute("UPDATE devices SET threat_level='medium' WHERE id=?", (device['id'],))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(30)  # Check every 30 seconds

# Start monitor in background
monitor = TrafficMonitor()
thread = threading.Thread(target=monitor.monitor_loop, daemon=True)
thread.start()
print("✅ Traffic Monitor Started!")

# ========== API ENDPOINTS ==========
@app.get("/")
def root():
    return {"message": "Network Guardian API"}

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                  (data['username'], data['password']))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"success": True, "role": user['role']}
    return {"success": False}

@app.get("/api/devices")
def get_devices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()
    conn.close()
    return [dict(d) for d in devices]

@app.get("/api/alerts")
def get_alerts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC")
    alerts = cursor.fetchall()
    conn.close()
    return [dict(a) for a in alerts]

@app.get("/api/playbook")
def get_playbook():
    conn = get_db()
    cursor = conn.cursor()
    # Fetch AI auto-resolved entries for the playbook
    cursor.execute("SELECT * FROM alerts WHERE message LIKE '🤖 AI Auto-Resolved%' ORDER BY id DESC")
    playbook = cursor.fetchall()
    conn.close()
    return [dict(p) for p in playbook]

@app.get("/api/stats")
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM devices")
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as online FROM devices WHERE status='online'")
    online = cursor.fetchone()['online']
    cursor.execute("SELECT COUNT(*) as threats FROM devices WHERE threat_level='high'")
    threats = cursor.fetchone()['threats']
    cursor.execute("SELECT COUNT(*) as offline FROM devices WHERE status!='online'")
    offline = cursor.fetchone()['offline']
    conn.close()
    return {"total_devices": total, "online": online, "offline": offline, "active_threats": threats}

@app.post("/api/devices/{device_id}/block")
def block_device(device_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE devices SET status='blocked', threat_level='high' WHERE id=?", (device_id,))
    cursor.execute("SELECT name FROM devices WHERE id=?", (device_id,))
    device = cursor.fetchone()
    cursor.execute('''
        INSERT INTO alerts (device_name, message, severity, timestamp, is_resolved)
        VALUES (?, ?, ?, ?, ?)
    ''', (device['name'], f"Device blocked by admin", 'high', datetime.now().strftime("%I:%M %p"), 0))
    conn.commit()
    conn.close()
    return {"message": "Device blocked"}

@app.post("/api/devices/{device_id}/unblock")
def unblock_device(device_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE devices SET status='online', threat_level='low' WHERE id=?", (device_id,))
    conn.commit()
    conn.close()
    return {"message": "Device unblocked"}

@app.post("/api/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET is_resolved=1 WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()
    return {"message": "Alert resolved"}

@app.post("/api/analyze")
async def analyze_device(request: Request):
    data = await request.json()
    device_id = data.get('device_id')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices WHERE id=?", (device_id,))
    device = cursor.fetchone()
    conn.close()
    
    if device:
        device_data = {
            'requests': random.randint(50, 600),
            'cpu': device['cpu_usage'],
            'memory': device['memory_usage'],
            'failed_logins': random.randint(0, 50)
        }
        result = analyzer.analyze_threat(device_data, device['name'])
        
        # Auto-create alert if threat detected
        if result['threat_type'] != 'Normal Traffic':
            conn = get_db()
            cursor = conn.cursor()
            
            if result.get('action') == 'block':
                # AI automatically resolving the threat by blocking it
                cursor.execute("UPDATE devices SET status='blocked', threat_level='high' WHERE id=?", (device_id,))
                cursor.execute('''
                    INSERT INTO alerts (device_name, message, severity, timestamp, is_resolved)
                    VALUES (?, ?, ?, ?, ?)
                ''', (device['name'], f"🤖 AI Auto-Resolved: Blocked {result['threat_type']}", 
                      result['severity'], datetime.now().strftime("%I:%M %p"), 1))
            else:
                cursor.execute('''
                    INSERT INTO alerts (device_name, message, severity, timestamp, is_resolved)
                    VALUES (?, ?, ?, ?, ?)
                ''', (device['name'], f"AI: {result['threat_type']} - {result['root_cause']}", 
                      result['severity'], datetime.now().strftime("%I:%M %p"), 0))

            conn.commit()
            conn.close()
        
        return result
    
    return {"error": "Device not found"}
