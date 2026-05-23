#!/usr/bin/env python3
"""
UNIVERSAL INFO BOT
Powered by @LEADER_JII
Force Join: @modxpatel & @ajaaobkl
"""

import requests
import json
import time
from datetime import datetime
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================= CONFIGURATION =================
BOT_TOKEN = "8757635805:AAGhawULq3hocLx7-bPCsiIVs5k2e5bV-EU"
DEVELOPER_USERNAME = "@LEADER_JII"

# API Configuration
API_BASE_URL = "https://all-sigma-pad-api-damo-5-day.vercel.app/api"
API_KEY = "RAJAN99"

# Channel info for FORCE JOIN
CHANNEL_1_NAME = "MOD X PATEL"
CHANNEL_1_LINK = "https://t.me/modxpatel"
CHANNEL_1_USERNAME = "modxpatel"

CHANNEL_2_NAME = "ALL ILLEGAL STUFFS"
CHANNEL_2_LINK = "https://t.me/ajaaobkl"
CHANNEL_2_USERNAME = "ajaaobkl"
# =================================================

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OFFSET = 0

user_data = {}

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
def send_msg(chat_id, text, reply_markup=None, parse_mode="HTML", reply_to=None):
    url = f"{BASE_URL}/sendMessage"
    
    try:
        chat_id = int(chat_id)
    except:
        pass
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
        "allow_sending_without_reply": True
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def edit_msg(chat_id, msg_id, text, reply_markup=None):
    url = f"{BASE_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

def send_callback(chat_id, text, callback_id):
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id, "text": text, "show_alert": False}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# ============ FORCE JOIN CHECK ============
def check_channel_join(user_id, channel_username):
    try:
        url = f"{BASE_URL}/getChatMember"
        payload = {"chat_id": f"@{channel_username}", "user_id": user_id}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                status = data.get("result", {}).get("status", "")
                if status in ["member", "administrator", "creator"]:
                    return True
        return False
    except:
        return False

def check_both_channels(user_id):
    c1 = check_channel_join(user_id, CHANNEL_1_USERNAME)
    c2 = check_channel_join(user_id, CHANNEL_2_USERNAME)
    return c1, c2

def get_force_join_keyboard(c1_joined=False, c2_joined=False):
    buttons = []
    
    if not c1_joined:
        buttons.append([{"text": f"📢 JOIN {CHANNEL_1_NAME}", "url": CHANNEL_1_LINK}])
    if not c2_joined:
        buttons.append([{"text": f"📢 JOIN {CHANNEL_2_NAME}", "url": CHANNEL_2_LINK}])
    
    buttons.append([{"text": "✅ CHECK MEMBERSHIP", "callback_data": "verify_join"}])
    
    return {"inline_keyboard": buttons}

def send_force_join_message(chat_id, c1_joined, c2_joined):
    status_msg = ""
    
    if c1_joined:
        status_msg += f"\n✅ {CHANNEL_1_NAME} - Joined"
    else:
        status_msg += f"\n❌ {CHANNEL_1_NAME} - Not joined"
    
    if c2_joined:
        status_msg += f"\n✅ {CHANNEL_2_NAME} - Joined"
    else:
        status_msg += f"\n❌ {CHANNEL_2_NAME} - Not joined"
    
    msg = f"⚠️ <b>ACCESS DENIED</b> ⚠️\n\nYou must join BOTH channels to use this bot!\n\n📢 <b>Channels Status:</b>{status_msg}\n\n👇 Click below to join and then verify."
    
    send_msg(chat_id, msg, get_force_join_keyboard(c1_joined, c2_joined))

# ============ API CALL ============
def call_api(api_type, term):
    try:
        url = f"{API_BASE_URL}?key={API_KEY}&type={api_type}&term={term}"
        print(f"📡 API: {url}")
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ============ FORMATTERS ============
def format_number_result(data, number):
    """Single record - for /num command"""
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    results = []
    if data.get("data", {}).get("result", {}).get("results"):
        results = data["data"]["result"]["results"]
    elif data.get("data", {}).get("success") and isinstance(data.get("data"), dict):
        if "result" in data["data"] and "results" in data["data"]["result"]:
            results = data["data"]["result"]["results"]
    
    if not results:
        return f"❌ No information found for {number}"
    
    first = results[0]
    total = len(results)
    
    msg = f"📞 NUMBER INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 Number: {number}\n\n"
    msg += f"👤 Name: {first.get('NAME', first.get('name', 'N/A'))}\n\n"
    msg += f"👨 Father: {first.get('fname', 'N/A')}\n\n"
    msg += f"🆔 Aadhaar: {first.get('id', 'N/A')}\n\n"
    msg += f"📞 Alternate: {first.get('alt', 'N/A')}\n\n"
    msg += f"📡 Carrier: {first.get('circle', 'N/A')}\n\n"
    msg += f"📧 Email: {first.get('email', 'N/A') or 'N/A'}\n\n"
    msg += f"📍 Address: {(first.get('ADDRESS', first.get('address', 'N/A')))[:100]}\n\n"
    
    if total > 1:
        msg += f"📚 Total Records: {total}\n"
        msg += f"💡 Use /full {number} to see all\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_full_number_result(data, number):
    """All records - for /full command"""
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    results = []
    if data.get("data", {}).get("result", {}).get("results"):
        results = data["data"]["result"]["results"]
    elif data.get("data", {}).get("success") and isinstance(data.get("data"), dict):
        if "result" in data["data"] and "results" in data["data"]["result"]:
            results = data["data"]["result"]["results"]
    
    if not results:
        return f"❌ No records found for {number}"
    
    total = len(results)
    msg = f"📞 FULL NUMBER DETAILS\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 Number: {number}\n"
    msg += f"📊 Total Records: {total}\n"
    msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, rec in enumerate(results[:20], 1):
        msg += f"▶ Record {i}\n"
        msg += f"   👤 Name: {rec.get('NAME', rec.get('name', 'N/A'))}\n"
        msg += f"   👨 Father: {rec.get('fname', 'N/A')}\n"
        msg += f"   🆔 Aadhaar: {rec.get('id', 'N/A')}\n"
        msg += f"   📞 Alt: {rec.get('alt', 'N/A')}\n"
        msg += f"   📡 Carrier: {rec.get('circle', 'N/A')}\n"
        address = rec.get('ADDRESS', rec.get('address', 'N/A')) or 'N/A'
        if len(address) > 80:
            address = address[:77] + '...'
        msg += f"   📍 Address: {address}\n\n"
    
    if total > 20:
        msg += f"⚠️ Showing first 20 of {total} records\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_aadhaar_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    ration_data = data.get("data", {})
    if not ration_data.get("success"):
        return f"❌ No Ration Card found for Aadhaar: {term}"
    
    details = ration_data.get("details", {})
    card_info = details.get("card_info", {})
    members = details.get("members", [])
    
    msg = f"🪪 RATION CARD INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 Aadhaar: {term}\n\n"
    msg += f"📇 Card ID: {ration_data.get('ration_card_id', 'N/A')}\n\n"
    msg += f"📋 Card Type: {card_info.get('Card Type', 'N/A')}\n\n"
    msg += f"📊 Scheme: {card_info.get('Scheme', 'N/A')}\n\n"
    msg += f"📍 Address: {card_info.get('Address', 'N/A')}\n\n"
    msg += f"🏠 District: {card_info.get('District', 'N/A')}\n\n"
    msg += f"🗺️ State: {card_info.get('State', 'N/A')}\n\n"
    msg += f"📅 Issue Date: {card_info.get('Issue Date', 'N/A')}\n\n"
    msg += f"🏪 FPS: {card_info.get('Home FPS', 'N/A')}\n\n"
    
    if members:
        msg += f"👥 FAMILY MEMBERS ({len(members)})\n"
        msg += f"━━━━━━━━━━━━━━━━━━\n"
        for i, member in enumerate(members[:5], 1):
            msg += f"{i}. 👤 {member.get('member_name', 'N/A').upper()}\n"
            msg += f"   👨‍👧 Relation: {member.get('relationship', 'N/A')}\n"
            msg += f"   🔞 Gender: {member.get('gender', 'N/A')}\n"
            msg += f"   🆔 UID: {member.get('uid_masked', 'N/A')}\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_vehicle_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    vehicle_data = data.get("data", {})
    if not vehicle_data:
        return f"❌ No information found for vehicle: {term.upper()}"
    
    msg = f"🚗 VEHICLE INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 Vehicle: {term.upper()}\n\n"
    msg += f"👤 Owner: {vehicle_data.get('Owner Name', 'N/A')}\n"
    msg += f"🏭 Model: {vehicle_data.get('Model Name', 'N/A')}\n"
    msg += f"📅 Reg Date: {vehicle_data.get('Registration Date', 'N/A')}\n"
    msg += f"🏢 RTO: {vehicle_data.get('Registered RTO', 'N/A')}\n"
    msg += f"📍 City: {vehicle_data.get('City Name', 'N/A')}\n"
    msg += f"⛽ Fuel: {vehicle_data.get('Fuel Type', 'N/A')}\n"
    msg += f"🏥 Insurance: {vehicle_data.get('Insurance Company', 'N/A')}\n"
    msg += f"📅 Insurance Upto: {vehicle_data.get('Insurance Upto', 'N/A')}\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_gst_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    gst_data = data.get("data", {}).get("result", {}).get("data", {})
    if not gst_data:
        return f"❌ No information found for GST: {term}"
    
    msg = f"📦 GST INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 GSTIN: {term}\n\n"
    msg += f"👤 Legal Name: {gst_data.get('LegalName', 'N/A')}\n"
    msg += f"🏪 Trade Name: {gst_data.get('TradeName', 'N/A')}\n"
    msg += f"📅 Reg Date: {gst_data.get('DtReg', 'N/A')}\n"
    msg += f"📊 Status: {gst_data.get('Status', 'N/A')}\n"
    msg += f"📍 Address: {gst_data.get('AddrLoc', 'N/A')}\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_ifsc_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    bank_data = data.get("data", {}).get("result", {})
    if not bank_data:
        return f"❌ No information found for IFSC: {term}"
    
    msg = f"🏦 IFSC INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 IFSC: {term}\n\n"
    msg += f"🏛️ Bank: {bank_data.get('BANK', 'N/A')}\n"
    msg += f"🏢 Branch: {bank_data.get('BRANCH', 'N/A')}\n"
    msg += f"🏙️ City: {bank_data.get('CITY', 'N/A')}\n"
    msg += f"📍 District: {bank_data.get('DISTRICT', 'N/A')}\n"
    msg += f"🗺️ State: {bank_data.get('STATE', 'N/A')}\n"
    msg += f"📬 Address: {bank_data.get('ADDRESS', 'N/A')}\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_ip_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    ip_data = data.get("data", {}).get("result", {})
    if not ip_data:
        return f"❌ No information found for IP: {term}"
    
    msg = f"🌐 IP INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 IP: {term}\n\n"
    msg += f"📍 Location: {ip_data.get('City', 'N/A')}, {ip_data.get('Region', 'N/A')}\n"
    msg += f"🌍 Country: {ip_data.get('Country', 'N/A')}\n"
    msg += f"🏢 ISP: {ip_data.get('ISP', 'N/A')}\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_email_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    results = []
    if data.get("data", {}).get("result", {}).get("results"):
        results = data["data"]["result"]["results"]
    
    if not results:
        return f"❌ No information found for Email: {term}"
    
    msg = f"📧 EMAIL INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 Email: {term}\n"
    msg += f"📊 Total Records: {len(results)}\n\n"
    
    for i, rec in enumerate(results[:3], 1):
        msg += f"▶ Record {i}\n"
        msg += f"   👤 Name: {rec.get('NAME', 'N/A')}\n"
        msg += f"   📞 Mobile: {rec.get('MOBILE', 'N/A')}\n"
        msg += f"   📍 Address: {(rec.get('ADDRESS', 'N/A'))[:60]}\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

def format_tg_result(data, term):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    tg_result = data.get("data", {}).get("result", {})
    if not tg_result.get("success"):
        return f"❌ No information found for Telegram ID: {term}"
    
    msg = f"📱 TG TO NUMBER\n━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🎯 Telegram ID: {term}\n"
    msg += f"📞 Mobile: {tg_result.get('number', 'N/A')}\n"
    msg += f"🌍 Country: {tg_result.get('country', 'N/A')}\n\n"
    
    msg += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return msg

# ============ COMMAND HANDLERS ============
def handle_start(chat_id, user_id):
    c1, c2 = check_both_channels(user_id)
    if not (c1 and c2):
        send_force_join_message(chat_id, c1, c2)
        return
    
    msg = f"""🎉 <b>WELCOME TO UNIVERSAL INFO BOT!</b> 🎉

📌 <b>Available Commands:</b>

🔹 <code>/num 9876543210</code> - Number details (1 record)
🔹 <code>/full 9876543210</code> - All number records
🔹 <code>/aadhaar 123412341234</code> - Ration Card info
🔹 <code>/vehicle UP92P2111</code> - Vehicle info
🔹 <code>/gst 10DJCPK4351Q1Z5</code> - GST info
🔹 <code>/ifsc SBIN0000001</code> - Bank IFSC info
🔹 <code>/ip 8.8.8.8</code> - IP geolocation
🔹 <code>/email test@gmail.com</code> - Email lookup
🔹 <code>/tg @username</code> - TG to Number

⚡ POWERED BY {DEVELOPER_USERNAME}"""
    
    send_msg(chat_id, msg)

def handle_command(chat_id, user_id, cmd, arg, msg_id=None, is_group=False):
    # Check force join first
    c1, c2 = check_both_channels(user_id)
    if not (c1 and c2):
        send_force_join_message(chat_id, c1, c2)
        return
    
    if not arg:
        send_msg(chat_id, f"❌ Usage: /{cmd} <value>", reply_to=msg_id if is_group else None)
        return
    
    if cmd == "num":
        if not arg.isdigit() or len(arg) != 10:
            send_msg(chat_id, "❌ Please enter a valid 10-digit number!", reply_to=msg_id if is_group else None)
            return
        send_msg(chat_id, f"🔍 Fetching number info for {arg}...")
        result = call_api("NUMBER", arg)
        send_msg(chat_id, format_number_result(result, arg), reply_to=msg_id if is_group else None)
    
    elif cmd == "full":
        if not arg.isdigit() or len(arg) != 10:
            send_msg(chat_id, "❌ Please enter a valid 10-digit number!", reply_to=msg_id if is_group else None)
            return
        send_msg(chat_id, f"🔍 Fetching all records for {arg}...")
        result = call_api("NUMBER", arg)
        full_msg = format_full_number_result(result, arg)
        # Split if too long
        if len(full_msg) > 4000:
            for i in range(0, len(full_msg), 4000):
                send_msg(chat_id, full_msg[i:i+4000], reply_to=msg_id if is_group and i==0 else None)
        else:
            send_msg(chat_id, full_msg, reply_to=msg_id if is_group else None)
    
    elif cmd == "aadhaar":
        if not arg.isdigit() or len(arg) != 12:
            send_msg(chat_id, "❌ Please enter a valid 12-digit Aadhaar number!", reply_to=msg_id if is_group else None)
            return
        send_msg(chat_id, f"🔍 Fetching Ration Card info for Aadhaar: {arg}...")
        result = call_api("AADHAAR", arg)
        send_msg(chat_id, format_aadhaar_result(result, arg), reply_to=msg_id if is_group else None)
    
    elif cmd == "vehicle":
        send_msg(chat_id, f"🔍 Fetching vehicle info for {arg.upper()}...")
        result = call_api("VEHICLE", arg)
        send_msg(chat_id, format_vehicle_result(result, arg), reply_to=msg_id if is_group else None)
    
    elif cmd == "gst":
        send_msg(chat_id, f"🔍 Fetching GST info for {arg.upper()}...")
        result = call_api("GST", arg)
        send_msg(chat_id, format_gst_result(result, arg), reply_to=msg_id if is_group else None)
    
    elif cmd == "ifsc":
        send_msg(chat_id, f"🔍 Fetching IFSC info for {arg.upper()}...")
        result = call_api("IFSC", arg)
        send_msg(chat_id, format_ifsc_result(result, arg), reply_to=msg_id if is_group else None)
    
    elif cmd == "ip":
        send_msg(chat_id, f"🔍 Fetching IP info for {arg}...")
        result = call_api("IP", arg)
        send_msg(chat_id, format_ip_result(result, arg), reply_to=msg_id if is_group else None)
    
    elif cmd == "email":
        if '@' not in arg:
            send_msg(chat_id, "❌ Please enter a valid email address!", reply_to=msg_id if is_group else None)
            return
        send_msg(chat_id, f"🔍 Fetching email info for {arg}...")
        result = call_api("EMAIL", arg)
        send_msg(chat_id, format_email_result(result, arg), reply_to=msg_id if is_group else None)
    
    elif cmd == "tg":
        send_msg(chat_id, f"🔍 Fetching number for {arg}...")
        result = call_api("TGNUMBER", arg)
        send_msg(chat_id, format_tg_result(result, arg), reply_to=msg_id if is_group else None)
    
    else:
        send_msg(chat_id, f"❌ Unknown command: /{cmd}\n\nUse /start to see available commands.", reply_to=msg_id if is_group else None)

# ============ MAIN HANDLER ============
def handle_update(update):
    global OFFSET
    
    # Handle callback queries
    if "callback_query" in update:
        callback = update["callback_query"]
        callback_id = callback["id"]
        chat_id = callback["message"]["chat"]["id"]
        msg_id = callback["message"]["message_id"]
        user_id = callback["from"]["id"]
        data = callback.get("data", "")
        
        if data == "verify_join":
            c1, c2 = check_both_channels(user_id)
            if c1 and c2:
                send_callback(chat_id, "✅ Access granted! You can now use the bot.", callback_id)
                edit_msg(chat_id, msg_id, f"✅ <b>ACCESS GRANTED!</b>\n\nWelcome! Use /start to see commands.\n\n⚡ POWERED BY {DEVELOPER_USERNAME}")
            else:
                send_callback(chat_id, "❌ Please join both channels first!", callback_id)
                status_msg = ""
                if c1:
                    status_msg += f"\n✅ {CHANNEL_1_NAME} - Joined"
                else:
                    status_msg += f"\n❌ {CHANNEL_1_NAME} - Not joined"
                if c2:
                    status_msg += f"\n✅ {CHANNEL_2_NAME} - Joined"
                else:
                    status_msg += f"\n❌ {CHANNEL_2_NAME} - Not joined"
                
                msg_text = f"⚠️ <b>ACCESS DENIED</b> ⚠️\n\nYou must join BOTH channels!\n\n📢 <b>Status:</b>{status_msg}\n\n👇 Join and click VERIFY again."
                edit_msg(chat_id, msg_id, msg_text, get_force_join_keyboard(c1, c2))
        return
    
    if "message" not in update:
        return
    
    msg = update["message"]
    chat_id = msg.get("chat", {}).get("id", 0)
    text = msg.get("text", "")
    user_id = msg.get("from", {}).get("id", 0)
    msg_id = msg.get("message_id", 0)
    chat_type = msg.get("chat", {}).get("type", "private")
    
    is_group = chat_type in ["group", "supergroup"]
    
    # In groups, only reply to commands
    if is_group and not text.startswith("/"):
        return
    
    print(f"📨 {user_id}: {text[:50] if text else 'No text'}")
    
    # Handle commands
    if text.startswith("/start"):
        handle_start(chat_id, user_id)
    
    elif text.startswith("/num"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "num", arg, msg_id, is_group)
    
    elif text.startswith("/full"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "full", arg, msg_id, is_group)
    
    elif text.startswith("/aadhaar"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "aadhaar", arg, msg_id, is_group)
    
    elif text.startswith("/vehicle"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "vehicle", arg, msg_id, is_group)
    
    elif text.startswith("/gst"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "gst", arg, msg_id, is_group)
    
    elif text.startswith("/ifsc"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "ifsc", arg, msg_id, is_group)
    
    elif text.startswith("/ip"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "ip", arg, msg_id, is_group)
    
    elif text.startswith("/email"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "email", arg, msg_id, is_group)
    
    elif text.startswith("/tg"):
        parts = text.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ""
        handle_command(chat_id, user_id, "tg", arg, msg_id, is_group)
    
    elif text.startswith("/"):
        send_msg(chat_id, f"❌ Unknown command.\n\nUse /start to see available commands.", reply_to=msg_id if is_group else None)

# ============ MAIN ============
def main():
    Thread(target=run_health_server, daemon=True).start()
    
    print("=" * 50)
    print("🤖 UNIVERSAL INFO BOT")
    print(f"👨‍💻 Powered by: {DEVELOPER_USERNAME}")
    print(f"📢 Force Join: @modxpatel & @ajaaobkl")
    print("=" * 50)
    print("Commands: /num, /full, /aadhaar, /vehicle, /gst, /ifsc, /ip, /email, /tg")
    print("=" * 50)
    
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
