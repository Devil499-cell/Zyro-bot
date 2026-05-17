import requests
import json
import time
from datetime import datetime
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================= CONFIGURATION =================
BOT_TOKEN = "7527091387:AAGYxbCeX-JZDYdgcBt1etLmp0sPkdpAepc"
ADMIN_PASSWORD = "#zyro2000"
DEVELOPER_USERNAME = "@Leader_jii"

# Channel info with FORCE JOIN for BOTH channels
CHANNEL_1_NAME = "ALL ILLEGAL STUFFS"
CHANNEL_1_LINK = "https://t.me/ajaaobkl"
CHANNEL_1_USERNAME = "ajaaobkl"

CHANNEL_2_NAME = "MOD X PATEL"
CHANNEL_2_LINK = "https://t.me/Mod_x_patel"
CHANNEL_2_USERNAME = "Mod_x_patel"

# APIs
UNIVERSAL_API = "https://all-sigma-pad-api-damo-5-day.vercel.app/api"
API_KEY = "RAJAN123"
# =================================================

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OFFSET = 0

user_data = {}
admin_session = {}
trending_numbers = {}
waiting_for_input = {}
pending_admin_login = {}  # Track users waiting to enter password

# ============ HEALTH SERVER ============
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Running")
    def log_message(self, *args): pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

# ============ SEND MESSAGE ============
def send_msg(chat_id, text, reply_markup=None, parse_mode="HTML"):
    url = f"{BASE_URL}/sendMessage"
    
    try:
        chat_id = int(chat_id)
    except:
        pass
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "allow_sending_without_reply": True,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_callback(chat_id, text, callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id, "text": text, "show_alert": False}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def edit_message(chat_id, message_id, text, reply_markup=None):
    url = f"{BASE_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

# ============ FORCE JOIN CHECK FOR BOTH CHANNELS ============
def check_force_join_both(chat_id):
    """Check if user has joined BOTH required channels"""
    try:
        # Check Channel 1
        url1 = f"{BASE_URL}/getChatMember"
        payload1 = {
            "chat_id": f"@{CHANNEL_1_USERNAME}",
            "user_id": chat_id
        }
        response1 = requests.post(url1, json=payload1, timeout=10)
        
        # Check Channel 2
        url2 = f"{BASE_URL}/getChatMember"
        payload2 = {
            "chat_id": f"@{CHANNEL_2_USERNAME}",
            "user_id": chat_id
        }
        response2 = requests.post(url2, json=payload2, timeout=10)
        
        channel1_joined = False
        channel2_joined = False
        
        if response1.status_code == 200:
            data1 = response1.json()
            if data1.get("ok"):
                status1 = data1.get("result", {}).get("status", "")
                if status1 in ["member", "administrator", "creator"]:
                    channel1_joined = True
        
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get("ok"):
                status2 = data2.get("result", {}).get("status", "")
                if status2 in ["member", "administrator", "creator"]:
                    channel2_joined = True
        
        return channel1_joined, channel2_joined
    except Exception as e:
        print(f"Force join check error: {e}")
        return False, False

def send_force_join_message(chat_id, channel1_joined=False, channel2_joined=False):
    """Send message asking user to join both channels"""
    
    # Build status message
    status_msg = ""
    buttons = []
    
    if not channel1_joined:
        status_msg += f"\n❌ {CHANNEL_1_NAME} - Not joined"
        buttons.append([{"text": f"📢 JOIN {CHANNEL_1_NAME}", "url": CHANNEL_1_LINK}])
    else:
        status_msg += f"\n✅ {CHANNEL_1_NAME} - Joined"
    
    if not channel2_joined:
        status_msg += f"\n❌ {CHANNEL_2_NAME} - Not joined"
        buttons.append([{"text": f"📢 JOIN {CHANNEL_2_NAME}", "url": CHANNEL_2_LINK}])
    else:
        status_msg += f"\n✅ {CHANNEL_2_NAME} - Joined"
    
    buttons.append([{"text": "✅ Check Membership", "callback_data": "check_membership"}])
    
    keyboard = {
        "inline_keyboard": buttons
    }
    
    msg = (
        f"⚠️ <b>ACCESS DENIED</b> ⚠️\n\n"
        f"You must join BOTH channels to use this bot!\n\n"
        f"📢 <b>Channels Status:</b>{status_msg}\n\n"
        f"👇 <b>Join both channels and click CHECK</b>"
    )
    send_msg(chat_id, msg, reply_markup=keyboard, parse_mode="HTML")

# ============ DATA MANAGEMENT ============
def save_data():
    try:
        with open("user_data.json", "w") as f:
            json.dump(user_data, f, indent=2)
        with open("trending.json", "w") as f:
            json.dump(trending_numbers, f, indent=2)
    except:
        pass

def load_data():
    global user_data, trending_numbers
    try:
        with open("user_data.json", "r") as f:
            user_data = json.load(f)
    except:
        user_data = {}
    try:
        with open("trending.json", "r") as f:
            trending_numbers = json.load(f)
    except:
        trending_numbers = {}

def is_admin(chat_id):
    return str(chat_id) in admin_session

def get_display_name(user_info):
    first_name = user_info.get("first_name", "")
    last_name = user_info.get("last_name", "")
    username = user_info.get("username", "")
    
    if first_name and last_name:
        full_name = f"{first_name} {last_name}"
    elif first_name:
        full_name = first_name
    elif username:
        full_name = username
    else:
        full_name = "User"
    
    if username and username != full_name and username not in full_name:
        return f"{full_name} (@{username})"
    return full_name

def update_stats(chat_id, user_info, search_type=None, search_term=None):
    cid = str(chat_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    first_name = user_info.get("first_name", "")
    last_name = user_info.get("last_name", "")
    username = user_info.get("username", "")
    display_name = get_display_name(user_info)
    
    if cid not in user_data:
        user_data[cid] = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "display_name": display_name,
            "searches": [],
            "joined": now,
            "last_active": now
        }
        print(f"✅ New user: {display_name}")
    else:
        if not user_data[cid].get("display_name") or user_data[cid].get("display_name") == "User":
            user_data[cid]["first_name"] = first_name
            user_data[cid]["last_name"] = last_name
            user_data[cid]["username"] = username
            user_data[cid]["display_name"] = display_name
        user_data[cid]["last_active"] = now
    
    if search_term:
        user_data[cid]["searches"].append({
            "type": search_type,
            "term": search_term,
            "time": now
        })
        if search_type == "NUMBER":
            trending_numbers[search_term] = trending_numbers.get(search_term, 0) + 1
    
    save_data()

# ============ UNIVERSAL API CALL ============
def call_universal_api(api_type, term):
    try:
        url = f"{UNIVERSAL_API}?key={API_KEY}&type={api_type}&term={term}"
        print(f"📡 API Call: {url}")
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)[:50]}

def call_sms_api(number, message):
    try:
        term = f"{number}|{message}"
        url = f"{UNIVERSAL_API}?key={API_KEY}&type=SMS&term={term}"
        print(f"📡 SMS API Call: {url}")
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)[:50]}

# ============ FORMATTERS ============
def format_number_result(data, number):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    results = []
    if data.get("data", {}).get("success"):
        results = data["data"].get("result", {}).get("results", [])
    elif isinstance(data.get("data"), list):
        results = data["data"]
    
    if not results:
        return f"❌ No information found for {number}"
    
    first = results[0]
    
    result = f"📞 NUMBER INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Number: {number}\n\n"
    result += f"👤 Name: {first.get('NAME', first.get('name', 'N/A'))}\n\n"
    result += f"👨 Father: {first.get('fname', 'N/A')}\n\n"
    result += f"🆔 Aadhaar: {first.get('id', 'N/A')}\n\n"
    result += f"📞 Alternate: {first.get('alt', 'N/A')}\n\n"
    result += f"📡 Carrier: {first.get('circle', 'N/A')}\n\n"
    result += f"📧 Email: {first.get('email', 'N/A') or 'N/A'}\n\n"
    
    address = first.get('ADDRESS', first.get('address', 'N/A')) or 'N/A'
    if len(address) > 80:
        address = address[:77] + '...'
    result += f"📍 Address: {address}\n\n"
    
    total = len(results)
    if total > 1:
        result += f"📚 Total Records: {total}\n"
        result += f"💡 Use /full {number} to see all\n\n"
    
    result += f"⚡ POWERED BY @Leader_jii"
    return result

def format_sms_result(data, number, message):
    if data.get("error"):
        return f"❌ SMS Failed: {data['error']}"
    
    msg_preview = message[:100] + "..." if len(message) > 100 else message
    
    result = f"📱 SMS RESULT\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Number: {number}\n"
    result += f"📝 Message: {msg_preview}\n\n"
    
    if data.get("success"):
        result += f"✅ Status: SENT\n"
    else:
        result += f"❌ Status: FAILED\n"
        result += f"💬 Response: {data.get('message', 'Unknown error')}\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_full_number_result(data, number):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    results = []
    if data.get("data", {}).get("success"):
        results = data["data"].get("result", {}).get("results", [])
    
    if not results:
        return f"❌ No records found for {number}"
    
    total = len(results)
    result = f"📞 FULL NUMBER DETAILS\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Number: {number}\n"
    result += f"📊 Total Records: {total}\n"
    result += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, rec in enumerate(results[:15], 1):
        result += f"▶ Record {i}\n"
        result += f"   👤 Name: {rec.get('NAME', rec.get('name', 'N/A'))}\n"
        result += f"   👨 Father: {rec.get('fname', 'N/A')}\n"
        result += f"   🆔 Aadhaar: {rec.get('id', 'N/A')}\n"
        result += f"   📞 Alt: {rec.get('alt', 'N/A')}\n"
        result += f"   📡 Carrier: {rec.get('circle', 'N/A')}\n"
        address = rec.get('ADDRESS', rec.get('address', 'N/A')) or 'N/A'
        if len(address) > 60:
            address = address[:57] + '...'
        result += f"   📍 Address: {address}\n\n"
    
    if total > 15:
        result += f"⚠️ Showing first 15 of {total} records\n"
    
    result += f"⚡ POWERED BY @Leader_jii"
    return result

def format_ip_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    ip_data = data.get("data", {}).get("result", {})
    if not ip_data:
        return f"❌ No information found for IP: {term}"
    
    result = f"🌐 IP INFORMATION\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 IP: {ip_data.get('IP', term)}\n\n"
    result += f"📍 Location: {ip_data.get('City', 'N/A')}, {ip_data.get('Region', 'N/A')}\n"
    result += f"🌍 Country: {ip_data.get('Country', 'N/A')}\n"
    result += f"📮 Postal: {ip_data.get('Postal', 'N/A')}\n\n"
    result += f"🏢 ISP: {ip_data.get('ISP', 'N/A')}\n"
    result += f"🏢 Organization: {ip_data.get('ORG', 'N/A')}\n"
    result += f"🆔 ASN: {ip_data.get('ASN', 'N/A')}\n\n"
    result += f"🌐 Domain: {ip_data.get('Domain', 'N/A')}\n"
    result += f"📡 Type: {ip_data.get('Type', 'N/A')}\n\n"
    result += f"🗺️ Coordinates: {ip_data.get('Location', 'N/A')}\n"
    result += f"⏰ Timezone: {ip_data.get('Timezone', 'N/A')}\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_vehicle_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    vehicle_data = data.get("data", {})
    if not vehicle_data:
        return f"❌ No information found for vehicle: {term.upper()}"
    
    result = f"🚗 VEHICLE INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Vehicle: {term.upper()}\n\n"
    result += f"👤 Owner: {vehicle_data.get('Owner Name', 'N/A')}\n"
    result += f"🏭 Model: {vehicle_data.get('Model Name', 'N/A')}\n"
    result += f"📝 Maker: {vehicle_data.get('Maker Model', 'N/A')}\n"
    result += f"🚦 Class: {vehicle_data.get('Vehicle Class', 'N/A')}\n"
    result += f"⛽ Fuel: {vehicle_data.get('Fuel Type', 'N/A')}\n"
    result += f"📅 Reg Date: {vehicle_data.get('Registration Date', 'N/A')}\n"
    result += f"🏢 RTO: {vehicle_data.get('Registered RTO', 'N/A')}\n"
    result += f"📍 City: {vehicle_data.get('City Name', 'N/A')}\n"
    result += f"📞 Phone: {vehicle_data.get('Phone', 'N/A')}\n"
    result += f"🏥 Insurance: {vehicle_data.get('Insurance Company', 'N/A')}\n"
    result += f"📅 Insurance Upto: {vehicle_data.get('Insurance Upto', 'N/A')}\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_tg_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    tg_result = data.get("data", {}).get("result", {})
    if not tg_result.get("success"):
        return f"❌ No information found for Telegram ID: {term}"
    
    result = f"📱 TG TO NUMBER\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Telegram ID: {term}\n"
    result += f"📞 Mobile: {tg_result.get('number', 'N/A')}\n"
    result += f"🌍 Country: {tg_result.get('country', 'N/A')}\n"
    result += f"📡 Code: {tg_result.get('country_code', 'N/A')}\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_email_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    results = []
    if data.get("data", {}).get("success"):
        results = data["data"].get("result", {}).get("results", [])
    
    if not results:
        return f"❌ No information found for Email: {term}"
    
    first = results[0]
    
    result = f"📧 EMAIL INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Email: {term}\n\n"
    result += f"👤 Name: {first.get('NAME', first.get('name', 'N/A'))}\n"
    result += f"📞 Mobile: {first.get('MOBILE', first.get('mobile', 'N/A'))}\n"
    result += f"📞 Alternate: {first.get('alt', 'N/A')}\n"
    result += f"📡 Carrier: {first.get('circle', 'N/A')}\n"
    address = first.get('ADDRESS', first.get('address', 'N/A')) or 'N/A'
    if len(address) > 60:
        address = address[:57] + '...'
    result += f"📍 Address: {address}\n\n"
    
    total = len(results)
    if total > 1:
        result += f"📚 Total Records: {total}\n"
        result += f"💡 Use /full {term} to see all\n\n"
    
    result += f"⚡ POWERED BY @Leader_jii"
    return result

def format_gst_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    gst_data = data.get("data", {}).get("result", {}).get("data", {})
    if not gst_data:
        return f"❌ No information found for GST: {term}"
    
    result = f"📦 GST INFORMATION\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 GSTIN: {gst_data.get('Gstin', term)}\n\n"
    result += f"👤 Legal Name: {gst_data.get('LegalName', 'N/A')}\n"
    result += f"🏪 Trade Name: {gst_data.get('TradeName', 'N/A')}\n\n"
    result += f"📅 Registration Date: {gst_data.get('DtReg', 'N/A')}\n"
    result += f"📊 Status: {gst_data.get('Status', 'N/A')}\n"
    result += f"📍 Address: {gst_data.get('AddrLoc', 'N/A')}, {gst_data.get('AddrSt', 'N/A')}\n"
    result += f"🏢 State Code: {gst_data.get('StateCode', 'N/A')}\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_ifsc_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    bank_data = data.get("data", {}).get("result", {})
    if not bank_data:
        return f"❌ No information found for IFSC: {term}"
    
    result = f"🏦 IFSC INFORMATION\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 IFSC: {bank_data.get('IFSC', term)}\n\n"
    result += f"🏛️ Bank: {bank_data.get('BANK', 'N/A')}\n"
    result += f"🏢 Branch: {bank_data.get('BRANCH', 'N/A')}\n"
    result += f"🏙️ City: {bank_data.get('CITY', 'N/A')}\n"
    result += f"📍 District: {bank_data.get('DISTRICT', 'N/A')}\n"
    result += f"🗺️ State: {bank_data.get('STATE', 'N/A')}\n\n"
    result += f"📬 Address: {bank_data.get('ADDRESS', 'N/A')}\n"
    result += f"📞 Contact: {bank_data.get('CONTACT', 'N/A')}\n"
    result += f"🔢 MICR: {bank_data.get('MICR', 'N/A')}\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_ration_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    ration_data = data.get("data", {})
    if not ration_data.get("success"):
        return f"❌ No information found for Aadhaar: {term}"
    
    details = ration_data.get("details", {})
    card_info = details.get("card_info", {})
    members = details.get("members", [])
    
    result = f"🪪 RATION CARD INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Aadhaar: {term}\n\n"
    result += f"📇 Card ID: {ration_data.get('ration_card_id', 'N/A')}\n\n"
    result += f"📋 Card Type: {card_info.get('Card Type', 'N/A')}\n"
    result += f"📍 Address: {card_info.get('Address', 'N/A')}\n"
    result += f"🏠 District: {card_info.get('District', 'N/A')}\n"
    result += f"🗺️ State: {card_info.get('State', 'N/A')}\n"
    result += f"📅 Issue Date: {card_info.get('Issue Date', 'N/A')}\n"
    result += f"🏪 FPS: {card_info.get('Home FPS', 'N/A')}\n"
    result += f"📊 Scheme: {card_info.get('Scheme', 'N/A')}\n\n"
    
    if members:
        result += f"👥 FAMILY MEMBERS ({len(members)})\n"
        result += f"━━━━━━━━━━━━━━━━━━\n"
        for i, member in enumerate(members[:5], 1):
            result += f"\n{i}. 👤 {member.get('member_name', 'N/A').upper()}\n"
            result += f"   👨‍👧 Relation: {member.get('relationship', 'N/A')}\n"
            result += f"   🔞 Gender: {member.get('gender', 'N/A')}\n"
            result += f"   🆔 UID: {member.get('uid_masked', 'N/A')}\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_full_ration_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    ration_data = data.get("data", {})
    if not ration_data.get("success"):
        return f"❌ No records found for Aadhaar: {term}"
    
    details = ration_data.get("details", {})
    card_info = details.get("card_info", {})
    members = details.get("members", [])
    monthly_summary = details.get("monthly_summary", [])
    
    result = f"🪪 FULL RATION CARD DETAILS\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Aadhaar: {term}\n"
    result += f"📇 Card ID: {ration_data.get('ration_card_id', 'N/A')}\n"
    result += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    result += f"📋 CARD INFO\n━━━━━━━━━━━━━━━━━━\n"
    result += f"Type: {card_info.get('Card Type', 'N/A')}\n"
    result += f"Scheme: {card_info.get('Scheme', 'N/A')}\n"
    result += f"Issue Date: {card_info.get('Issue Date', 'N/A')}\n"
    result += f"District: {card_info.get('District', 'N/A')}\n"
    result += f"State: {card_info.get('State', 'N/A')}\n"
    result += f"FPS: {card_info.get('Home FPS', 'N/A')}\n"
    result += f"Address: {card_info.get('Address', 'N/A')}\n\n"
    
    if members:
        result += f"👥 ALL MEMBERS ({len(members)})\n"
        result += f"━━━━━━━━━━━━━━━━━━\n"
        for i, member in enumerate(members, 1):
            result += f"\n{i}. 👤 {member.get('member_name', 'N/A').upper()}\n"
            result += f"   Relation: {member.get('relationship', 'N/A')}\n"
            result += f"   Gender: {member.get('gender', 'N/A')}\n"
            result += f"   UID: {member.get('uid_masked', 'N/A')}\n"
            result += f"   Updated: {member.get('cr_last_updated', 'N/A')}\n"
    
    if monthly_summary:
        result += f"\n📆 MONTHLY SUMMARY\n"
        result += f"━━━━━━━━━━━━━━━━━━\n"
        for summary in monthly_summary:
            result += f"• {summary.get('month', 'N/A')}: {summary.get('member_count', 'N/A')} members\n"
    
    result += f"\n⚡ POWERED BY @Leader_jii"
    return result

def format_full_email_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    results = []
    if data.get("data", {}).get("success"):
        results = data["data"].get("result", {}).get("results", [])
    
    if not results:
        return f"❌ No records found for Email: {term}"
    
    total = len(results)
    result = f"📧 FULL EMAIL DETAILS\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Email: {term}\n"
    result += f"📊 Total Records: {total}\n"
    result += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, rec in enumerate(results[:15], 1):
        result += f"▶ Record {i}\n"
        result += f"   👤 Name: {rec.get('NAME', rec.get('name', 'N/A'))}\n"
        result += f"   📞 Mobile: {rec.get('MOBILE', rec.get('mobile', 'N/A'))}\n"
        result += f"   📞 Alt: {rec.get('alt', 'N/A')}\n"
        result += f"   📡 Carrier: {rec.get('circle', 'N/A')}\n"
        address = rec.get('ADDRESS', rec.get('address', 'N/A')) or 'N/A'
        if len(address) > 60:
            address = address[:57] + '...'
        result += f"   📍 Address: {address}\n\n"
    
    if total > 15:
        result += f"⚠️ Showing first 15 of {total} records\n"
    
    result += f"⚡ POWERED BY @Leader_jii"
    return result

# ============ ADMIN FUNCTIONS ============
def show_admin_menu(chat_id):
    """Show admin menu with all options"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📊 Dashboard", "callback_data": "admin_dashboard"}],
            [{"text": "👥 Users List", "callback_data": "admin_users"}],
            [{"text": "📜 Search History", "callback_data": "admin_history"}],
            [{"text": "🔥 Trending", "callback_data": "admin_trending"}],
            [{"text": "🗑️ Remove User", "callback_data": "admin_remove"}],
            [{"text": "📢 Broadcast", "callback_data": "admin_broadcast"}],
            [{"text": "🚪 Logout", "callback_data": "admin_logout"}]
        ]
    }
    msg = f"🔐 <b>ADMIN PANEL</b>\n━━━━━━━━━━━━━━━━━━\n\nWelcome to admin panel!\n\nSelect an option below:"
    send_msg(chat_id, msg, reply_markup=keyboard, parse_mode="HTML")

def show_dashboard(chat_id):
    total_users = len(user_data)
    total_searches = sum(len(u.get("searches", [])) for u in user_data.values())
    
    msg = f"📊 ADMIN DASHBOARD\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"👥 Total Users: {total_users}\n"
    msg += f"🔍 Total Searches: {total_searches}\n"
    msg += f"📊 Trending Numbers: {len(trending_numbers)}\n"
    msg += f"\n⚡ POWERED BY @Leader_jii"
    send_msg(chat_id, msg)
    show_admin_menu(chat_id)

def show_users(chat_id):
    if not user_data:
        send_msg(chat_id, "❌ No users found!")
        show_admin_menu(chat_id)
        return
    
    msg = "👥 USER LIST\n━━━━━━━━━━━━━━━━━━\n\n"
    for i, (cid, data) in enumerate(list(user_data.items())[:20], 1):
        name = data.get("display_name", "Unknown")
        searches = len(data.get("searches", []))
        msg += f"{i}. {name}\n   🔍 {searches} searches\n   🆔 <code>{cid}</code>\n\n"
    
    if len(user_data) > 20:
        msg += f"⚠️ Showing first 20 of {len(user_data)} users"
    
    msg += f"\n⚡ POWERED BY @Leader_jii"
    send_msg(chat_id, msg)
    show_admin_menu(chat_id)

def show_all_history(chat_id):
    all_searches = []
    for cid, data in user_data.items():
        for s in data.get("searches", []):
            name = data.get("display_name", "Unknown")
            all_searches.append(f"{name}: [{s.get('type', 'Unknown')}] {s.get('term', 'N/A')} - {s.get('time', 'N/A')}")
    
    if all_searches:
        msg = "📜 LAST 30 SEARCHES\n━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(all_searches[-30:])
        msg += f"\n\n⚡ POWERED BY @Leader_jii"
        send_msg(chat_id, msg)
    else:
        send_msg(chat_id, "❌ No history found!")
    show_admin_menu(chat_id)

def get_trending():
    if not trending_numbers:
        return "📊 No trending data yet!"
    
    sorted_trend = sorted(trending_numbers.items(), key=lambda x: x[1], reverse=True)[:10]
    msg = "🔥 TRENDING NUMBERS\n━━━━━━━━━━━━━━━━━━\n\n"
    for i, (num, count) in enumerate(sorted_trend, 1):
        msg += f"{i}. <code>{num}</code> - {count} searches\n"
    
    msg += f"\n⚡ POWERED BY @Leader_jii"
    return msg

def remove_user(chat_id, target_id):
    target = str(target_id).strip()
    if target in user_data:
        name = user_data[target].get("display_name", "Unknown")
        del user_data[target]
        save_data()
        send_msg(chat_id, f"✅ Removed user '{name}'!")
    else:
        send_msg(chat_id, f"❌ User {target} not found!")
    show_admin_menu(chat_id)

def broadcast_msg(chat_id, msg_text):
    if not user_data:
        send_msg(chat_id, "❌ No users found!")
        show_admin_menu(chat_id)
        return
    
    send_msg(chat_id, f"⏳ Sending to {len(user_data)} users...")
    sent = 0
    
    for cid in user_data.keys():
        try:
            if send_msg(int(cid), f"📢 BROADCAST\n\n{msg_text}\n\n⚡ POWERED BY @Leader_jii"):
                sent += 1
            time.sleep(0.05)
        except:
            pass
    
    send_msg(chat_id, f"✅ Sent to {sent}/{len(user_data)} users")
    show_admin_menu(chat_id)

# ============ SMS FLOW ============
def handle_sms_command(chat_id, text):
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        send_msg(chat_id, "❌ Usage: /sms 9876543210 Your message here")
        return
    
    number = parts[0].strip()
    message = parts[1].strip()
    
    if not number.isdigit() or len(number) != 10:
        send_msg(chat_id, "❌ Please enter a valid 10-digit number!")
        return
    
    if not message:
        send_msg(chat_id, "❌ Please enter a message to send!")
        return
    
    send_msg(chat_id, f"📱 Sending SMS to {number}...\n\n⏳ Please wait...")
    result = call_sms_api(number, message)
    send_msg(chat_id, format_sms_result(result, number, message))

# ============ COMMAND HANDLERS ============
def handle_full_command(chat_id, text):
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        send_msg(chat_id, "❌ Usage:\n/full 9876543210\n/full 123412341234\n/full test@gmail.com")
        return
    
    query = parts[1].strip()
    
    if query.isdigit() and len(query) == 10:
        send_msg(chat_id, f"🔍 Fetching all records for number: {query}...")
        result = call_universal_api("NUMBER", query)
        send_msg(chat_id, format_full_number_result(result, query))
    
    elif query.isdigit() and len(query) == 12:
        send_msg(chat_id, f"🔍 Fetching full ration card details for: {query}...")
        result = call_universal_api("AADHAAR", query)
        send_msg(chat_id, format_full_ration_result(result, query))
    
    elif '@' in query and '.' in query:
        send_msg(chat_id, f"🔍 Fetching all records for Email: {query}...")
        result = call_universal_api("EMAIL", query)
        send_msg(chat_id, format_full_email_result(result, query))
    
    else:
        send_msg(chat_id, "❌ Invalid!\n\nUse:\n/full 9876543210\n/full 123412341234\n/full test@gmail.com")

def handle_num_command(chat_id, number):
    if not number.isdigit() or len(number) != 10:
        send_msg(chat_id, "❌ Please enter a valid 10-digit number!")
        return
    
    send_msg(chat_id, f"🔍 Searching number: {number}...")
    result = call_universal_api("NUMBER", number)
    send_msg(chat_id, format_number_result(result, number))

def handle_ip_command(chat_id, ip):
    send_msg(chat_id, f"🔍 Searching IP: {ip}...")
    result = call_universal_api("IP", ip)
    send_msg(chat_id, format_ip_result(result, ip))

def handle_vehicle_command(chat_id, vehicle):
    vehicle = vehicle.upper()
    send_msg(chat_id, f"🔍 Searching vehicle: {vehicle}...")
    result = call_universal_api("VEHICLE", vehicle)
    send_msg(chat_id, format_vehicle_result(result, vehicle))

def handle_tgnum_command(chat_id, tg_id):
    send_msg(chat_id, f"🔍 Searching Telegram ID: {tg_id}...")
    result = call_universal_api("TGNUMBER", tg_id)
    send_msg(chat_id, format_tg_result(result, tg_id))

def handle_email_command(chat_id, email):
    send_msg(chat_id, f"🔍 Searching email: {email}...")
    result = call_universal_api("EMAIL", email)
    send_msg(chat_id, format_email_result(result, email))

def handle_gst_command(chat_id, gst):
    gst = gst.upper()
    send_msg(chat_id, f"🔍 Searching GST: {gst}...")
    result = call_universal_api("GST", gst)
    send_msg(chat_id, format_gst_result(result, gst))

def handle_ifsc_command(chat_id, ifsc):
    ifsc = ifsc.upper()
    send_msg(chat_id, f"🔍 Searching IFSC: {ifsc}...")
    result = call_universal_api("IFSC", ifsc)
    send_msg(chat_id, format_ifsc_result(result, ifsc))

def handle_ration_command(chat_id, aadhaar):
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        send_msg(chat_id, "❌ Please enter a valid 12-digit Aadhaar number!")
        return
    
    send_msg(chat_id, f"🔍 Searching ration card for Aadhaar: {aadhaar}...")
    result = call_universal_api("AADHAAR", aadhaar)
    send_msg(chat_id, format_ration_result(result, aadhaar))

# ============ MAIN HANDLER ============
def handle_update(update):
    global OFFSET
    
    # Handle callback queries
    if "callback_query" in update:
        callback = update["callback_query"]
        callback_id = callback["id"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback.get("data", "")
        
        if data == "check_membership":
            c1_joined, c2_joined = check_force_join_both(chat_id)
            if c1_joined and c2_joined:
                send_callback(chat_id, "✅ Both channels joined! You can now use the bot.", callback_id)
                send_msg(chat_id, "✅ <b>Access Granted!</b>\n\nYou can now use all bot features.\n\nType /help to see commands.", parse_mode="HTML")
            else:
                send_callback(chat_id, "❌ Please join both channels first!", callback_id)
                send_force_join_message(chat_id, c1_joined, c2_joined)
            return
        
        # Admin callback handlers
        if data == "admin_dashboard":
            show_dashboard(chat_id)
        elif data == "admin_users":
            show_users(chat_id)
        elif data == "admin_history":
            show_all_history(chat_id)
        elif data == "admin_trending":
            send_msg(chat_id, get_trending())
            show_admin_menu(chat_id)
        elif data == "admin_remove":
            send_msg(chat_id, "🗑️ Send user ID to remove:\nType /cancel to cancel")
            admin_session[str(chat_id)] = {"remove_mode": True}
        elif data == "admin_broadcast":
            send_msg(chat_id, "📢 Send message to broadcast:\nType /cancel to cancel")
            admin_session[str(chat_id)] = {"broadcast_mode": True}
        elif data == "admin_logout":
            if str(chat_id) in admin_session:
                del admin_session[str(chat_id)]
            send_msg(chat_id, "👋 Logged out from admin!")
        
        send_callback(chat_id, "", callback_id)
        return
    
    if "message" not in update:
        return
    
    msg = update["message"]
    if not isinstance(msg, dict):
        return
    
    chat_id = msg.get("chat", {}).get("id", 0)
    text = msg.get("text", "")
    user_id = msg.get("from", {}).get("id", 0)
    user_info = msg.get("chat", {})
    
    print(f"📨 {user_info.get('first_name', 'User')} | {text[:50] if text else 'No text'}")
    
    # ============ GROUP HANDLER - IGNORE NON-COMMAND MESSAGES ============
    is_group = chat_id < 0
    
    if is_group:
        # In groups, ONLY respond to messages that start with /
        if not text or not text.startswith("/"):
            return  # Silently ignore non-command messages in groups
    
    # ============ FORCE JOIN CHECK (only for private chats OR command messages) ============
    # For groups: Only check force join if it's a command
    # For private: Always check force join
    if not is_group or (is_group and text and text.startswith("/")):
        # Skip force join for admin login and /admin command
        if text != ADMIN_PASSWORD and text != "/admin" and not text.startswith("/admin "):
            c1_joined, c2_joined = check_force_join_both(user_id)
            if not (c1_joined and c2_joined):
                send_force_join_message(chat_id, c1_joined, c2_joined)
                return
    
    # ============ UPDATE STATS ============
    update_stats(chat_id, user_info)
    admin = is_admin(chat_id)
    
    # ============ HANDLE PENDING ADMIN LOGIN ============
    if str(chat_id) in pending_admin_login:
        if text == ADMIN_PASSWORD:
            admin_session[str(chat_id)] = {}
            del pending_admin_login[str(chat_id)]
            send_msg(chat_id, "✅ <b>Admin access granted!</b>\n\nWelcome to admin panel!", parse_mode="HTML")
            show_admin_menu(chat_id)
        else:
            send_msg(chat_id, f"❌ Wrong password!\n\nAccess denied.")
            del pending_admin_login[str(chat_id)]
        return
    
    # ============ COMMAND HANDLING ============
    # Admin command - ask for password first
    if text == "/admin":
        if admin:
            show_admin_menu(chat_id)
        else:
            pending_admin_login[str(chat_id)] = True
            send_msg(chat_id, "🔐 <b>ADMIN LOGIN</b>\n━━━━━━━━━━━━━━━━━━\n\nPlease enter the admin password to continue.\n\nType /cancel to cancel.", parse_mode="HTML")
        return
    
    # Cancel admin login
    if text == "/cancel" and str(chat_id) in pending_admin_login:
        del pending_admin_login[str(chat_id)]
        send_msg(chat_id, "❌ Login cancelled!")
        return
    
    # Hidden admin login via direct password (for backward compatibility)
    if text == ADMIN_PASSWORD and not admin:
        admin_session[str(chat_id)] = {}
        send_msg(chat_id, "✅ <b>Admin access granted!</b>\n\nType /admin to open admin panel.", parse_mode="HTML")
        return
    
    # SMS Command
    if text.startswith("/sms"):
        cmd_parts = text.split(maxsplit=2)
        if len(cmd_parts) >= 3:
            handle_sms_command(chat_id, f"{cmd_parts[1]} {cmd_parts[2]}")
        else:
            send_msg(chat_id, "❌ Usage: /sms 9876543210 Your message here")
        return
    
    # Full Command
    if text.startswith("/full"):
        handle_full_command(chat_id, text)
        return
    
    # Num Command
    if text.startswith("/num"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_num_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /num 9876543210")
        return
    
    # IP Command
    if text.startswith("/ip"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_ip_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /ip 8.8.8.8")
        return
    
    # Vehicle Command
    if text.startswith("/vehicle"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_vehicle_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /vehicle GJ08CJ7132")
        return
    
    # TG to Number Command
    if text.startswith("/tgnum"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_tgnum_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /tgnum 8490678882")
        return
    
    # Email Command
    if text.startswith("/email"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_email_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /email test@gmail.com")
        return
    
    # GST Command
    if text.startswith("/gst"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_gst_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /gst 22AAAAA0000A1Z")
        return
    
    # IFSC Command
    if text.startswith("/ifsc"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_ifsc_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /ifsc SBIN0000001")
        return
    
    # Ration Command
    if text.startswith("/ration"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_ration_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /ration 123412341234")
        return
    
    # ============ ADMIN MODES ============
    if admin and admin_session.get(str(chat_id), {}).get("remove_mode"):
        if text == "/cancel":
            admin_session[str(chat_id)]["remove_mode"] = False
            send_msg(chat_id, "❌ Cancelled!")
            show_admin_menu(chat_id)
        elif text and text.isdigit():
            remove_user(chat_id, text)
            admin_session[str(chat_id)]["remove_mode"] = False
        return
    
    if admin and admin_session.get(str(chat_id), {}).get("broadcast_mode"):
        if text == "/cancel":
            admin_session[str(chat_id)]["broadcast_mode"] = False
            send_msg(chat_id, "❌ Cancelled!")
            show_admin_menu(chat_id)
        elif text:
            broadcast_msg(chat_id, text)
            admin_session[str(chat_id)]["broadcast_mode"] = False
        return
    
    # ============ DIRECT NUMBER INPUT (PRIVATE CHAT ONLY) ============
    if not is_group and text and text.isdigit() and len(text) == 10:
        handle_num_command(chat_id, text)
        return
    
    # ============ HELP / START ============
    if text == "/start" or text == "/help":
        welcome_msg = (
            f"🎉 <b>WELCOME TO INFO BOT!</b> 🎉\n\n"
            f"📱 <b>MULTI INFO BOT</b>\n\n"
            f"✨ <b>Available Commands:</b>\n\n"
            f"📞 <code>/num 9876543210</code> - Mobile number info\n"
            f"🌐 <code>/ip 8.8.8.8</code> - IP address details\n"
            f"🚗 <code>/vehicle GJ08CJ7132</code> - Vehicle info\n"
            f"📱 <code>/tgnum 8490678882</code> - TG ID to number\n"
            f"📧 <code>/email test@gmail.com</code> - Email lookup\n"
            f"📦 <code>/gst 22AAAAA0000A1Z</code> - GST info\n"
            f"🏦 <code>/ifsc SBIN0000001</code> - IFSC lookup\n"
            f"🪪 <code>/ration 123412341234</code> - Ration card\n"
            f"📱 <code>/sms 9876543210 Hello</code> - Send SMS\n"
            f"📚 <code>/full [query]</code> - All records\n\n"
            f"📌 <b>Send any 10-digit number directly in private chat!</b>\n\n"
            f"⚡ <b>Powered by @Leader_jii</b>"
        )
        send_msg(chat_id, welcome_msg, parse_mode="HTML")
        return
    
    # ============ IGNORE ANYTHING ELSE IN GROUPS ============
    if is_group:
        return  # Silently ignore any non-command messages in groups
    
    # For private chat - unknown command
    if text and not text.startswith("/"):
        send_msg(chat_id, "❌ Invalid command!\n\nType /help to see available commands.")

# ============ MAIN ============
def main():
    load_data()
    Thread(target=run_health_server, daemon=True).start()
    
    print("=" * 60)
    print("🤖 MULTI INFO BOT STARTED")
    print("=" * 60)
    print(f"👥 Loaded users: {len(user_data)}")
    print(f"👨‍💻 Powered by: {DEVELOPER_USERNAME}")
    print(f"🔐 Admin Password: {ADMIN_PASSWORD}")
    print("=" * 60)
    print("📌 FORCE JOIN ENABLED FOR BOTH CHANNELS:")
    print(f"   1. {CHANNEL_1_NAME} - {CHANNEL_1_LINK}")
    print(f"   2. {CHANNEL_2_NAME} - {CHANNEL_2_LINK}")
    print("=" * 60)
    print("📌 Admin Access: Type /admin and enter password: #zyro2000")
    print("📌 GROUPS: Bot only responds to commands (messages starting with /)")
    print("📌 Normal messages in groups are IGNORED")
    print("=" * 60)
    
    global OFFSET
    while True:
        try:
            resp = requests.get(f"{BASE_URL}/getUpdates", 
                               params={"offset": OFFSET, "timeout": 30}, timeout=35)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        if isinstance(update, dict):
                            handle_update(update)
                            OFFSET = update.get("update_id", OFFSET) + 1
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n👋 Bot stopped!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
