import logging
import json
import os
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# ===================== CONFIGURATION =====================
BOT_TOKEN    = "8632632108:AAE_e0uWgzugp-rvRkCWASfFnRk1z9W9JOk"
API_KEY      = "RAJAN123"
BASE_API_URL = "https://all-sigma-pad-api-damo-5-day.vercel.app/api"

# ===================== ALL APIs =====================
NUM_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=NUMBER&term={{}}"
AADHAR_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=AADHAAR&term={{}}"
TG_NUM_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=TGNUMBER&term={{}}"
GST_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=GST&term={{}}"
IP_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=IP&term={{}}"
INSTA_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=INSTAGRAM&term={{}}"
FF_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=FREEFIRE&term={{}}"
VEHICLE_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=VEHICLE&term={{}}"
SMS_API_URL = f"{BASE_API_URL}?key={API_KEY}&type=SMS&term={{}}|{{}}"

# Admin User ID
ADMIN_ID = 7148414172

# Force Join Channels
CHANNEL_1_ID       = "-1003504397910"
CHANNEL_1_LINK     = "https://t.me/+-wTiagx9CCljM2M1"
CHANNEL_1_NAME     = "ALL ILLEGAL STUFFS"

CHANNEL_2_ID       = "@SelfBanner"
CHANNEL_2_LINK     = "https://t.me/SelfBanner"
CHANNEL_2_NAME     = "BackupChannel"

CHANNEL_3_ID       = "@Mod_x_patel"
CHANNEL_3_LINK     = "https://t.me/Mod_x_patel"
CHANNEL_3_NAME     = "API CHANNEL"

# Data files
USERS_FILE     = "users.json"
PROTECTED_FILE = "protected.json"
BANNED_FILE    = "banned.json"
HISTORY_FILE   = "history.json"
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ===================== DATA HELPERS =====================

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_protected() -> list:
    if os.path.exists(PROTECTED_FILE):
        with open(PROTECTED_FILE, "r") as f:
            return json.load(f)
    return []

def save_protected(protected: list) -> None:
    with open(PROTECTED_FILE, "w") as f:
        json.dump(protected, f, indent=2)

def load_banned() -> list:
    if os.path.exists(BANNED_FILE):
        with open(BANNED_FILE, "r") as f:
            return json.load(f)
    return []

def save_banned(banned: list) -> None:
    with open(BANNED_FILE, "w") as f:
        json.dump(banned, f, indent=2)

def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history: dict) -> None:
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def log_search(user_id: int, query: str, command: str = "num") -> None:
    history = load_history()
    uid = str(user_id)
    if uid not in history:
        history[uid] = []
    history[uid].append({
        "command": command,
        "query": query,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    history[uid] = history[uid][-30:]
    save_history(history)

def register_user(user) -> bool:
    users = load_users()
    uid = str(user.id)
    is_new = uid not in users
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users[uid] = {
        "id": user.id,
        "username": user.username or "N/A",
        "first_name": user.first_name or "N/A",
        "joined": users[uid].get("joined", now) if uid in users else now,
    }
    save_users(users)
    return is_new

# ===================== ADMIN & BAN CHECK =====================

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def is_banned(user_id: int) -> bool:
    return str(user_id) in [str(b) for b in load_banned()]

# ===================== FORCE JOIN =====================

async def is_member(bot, user_id: int, channel: str) -> bool:
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

def join_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"➕ Join {CHANNEL_1_NAME}", url=CHANNEL_1_LINK),
            InlineKeyboardButton(f"➕ Join {CHANNEL_2_NAME}", url=CHANNEL_2_LINK),
        ],
        [
            InlineKeyboardButton(f"➕ Join {CHANNEL_3_NAME}", url=CHANNEL_3_LINK),
        ],
        [
            InlineKeyboardButton("✅ I've Joined — Verify Now", callback_data="verify_join"),
        ]
    ])

def result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📢 {CHANNEL_1_NAME}", url=CHANNEL_1_LINK),
            InlineKeyboardButton(f"📢 {CHANNEL_2_NAME}", url=CHANNEL_2_LINK),
        ],
        [
            InlineKeyboardButton(f"📢 {CHANNEL_3_NAME}", url=CHANNEL_3_LINK),
        ]
    ])

async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id

    if is_banned(user_id) and not is_admin(user_id):
        await update.message.reply_text("🚫 *You have been banned from using this bot.*", parse_mode="Markdown")
        return False

    if is_admin(user_id):
        return True

    bot = context.bot
    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)
    joined3 = await is_member(bot, user_id, CHANNEL_3_ID)

    if joined1 and joined2 and joined3:
        return True

    not_joined = []
    if not joined1:
        not_joined.append(CHANNEL_1_NAME)
    if not joined2:
        not_joined.append(CHANNEL_2_NAME)
    if not joined3:
        not_joined.append(CHANNEL_3_NAME)

    msg = (
        "❌ *Access Denied!*\n\n"
        "To use this bot, you must join all channels first:\n\n"
        f"📢 *{CHANNEL_1_NAME}*\n"
        f"📢 *{CHANNEL_2_NAME}*\n"
        f"📢 *{CHANNEL_3_NAME}*\n\n"
        f"⚠️ *Not Joined:* {', '.join(not_joined)}\n\n"
        "After joining, press the *Verify* button below ✅"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=join_keyboard())
    return False

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    bot = context.bot

    joined1 = await is_member(bot, user_id, CHANNEL_1_ID)
    joined2 = await is_member(bot, user_id, CHANNEL_2_ID)
    joined3 = await is_member(bot, user_id, CHANNEL_3_ID)

    if joined1 and joined2 and joined3:
        await query.edit_message_text(
            "✅ *Verified! You can now use the bot.*\n\n"
            "📲 Type `/num 9876543210` to get started.",
            parse_mode="Markdown",
        )
    else:
        not_joined = []
        if not joined1:
            not_joined.append(CHANNEL_1_NAME)
        if not joined2:
            not_joined.append(CHANNEL_2_NAME)
        if not joined3:
            not_joined.append(CHANNEL_3_NAME)

        await query.edit_message_text(
            "❌ *Still not joined!*\n\n"
            f"⚠️ *Pending channels:* {', '.join(not_joined)}\n\n"
            "Please join all channels and verify again ✅",
            parse_mode="Markdown",
            reply_markup=join_keyboard(),
        )

# ===================== API HELPER =====================

async def fetch_api(url: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"API Error: {e}")
        return {"error": str(e)}

def clean_text(text):
    if not text or text == "None" or text == "N/A":
        return "N/A"
    text = str(text).replace("!", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()

def mask_name(name):
    """Mask name like P*****T B*********I"""
    if not name or name == "N/A":
        return "N/A"
    name = str(name)
    if len(name) <= 2:
        return name
    parts = name.split()
    masked_parts = []
    for part in parts:
        if len(part) <= 2:
            masked_parts.append(part)
        else:
            masked_parts.append(part[0] + "*" * (len(part) - 2) + part[-1])
    return " ".join(masked_parts)

# ===================== IP FORMATTER =====================

def format_ip_response(data, term):
    """Format IP API response into beautiful format"""
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    # Extract data
    result_data = data.get("data", {}).get("result", {})
    if not result_data:
        result_data = data
    
    ip = term
    city = clean_text(result_data.get('city', 'N/A'))
    region = clean_text(result_data.get('region', 'N/A'))
    country = clean_text(result_data.get('country', 'N/A'))
    postal = clean_text(result_data.get('zip', result_data.get('postal', 'N/A')))
    isp = clean_text(result_data.get('isp', 'N/A'))
    org = clean_text(result_data.get('org', 'N/A'))
    asn = clean_text(result_data.get('as', result_data.get('asn', 'N/A')))
    domain = clean_text(result_data.get('domain', result_data.get('hosting_domain', 'N/A')))
    ip_type = clean_text(result_data.get('type', result_data.get('ip_type', 'N/A')))
    lat = result_data.get('lat', result_data.get('latitude', 'N/A'))
    lon = result_data.get('lon', result_data.get('longitude', 'N/A'))
    timezone = clean_text(result_data.get('timezone', result_data.get('tz', 'N/A')))
    
    # Build location string
    location_parts = []
    if city != "N/A":
        location_parts.append(city)
    if region != "N/A" and region != city:
        location_parts.append(region)
    location = ", ".join(location_parts) if location_parts else "N/A"
    
    result = "🌐 *IP INFORMATION*\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 *IP:* `{ip}`\n"
    
    if location != "N/A":
        result += f"📍 *Location:* `{location}`\n"
    if country != "N/A":
        result += f"🌍 *Country:* `{country}`\n"
    if postal != "N/A":
        result += f"📮 *Postal:* `{postal}`\n\n"
    else:
        result += "\n"
    
    if isp != "N/A":
        result += f"🏢 *ISP:* `{isp}`\n"
    if org != "N/A" and org != isp:
        result += f"🏢 *Organization:* `{org}`\n"
    if asn != "N/A":
        result += f"🆔 *ASN:* `{asn}`\n\n"
    else:
        result += "\n"
    
    if domain != "N/A" and domain != "-":
        result += f"🌐 *Domain:* `{domain}`\n"
    if ip_type != "N/A":
        result += f"📡 *Type:* `{ip_type}`\n\n"
    else:
        result += "\n"
    
    if lat != "N/A" and lon != "N/A":
        result += f"🗺️ *Coordinates:* `{lat}, {lon}`\n"
    if timezone != "N/A":
        result += f"⏰ *Timezone:* `{timezone}`\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

# ===================== VEHICLE FORMATTER =====================

def format_vehicle_response(data, term):
    """Format Vehicle API response into beautiful format"""
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    result_data = data.get("data", {}).get("result", {})
    
    vehicle_no = term.upper()
    owner_name = mask_name(clean_text(result_data.get('owner_name', result_data.get('name', 'N/A'))))
    maker_model = clean_text(result_data.get('maker_model', 'N/A'))
    model_name = clean_text(result_data.get('model_name', 'N/A'))
    vehicle_class = clean_text(result_data.get('vehicle_class', result_data.get('class', 'N/A')))
    fuel_type = clean_text(result_data.get('fuel_type', 'N/A'))
    reg_date = clean_text(result_data.get('registration_date', result_data.get('reg_date', 'N/A')))
    rto = clean_text(result_data.get('rto', result_data.get('registering_authority', 'N/A')))
    city = clean_text(result_data.get('city', result_data.get('district', 'N/A')))
    phone = clean_text(result_data.get('phone', result_data.get('mobile', 'N/A')))
    insurance_company = clean_text(result_data.get('insurance_company', result_data.get('insurer', 'N/A')))
    insurance_upto = clean_text(result_data.get('insurance_upto', result_data.get('insurance_valid_till', 'N/A')))
    
    result = "🚗 *VEHICLE INFO*\n━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🎯 *Vehicle:* `{vehicle_no}`\n\n"
    
    result += f"👤 *Owner:* `{owner_name}`\n"
    if maker_model != "N/A":
        result += f"🏭 *Model:* `{maker_model}`\n"
    if model_name != "N/A" and model_name != maker_model:
        result += f"📝 *Maker:* `{model_name}`\n"
    if vehicle_class != "N/A":
        result += f"🚦 *Class:* `{vehicle_class}`\n"
    if fuel_type != "N/A":
        result += f"⛽ *Fuel:* `{fuel_type}`\n\n"
    else:
        result += "\n"
    
    if reg_date != "N/A":
        result += f"📅 *Reg Date:* `{reg_date}`\n"
    if rto != "N/A":
        result += f"🏢 *RTO:* `{rto}`\n"
    if city != "N/A":
        result += f"📍 *City:* `{city}`\n"
    if phone != "N/A":
        result += f"📞 *Phone:* `{phone}`\n\n"
    else:
        result += "\n"
    
    if insurance_company != "N/A":
        result += f"🏥 *Insurance:* `{insurance_company}`\n"
    if insurance_upto != "N/A":
        result += f"📅 *Insurance Upto:* `{insurance_upto}`\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

# ===================== AADHAR FORMATTER =====================

def format_aadhar_response(data, term):
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    result = "📊 *AADHAR CARD INFO*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🆔 *Aadhaar Number:* `{term}`\n"
    
    details = data.get("data", {}).get("details", {})
    card_info = details.get("card_info", {})
    
    if card_info:
        result += f"📄 *Ration Card ID:* `{card_info.get('Ration Card ID', 'N/A')}`\n"
        result += f"🏠 *District:* `{card_info.get('District', 'N/A')}`\n"
        result += f"📍 *State:* `{card_info.get('State', 'N/A')}`\n"
        result += f"📋 *Card Type:* `{card_info.get('Card Type', 'N/A')}`\n"
        result += f"🏪 *Home FPS:* `{card_info.get('Home FPS', 'N/A')}`\n"
        result += f"📅 *Issue Date:* `{card_info.get('Issue Date', 'N/A')}`\n"
    
    members = details.get("members", [])
    if members:
        result += f"\n👥 *FAMILY MEMBERS* ({len(members)})\n━━━━━━━━━━━━━━━━━━━━━\n"
        for member in members[:10]:
            result += f"👤 *Name:* `{member.get('member_name', 'N/A')}`\n"
            result += f"👨 *Relation:* `{member.get('relationship', 'N/A')}`\n"
            result += f"⚥ *Gender:* `{member.get('gender', 'N/A')}`\n"
            result += f"🆔 *Masked UID:* `{member.get('uid_masked', 'N/A')}`\n"
            result += f"📅 *Updated:* `{member.get('cr_last_updated', 'N/A')}`\n━━━━━━━━━━━━━━━━━━━━━\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

# ===================== OTHER FORMATTERS =====================

def format_number_response(data, term):
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    result = "📞 *NUMBER INFO*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"📱 *Mobile Number:* `{term}`\n"
    
    results = []
    if data.get("data") and data["data"].get("result") and data["data"]["result"].get("results"):
        results = data["data"]["result"]["results"]
    elif data.get("result") and data["result"].get("results"):
        results = data["result"]["results"]
    
    if results:
        result += f"\n📊 *Total Results:* `{len(results)}`\n━━━━━━━━━━━━━━━━━━━━━\n"
        for idx, info in enumerate(results[:5], 1):
            result += f"\n📌 *RESULT #{idx}*\n"
            result += f"👤 *Name:* `{clean_text(info.get('NAME', info.get('name', 'N/A')))}`\n"
            result += f"👨 *Father:* `{clean_text(info.get('fname', 'N/A'))}`\n"
            result += f"📱 *Mobile:* `{clean_text(info.get('MOBILE', info.get('mobile', 'N/A')))}`\n"
            result += f"📞 *Alternate:* `{clean_text(info.get('alt', 'N/A'))}`\n"
            result += f"📡 *Carrier:* `{clean_text(info.get('circle', 'N/A'))}`\n"
            result += f"🏠 *Address:* `{clean_text(info.get('ADDRESS', info.get('address', 'N/A')))[:80]}`\n"
            if info.get('id'):
                result += f"🆔 *ID:* `{clean_text(info.get('id'))}`\n"
            result += f"━━━━━━━━━━━━━━━━━━━━━\n"
    else:
        result += f"\n❌ *No data found for number:* `{term}`\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

def format_tgnum_response(data, term):
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    result = "📞 *TELEGRAM TO NUMBER INFO*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🆔 *Telegram ID:* `{term}`\n"
    
    result_data = data.get("data", {}).get("result", {})
    
    if result_data:
        result += f"📱 *Phone Number:* `{result_data.get('number', 'N/A')}`\n"
        result += f"🌍 *Country:* `{result_data.get('country', 'N/A')}`\n"
        result += f"📞 *Country Code:* `{result_data.get('country_code', 'N/A')}`\n"
        result += f"💬 *Message:* `{result_data.get('msg', 'N/A')}`\n"
    else:
        result += f"❌ *No data found for Telegram ID:* `{term}`\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

def format_gst_response(data, term):
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    result = "🏢 *GST INFORMATION*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🔹 *GST Number:* `{term}`\n"
    
    result_data = data.get("data", {}).get("result", {})
    
    if result_data:
        result += f"🏭 *Business Name:* `{clean_text(result_data.get('business_name', result_data.get('name', 'N/A')))}`\n"
        result += f"📛 *Trade Name:* `{clean_text(result_data.get('trade_name', 'N/A'))}`\n"
        result += f"📅 *Registration Date:* `{clean_text(result_data.get('registration_date', 'N/A'))}`\n"
        result += f"🗺️ *State:* `{clean_text(result_data.get('state', 'N/A'))}`\n"
        result += f"✅ *Status:* `{clean_text(result_data.get('status', 'N/A'))}`\n"
    else:
        result += f"❌ *No data found for GST:* `{term}`\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

def format_insta_response(data, term):
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    result = "📸 *INSTAGRAM PROFILE INFO*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🔹 *Username:* `{term}`\n"
    
    result_data = data.get("data", {}).get("result", {})
    
    if result_data:
        result += f"👤 *Full Name:* `{clean_text(result_data.get('full_name', 'N/A'))}`\n"
        result += f"👥 *Followers:* `{result_data.get('followers', 0):,}`\n"
        result += f"📌 *Following:* `{result_data.get('following', 0):,}`\n"
        result += f"📷 *Posts:* `{result_data.get('posts', 0)}`\n"
        result += f"🔒 *Private Account:* `{result_data.get('is_private', False)}`\n"
        result += f"✅ *Verified:* `{result_data.get('is_verified', False)}`\n"
        result += f"📝 *Bio:* `{clean_text(result_data.get('bio', 'N/A'))[:100]}`\n"
    else:
        result += f"❌ *No data found for Instagram:* `{term}`\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

def format_ff_response(data, term):
    if data.get("error"):
        return f"❌ *Error:* {data['error']}"
    
    result = "🎮 *FREE FIRE PLAYER INFO*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"🆔 *Player ID:* `{term}`\n"
    
    result_data = data.get("data", {}).get("result", {})
    
    if result_data:
        basic = result_data.get("basicInfo", {})
        clan = result_data.get("clanBasicInfo", {})
        
        result += f"👤 *Nickname:* `{clean_text(basic.get('nickname', 'N/A'))}`\n"
        result += f"📊 *Level:* `{basic.get('level', 'N/A')}`\n"
        result += f"🌍 *Region:* `{clean_text(basic.get('region', 'N/A'))}`\n"
        result += f"🏆 *Rank:* `{basic.get('rank', 'N/A')}`\n"
        result += f"⭐ *Rank Points:* `{basic.get('rankingPoints', 'N/A')}`\n"
        result += f"❤️ *Liked:* `{basic.get('liked', 0):,}`\n\n"
        result += f"👥 *CLAN INFO*\n━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"📛 *Clan Name:* `{clean_text(clan.get('clanName', 'N/A'))}`\n"
        result += f"📊 *Clan Level:* `{clan.get('clanLevel', 'N/A')}`\n"
        result += f"👥 *Members:* `{clan.get('memberNum', 'N/A')}`\n\n"
        result += f"📅 *Account Created:* `{basic.get('createAt', 'N/A')[:10]}`\n"
        result += f"🕐 *Last Login:* `{basic.get('lastLoginAt', 'N/A')[:10]}`\n"
    else:
        result += f"❌ *No data found for FF ID:* `{term}`\n"
    
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

def format_sms_response(data, phone, message):
    if data.get("error"):
        return f"❌ *SMS Failed:* {data['error']}"
    
    result = "📱 *SMS RESULT*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    result += f"📞 *Phone Number:* `{phone}`\n"
    result += f"📝 *Message:* `{message[:100]}{'...' if len(message) > 100 else ''}`\n"
    
    status = "SENT"
    if data.get("data") and data["data"].get("api_response"):
        try:
            api_resp = data["data"]["api_response"]
            if isinstance(api_resp, str):
                resp_json = json.loads(api_resp)
                status = resp_json.get("message", "SENT")
        except:
            status = "SENT"
    
    result += f"✅ *Status:* `{status}`\n"
    result += f"\n⚡ *POWERED BY @Leader_jiii*"
    return result

# ===================== COMMAND HANDLERS =====================

async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/num 9876543210`", parse_mode="Markdown")
        return
    mobile_number = context.args[0].strip()
    if not mobile_number.isdigit() or len(mobile_number) != 10:
        await update.message.reply_text("❌ Please enter a valid 10-digit mobile number!")
        return
    log_search(user.id, mobile_number, "num")
    searching_msg = await update.message.reply_text(f"🔍 Searching `{mobile_number}` ...", parse_mode="Markdown")
    url = NUM_API_URL.format(mobile_number)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_number_response(data, mobile_number), parse_mode="Markdown", reply_markup=result_keyboard())

async def aadhar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/aadhar 123456789012`", parse_mode="Markdown")
        return
    aadhar_number = context.args[0].strip()
    log_search(user.id, aadhar_number, "aadhar")
    searching_msg = await update.message.reply_text(f"🔍 Searching Aadhar `{aadhar_number}` ...", parse_mode="Markdown")
    url = AADHAR_API_URL.format(aadhar_number)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_aadhar_response(data, aadhar_number), parse_mode="Markdown", reply_markup=result_keyboard())

async def gst_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/gst 22AAAAA0000A1Z`", parse_mode="Markdown")
        return
    gst_no = context.args[0].strip().upper()
    log_search(user.id, gst_no, "gst")
    searching_msg = await update.message.reply_text(f"🔍 Searching GST `{gst_no}` ...", parse_mode="Markdown")
    url = GST_API_URL.format(gst_no)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_gst_response(data, gst_no), parse_mode="Markdown", reply_markup=result_keyboard())

async def tgnum_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/tgnum 6323367629`", parse_mode="Markdown")
        return
    tg_id = context.args[0].strip()
    log_search(user.id, tg_id, "tgnum")
    searching_msg = await update.message.reply_text(f"🔍 Searching Telegram ID `{tg_id}` ...", parse_mode="Markdown")
    url = TG_NUM_API_URL.format(tg_id)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_tgnum_response(data, tg_id), parse_mode="Markdown", reply_markup=result_keyboard())

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/ip 8.8.8.8`", parse_mode="Markdown")
        return
    ip_addr = context.args[0].strip()
    log_search(user.id, ip_addr, "ip")
    searching_msg = await update.message.reply_text(f"🔍 Searching IP `{ip_addr}` ...", parse_mode="Markdown")
    url = IP_API_URL.format(ip_addr)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_ip_response(data, ip_addr), parse_mode="Markdown", reply_markup=result_keyboard())

async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/insta username`", parse_mode="Markdown")
        return
    insta_user = context.args[0].strip()
    log_search(user.id, insta_user, "insta")
    searching_msg = await update.message.reply_text(f"🔍 Searching Instagram `{insta_user}` ...", parse_mode="Markdown")
    url = INSTA_API_URL.format(insta_user)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_insta_response(data, insta_user), parse_mode="Markdown", reply_markup=result_keyboard())

async def ff_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/ff 854127389`", parse_mode="Markdown")
        return
    ff_id = context.args[0].strip()
    log_search(user.id, ff_id, "ff")
    searching_msg = await update.message.reply_text(f"🔍 Searching Free Fire ID `{ff_id}` ...", parse_mode="Markdown")
    url = FF_API_URL.format(ff_id)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_ff_response(data, ff_id), parse_mode="Markdown", reply_markup=result_keyboard())

async def vehicle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/vehicle RJ18CF3690`", parse_mode="Markdown")
        return
    vehicle_no = " ".join(context.args).strip().upper()
    log_search(user.id, vehicle_no, "vehicle")
    searching_msg = await update.message.reply_text(f"🔍 Searching vehicle `{vehicle_no}` ...", parse_mode="Markdown")
    url = VEHICLE_API_URL.format(vehicle_no)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ API Error: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_vehicle_response(data, vehicle_no), parse_mode="Markdown", reply_markup=result_keyboard())

async def sms_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    register_user(user)
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: `/sms 9876543210 Your message here`", parse_mode="Markdown")
        return
    phone_number = context.args[0].strip()
    message = " ".join(context.args[1:]).strip()
    if not phone_number.isdigit() or len(phone_number) != 10:
        await update.message.reply_text("❌ Please enter a valid 10-digit phone number!")
        return
    log_search(user.id, f"{phone_number}|{message[:50]}", "sms")
    searching_msg = await update.message.reply_text(f"📱 Sending SMS to `{phone_number}` ...", parse_mode="Markdown")
    url = SMS_API_URL.format(phone_number, message)
    data = await fetch_api(url)
    try:
        await searching_msg.delete()
    except:
        pass
    if data.get("error"):
        await update.message.reply_text(f"❌ SMS Failed: {data['error']}", parse_mode="Markdown")
        return
    await update.message.reply_text(format_sms_response(data, phone_number, message), parse_mode="Markdown", reply_markup=result_keyboard())

# ===================== START & HELP =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    user = update.effective_user
    is_new = register_user(user)
    if is_new:
        users = load_users()
        total = len(users)
        username_display = f"@{user.username}" if user.username else "No Username"
        notify_msg = f"🆕 *New User Joined!*\n\n👤 *Name:* {user.first_name}\n🔗 *Username:* {username_display}\n🆔 *User ID:* `{user.id}`\n📊 *Total Users Now:* `{total}`"
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=notify_msg, parse_mode="Markdown")
        except:
            pass
    await update.message.reply_text(
        "🔍 *Welcome to Info Bot!*\n\n━━━━━━━━━━━━━━━━━━━━━\n📲 *Available Commands:*\n\n"
        "`/num` - Mobile Number Info\n`/aadhar` - Aadhar Card Info\n`/gst` - GST Number Info\n"
        "`/tgnum` - Phone to Telegram ID\n`/ip` - IP Address Details\n`/insta` - Instagram Profile Info\n"
        "`/ff` - Free Fire ID Info\n`/vehicle` - Vehicle Registration Info\n`/sms` - Send Custom SMS\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\nType `/help` for usage examples.\n\n⚡ *Powered by @Leader_jiii*",
        parse_mode="Markdown",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_force_join(update, context):
        return
    await update.message.reply_text(
        "📖 *Help — Available Commands*\n\n━━━━━━━━━━━━━━━━━━━━━\n🤖 *Bot Commands:*\n\n"
        "🔹 `/num 9876543210` - Mobile number info\n🔹 `/aadhar 123456789012` - Aadhar card info\n"
        "🔹 `/gst 22AAAAA0000A1Z` - GST number info\n🔹 `/tgnum 6323367629` - Telegram ID to number\n"
        "🔹 `/ip 8.8.8.8` - IP address details\n🔹 `/insta username` - Instagram profile\n"
        "🔹 `/ff 854127389` - Free Fire player info\n🔹 `/vehicle RJ18CF3690` - Vehicle info\n"
        "🔹 `/sms 9876543210 Hello` - Send SMS\n\n━━━━━━━━━━━━━━━━━━━━━\n⚡ *Powered by @Leader_jiii*",
        parse_mode="Markdown",
    )

# ===================== ADMIN COMMANDS =====================

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    users = load_users()
    protected = load_protected()
    banned = load_banned()
    history = load_history()
    total_searches = sum(len(v) for v in history.values())
    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n👥 Total Users: `{len(users)}`\n🔒 Protected Numbers: `{len(protected)}`\n🚫 Banned Users: `{len(banned)}`\n🔍 Total Searches: `{total_searches}`",
        parse_mode="Markdown"
    )

async def admin_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/ban user_id`", parse_mode="Markdown")
        return
    uid = context.args[0].strip()
    banned = load_banned()
    if uid in [str(b) for b in banned]:
        await update.message.reply_text(f"User `{uid}` already banned.", parse_mode="Markdown")
        return
    banned.append(uid)
    save_banned(banned)
    await update.message.reply_text(f"🚫 User `{uid}` has been banned.", parse_mode="Markdown")

async def admin_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/unban user_id`", parse_mode="Markdown")
        return
    uid = context.args[0].strip()
    banned = load_banned()
    if uid not in [str(b) for b in banned]:
        await update.message.reply_text(f"User `{uid}` is not banned.", parse_mode="Markdown")
        return
    banned = [b for b in banned if str(b) != uid]
    save_banned(banned)
    await update.message.reply_text(f"✅ User `{uid}` has been unbanned.", parse_mode="Markdown")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/bcast message`", parse_mode="Markdown")
        return
    msg = " ".join(context.args)
    users = load_users()
    success = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 *Announcement*\n\n{msg}\n\n⚡ *@Leader_jiii*", parse_mode="Markdown")
            success += 1
        except:
            pass
    await update.message.reply_text(f"✅ Broadcast sent to {success} users.", parse_mode="Markdown")

# ===================== MAIN =====================

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("num", num_command))
    app.add_handler(CommandHandler("aadhar", aadhar_command))
    app.add_handler(CommandHandler("gst", gst_command))
    app.add_handler(CommandHandler("tgnum", tgnum_command))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("insta", insta_command))
    app.add_handler(CommandHandler("ff", ff_command))
    app.add_handler(CommandHandler("vehicle", vehicle_command))
    app.add_handler(CommandHandler("sms", sms_command))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("ban", admin_ban))
    app.add_handler(CommandHandler("unban", admin_unban))
    app.add_handler(CommandHandler("bcast", admin_broadcast))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_join$"))
    logger.info("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
