import requests
import json
import time
from datetime import datetime
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib3
import warnings

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

# ================= CONFIGURATION =================
BOT_TOKEN = "7527091387:AAGYxbCeX-JZDYdgcBt1etLmp0sPkdpAepc"
ADMIN_PASSWORD = "#zyro2000"
DEVELOPER_USERNAME = "@LEADER_JIIII"

# Channel info with FORCE JOIN for BOTH channels
CHANNEL_1_NAME = "ALL ILLEGAL STUFFS"
CHANNEL_1_LINK = "https://t.me/ajaaobkl"
CHANNEL_1_USERNAME = "ajaaobkl"

CHANNEL_2_NAME = "MOD X PATEL"
CHANNEL_2_LINK = "https://t.me/Mod_x_patel"
CHANNEL_2_USERNAME = "Mod_x_patel"

# Number API 
NUMBER_API_URL = "https://number-info-api-a5va.vercel.app/api"
# =================================================

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OFFSET = 0

user_data = {}
admin_session = {}
trending_numbers = {}
pending_admin_login = {}

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
        url1 = f"{BASE_URL}/getChatMember"
        payload1 = {
            "chat_id": f"@{CHANNEL_1_USERNAME}",
            "user_id": chat_id
        }
        response1 = requests.post(url1, json=payload1, timeout=10)
        
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

def update_stats(chat_id, user_info, search_term=None):
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
            "term": search_term,
            "time": now
        })
        trending_numbers[search_term] = trending_numbers.get(search_term, 0) + 1
    
    save_data()

# ============ NUMBER API CALL WITH DEBUG ============
def call_number_api(number):
    try:
        url = f"{NUMBER_API_URL}?number={number}"
        print(f"📡 API Call: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # SSL verification disable with timeout
        resp = requests.get(url, headers=headers, timeout=30, verify=False)
        
        print(f"Response Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"API Response: {json.dumps(data, indent=2)}")  # Debug print
            return data
        else:
            return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        print(f"API Error: {e}")
        return {"error": str(e)[:50]}

# ============ FORMATTER - FIXED FOR ACTUAL API RESPONSE ============
def format_number_result(data, number):
    if data.get("error"):
        return f"❌ Error: {data['error']}"
    
    # Try to extract data from different possible response structures
    result_data = None
    
    # Case 1: Direct result
    if "result" in data:
        result_data = data["result"]
    # Case 2: Data wrapper
    elif "data" in data:
        result_data = data["data"]
        if isinstance(result_data, dict) and "result" in result_data:
            result_data = result_data["result"]
    # Case 3: Data is the result itself
    else:
        result_data = data
    
    # If still no data, check if it's a list
    if isinstance(result_data, list) and len(result_data) > 0:
        result_data = result_data[0]
    
    # If no valid data found
    if not result_data or not isinstance(result_data, dict):
        print(f"Could not extract data from: {data}")
        return f"❌ No information found for {number}\n\nAPI Response format issue. Contact developer."
    
    # Extract fields with fallbacks
    name = result_data.get('name') or result_data.get('NAME') or result_data.get('Name') or 'N/A'
    fname = result_data.get('fname') or result_data.get('FNAME') or result_data.get('father_name') or result_data.get('FATHER') or 'N/A'
    aadhaar = result_data.get('id') or result_data.get('ID') or result_data.get('aadhaar') or result_data.get('AADHAAR') or 'N/A'
    alt = result_data.get('alt') or result_data.get('ALT') or result_data.get('alternate') or result_data.get('ALTERNATE') or 'N/A'
    carrier = result_data.get('circle') or result_data.get('CIRCLE') or result_data.get('operator') or result_data.get('OPERATOR') or 'N/A'
    email = result_data.get('email') or result_data.get('EMAIL') or result_data.get('Email') or 'N/A'
    address = result_data.get('address') or result_data.get('ADDRESS') or result_data.get('Address') or 'N/A'
    
    # Format the response
    result = f"📞 NUMBER INFO\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 Number: {number}\n\n"
    result += f"👤 Name: {name}\n\n"
    result += f"👨 Father: {fname}\n\n"
    result += f"🆔 Aadhaar: {aadhaar}\n\n"
    result += f"📞 Alternate: {alt}\n\n"
    result += f"📡 Carrier: {carrier}\n\n"
    result += f"📧 Email: {email if email else 'N/A'}\n\n"
    
    if address and address != 'N/A':
        if len(address) > 80:
            address = address[:77] + '...'
        result += f"📍 Address: {address}\n\n"
    
    result += f"⚡ POWERED BY {DEVELOPER_USERNAME}"
    return result

# ============ ADMIN FUNCTIONS ============
def show_admin_menu(chat_id):
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
    msg += f"\n⚡ POWERED BY {DEVELOPER_USERNAME}"
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
    
    msg += f"\n⚡ POWERED BY {DEVELOPER_USERNAME}"
    send_msg(chat_id, msg)
    show_admin_menu(chat_id)

def show_all_history(chat_id):
    all_searches = []
    for cid, data in user_data.items():
        for s in data.get("searches", []):
            name = data.get("display_name", "Unknown")
            all_searches.append(f"{name}: {s.get('term', 'N/A')} - {s.get('time', 'N/A')}")
    
    if all_searches:
        msg = "📜 LAST 30 SEARCHES\n━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(all_searches[-30:])
        msg += f"\n\n⚡ POWERED BY {DEVELOPER_USERNAME}"
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
    
    msg += f"\n⚡ POWERED BY {DEVELOPER_USERNAME}"
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
            if send_msg(int(cid), f"📢 BROADCAST\n\n{msg_text}\n\n⚡ POWERED BY {DEVELOPER_USERNAME}"):
                sent += 1
            time.sleep(0.05)
        except:
            pass
    
    send_msg(chat_id, f"✅ Sent to {sent}/{len(user_data)} users")
    show_admin_menu(chat_id)

# ============ COMMAND HANDLERS ============
def handle_num_command(chat_id, number):
    if not number.isdigit() or len(number) != 10:
        send_msg(chat_id, "❌ Please enter a valid 10-digit number!\n\nUsage: /num 9876543210")
        return
    
    send_msg(chat_id, f"🔍 Searching number: {number}...\n\n⏳ Please wait...")
    result = call_number_api(number)
    formatted_result = format_number_result(result, number)
    send_msg(chat_id, formatted_result)

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
                send_callback(chat_id, "✅ Both channels joined! Access granted.", callback_id)
                
                msg_id = callback["message"]["message_id"]
                success_msg = (
                    f"✅ <b>ACCESS GRANTED!</b> ✅\n\n"
                    f"Thank you for joining both channels!\n\n"
                    f"You can now use the bot.\n\n"
                    f"Use /num 9876543210 to get number info!"
                )
                edit_message(chat_id, msg_id, success_msg)
                
                welcome_msg = (
                    f"🎉 <b>WELCOME TO NUMBER INFO BOT!</b> 🎉\n\n"
                    f"📞 <b>Use /num command to get number details!</b>\n\n"
                    f"📌 <b>Usage:</b>\n"
                    f"<code>/num 9876543210</code>\n\n"
                    f"⚡ <b>Powered by {DEVELOPER_USERNAME}</b>"
                )
                send_msg(chat_id, welcome_msg, parse_mode="HTML")
            else:
                send_callback(chat_id, "❌ Please join both channels first!", callback_id)
                
                msg_id = callback["message"]["message_id"]
                
                status_msg = ""
                buttons = []
                
                if not c1_joined:
                    status_msg += f"\n❌ {CHANNEL_1_NAME} - Not joined"
                    buttons.append([{"text": f"📢 JOIN {CHANNEL_1_NAME}", "url": CHANNEL_1_LINK}])
                else:
                    status_msg += f"\n✅ {CHANNEL_1_NAME} - Joined"
                
                if not c2_joined:
                    status_msg += f"\n❌ {CHANNEL_2_NAME} - Not joined"
                    buttons.append([{"text": f"📢 JOIN {CHANNEL_2_NAME}", "url": CHANNEL_2_LINK}])
                else:
                    status_msg += f"\n✅ {CHANNEL_2_NAME} - Joined"
                
                buttons.append([{"text": "✅ Check Again", "callback_data": "check_membership"}])
                
                keyboard = {"inline_keyboard": buttons}
                
                msg_text = (
                    f"⚠️ <b>ACCESS DENIED</b> ⚠️\n\n"
                    f"You must join BOTH channels to use this bot!\n\n"
                    f"📢 <b>Channels Status:</b>{status_msg}\n\n"
                    f"👇 <b>Join both channels and click CHECK AGAIN</b>"
                )
                edit_message(chat_id, msg_id, msg_text, keyboard)
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
    
    # ============ GROUP HANDLER ============
    is_group = chat_id < 0
    
    if is_group:
        if not text or not text.startswith("/"):
            return
    
    # ============ FORCE JOIN CHECK ============
    if not is_group or (is_group and text and text.startswith("/")):
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
    
    # ============ ADMIN COMMAND ============
    if text == "/admin":
        if admin:
            show_admin_menu(chat_id)
        else:
            pending_admin_login[str(chat_id)] = True
            send_msg(chat_id, "🔐 <b>ADMIN LOGIN</b>\n━━━━━━━━━━━━━━━━━━\n\nPlease enter the admin password to continue.\n\nType /cancel to cancel.", parse_mode="HTML")
        return
    
    if text == "/cancel" and str(chat_id) in pending_admin_login:
        del pending_admin_login[str(chat_id)]
        send_msg(chat_id, "❌ Login cancelled!")
        return
    
    if text == ADMIN_PASSWORD and not admin:
        admin_session[str(chat_id)] = {}
        send_msg(chat_id, "✅ <b>Admin access granted!</b>\n\nType /admin to open admin panel.", parse_mode="HTML")
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
    
    # ============ /num COMMAND ============
    if text.startswith("/num"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            handle_num_command(chat_id, parts[1])
        else:
            send_msg(chat_id, "❌ Usage: /num 9876543210")
        return
    
    # ============ HELP / START ============
    if text == "/start" or text == "/help":
        welcome_msg = (
            f"🎉 <b>WELCOME TO NUMBER INFO BOT!</b> 🎉\n\n"
            f"📞 <b>Use /num command to get number details!</b>\n\n"
            f"📌 <b>Usage:</b>\n"
            f"<code>/num 9876543210</code>\n\n"
            f"⚡ <b>Powered by {DEVELOPER_USERNAME}</b>"
        )
        send_msg(chat_id, welcome_msg, parse_mode="HTML")
        return
    
    # ============ IGNORE ANYTHING ELSE ============
    if is_group:
        return
    
    if text and not text.startswith("/"):
        send_msg(chat_id, "❌ Please use /num command!\n\nUsage: /num 9876543210")

# ============ MAIN ============
def main():
    load_data()
    Thread(target=run_health_server, daemon=True).start()
    
    print("=" * 60)
    print("🤖 NUMBER INFO BOT STARTED")
    print("=" * 60)
    print(f"👥 Loaded users: {len(user_data)}")
    print(f"👨‍💻 Powered by: {DEVELOPER_USERNAME}")
    print(f"🔐 Admin Password: {ADMIN_PASSWORD}")
    print("=" * 60)
    print("📌 FORCE JOIN ENABLED FOR BOTH CHANNELS:")
    print(f"   1. {CHANNEL_1_NAME} - {CHANNEL_1_LINK}")
    print(f"   2. {CHANNEL_2_NAME} - {CHANNEL_2_LINK}")
    print("=" * 60)
    print("📌 ONLY /num COMMAND AVAILABLE")
    print("📌 Usage: /num 9876543210")
    print("📌 SSL Verification DISABLED for API calls")
    print("📌 DEBUG MODE: API responses will be printed in console")
    print("📌 Admin Access: Type /admin and enter password: #zyro2000")
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
