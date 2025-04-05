import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatType, UserStatus
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied, ChannelInvalid
from config import COMMAND_PREFIX, PROFILE_ERROR_URL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

START_MESSAGE = """
<b>Welcome to the Telegram Info Bot 🌟</b>

Get quick and detailed insights about any Telegram user or group.

<b>Features:</b>
👤 Full Name  
🆔 User ID  
🔖 Username  
💬 Chat ID  
🌐 Data Center Location  
💎 Premium Status  
🛡 Verified Badge  
🚩 Account Flags  
🕒 Online Status  
📅 Account Creation Date  
⏳ Account Age

Use /info or /id to get started! 🚀
"""

# Mapping of Data Center IDs to their locations
DC_LOCATIONS = {
    1: "MIA, Miami, USA, US",
    2: "AMS, Amsterdam, Netherlands, NL",
    3: "MBA, Mumbai, India, IN",
    4: "STO, Stockholm, Sweden, SE",
    5: "SIN, Singapore, SG",
    6: "LHR, London, United Kingdom, GB",
    7: "FRA, Frankfurt, Germany, DE",
    8: "JFK, New York, USA, US",
    9: "HKG, Hong Kong, HK",
    10: "TYO, Tokyo, Japan, JP",
    11: "SYD, Sydney, Australia, AU",
    12: "GRU, São Paulo, Brazil, BR",
    13: "DXB, Dubai, UAE, AE",
    14: "CDG, Paris, France, FR",
    15: "ICN, Seoul, South Korea, KR",
}

# Function to calculate account age accurately
def calculate_account_age(creation_date):
    today = datetime.now()
    delta = relativedelta(today, creation_date)
    years = delta.years
    months = delta.months
    days = delta.days
    return f"{years} years, {months} months, {days} days"

# Function to estimate account creation date based on user ID
def estimate_account_creation_date(user_id):
    # Known reference points for user IDs and their creation dates
    reference_points = [
        (100000000, datetime(2013, 8, 1)),  # Telegram's launch date
        (1273841502, datetime(2020, 8, 13)),  # Example reference point
        (1500000000, datetime(2021, 5, 1)),  # Another reference point
        (2000000000, datetime(2022, 12, 1)),  # Another reference point
    ]
    
    # Find the closest reference point
    closest_point = min(reference_points, key=lambda x: abs(x[0] - user_id))
    closest_user_id, closest_date = closest_point
    
    # Calculate the difference in user IDs
    id_difference = user_id - closest_user_id
    
    # Estimate the creation date based on the difference
    # Assuming 250,000 user IDs are created per day (adjust as needed)
    days_difference = id_difference / 20000000
    creation_date = closest_date + timedelta(days=days_difference)
    
    return creation_date

def setup_info_handler(app):
    @app.on_message(filters.command(["info", "id"], prefixes=COMMAND_PREFIX) & (filters.private | filters.group))
    async def handle_info_command(client: Client, message: Message):
        logger.info("Received /info or /id command")
        try:
            progress_message = await client.send_message(message.chat.id, "**✨  Smart Tools  Fetching Info From Database 💥**")
            try:
                if not message.command or (len(message.command) == 1 and not message.reply_to_message):
                    logger.info("Fetching current user info")
                    user = message.from_user
                    chat = message.chat
                    premium_status = "✅ Yes" if user.is_premium else "❌ No"
                    dc_location = DC_LOCATIONS.get(user.dc_id, "Unknown")
                    account_created = estimate_account_creation_date(user.id)
                    account_created_str = account_created.strftime("%B %d, %Y")
                    account_age = calculate_account_age(account_created)
                    
                    # Added verification and status
                    verified_status = "✅ Yes" if getattr(user, 'is_verified', False) else "❌ No"
                    
                    status = "⚪️ Unknown"
                    if user.status:
                        if user.status == UserStatus.ONLINE:
                            status = "✅ Online"
                        elif user.status == UserStatus.OFFLINE:
                            status = "❌ Offline"
                        elif user.status == UserStatus.RECENTLY:
                            status = "☑️ Recently online"
                        elif user.status == UserStatus.LAST_WEEK:
                            status = "✖️ Last seen within week"
                        elif user.status == UserStatus.LAST_MONTH:
                            status = "❎ Last seen within month"
                    
                    response = (
                        "🌟 **User Information** 🌟\n\n"
                        f"👤 **Full Name:** {user.first_name} {user.last_name or ''}\n"
                        f"🆔 **User ID:** `{user.id}`\n"
                        f"🔖 **Username:** @{user.username}\n"
                        f"💬 **Chat Id:** `{chat.id}`\n"
                        f"🌐 **Data Center:** {user.dc_id} ({dc_location})\n"
                        f"💎 **Premium User:** {premium_status}\n"
                        f"🛡 **Verified:** {verified_status}\n"
                        f"🚩 **Flags:** {'⚠️ Scam' if getattr(user, 'is_scam', False) else '⚠️ Fake' if getattr(user, 'is_fake', False) else '✅ Clean'}\n"
                        f"🕒 **Status:** {status}\n"
                        f"📅 **Account Created On:** {account_created_str}\n"
                        f"⏳ **Account Age:** {account_age}"
                    )
                    buttons = [
                        [InlineKeyboardButton("✨ Android Link", url=f"tg://openmessage?user_id={user.id}"), InlineKeyboardButton("⚡️ iOS Link", url=f"tg://user?id={user.id}")],
                        [InlineKeyboardButton("💥 Permanent Link", user_id=user.id)],
                    ]
                    photo = await client.download_media(user.photo.big_file_id) if user.photo else PROFILE_ERROR_URL
                    await client.send_photo(chat_id=message.chat.id, photo=photo, caption=response, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))
                    logger.info("User info fetched successfully with buttons")
                elif message.reply_to_message:
                    # Show info of the replied user or bot
                    logger.info("Fetching info of the replied user or bot")
                    user = message.reply_to_message.from_user
                    chat = message.chat
                    premium_status = "✅ Yes" if user.is_premium else "❌ No"
                    dc_location = DC_LOCATIONS.get(user.dc_id, "Unknown")
                    account_created = estimate_account_creation_date(user.id)
                    account_created_str = account_created.strftime("%B %d, %Y")
                    account_age = calculate_account_age(account_created)
                    
                    # Added verification and status
                    verified_status = "✅ Yes" if getattr(user, 'is_verified', False) else "❌ No"
                    
                    status = "⚪️ Unknown"
                    if user.status:
                        if user.status == UserStatus.ONLINE:
                            status = "🟢 Online"
                        elif user.status == UserStatus.OFFLINE:
                            status = "⚫️ Offline"
                        elif user.status == UserStatus.RECENTLY:
                            status = "🟡 Recently online"
                        elif user.status == UserStatus.LAST_WEEK:
                            status = "🟠 Last seen within week"
                        elif user.status == UserStatus.LAST_MONTH:
                            status = "🔴 Last seen within month"
                    
                    response = (
                        "🌟 **User Information** 🌟\n\n"
                        f"👤 **Full Name:** {user.first_name} {user.last_name or ''}\n"
                        f"🆔 **User ID:** `{user.id}`\n"
                        f"🔖 **Username:** @{user.username}\n"
                        f"💬 **Chat Id:** `{chat.id}`\n"
                        f"🌐 **Data Center:** {user.dc_id} ({dc_location})\n"
                        f"💎 **Premium User:** {premium_status}\n"
                        f"🛡 **Verified:** {verified_status}\n"
                        f"🚩 **Flags:** {'⚠️ Scam' if getattr(user, 'is_scam', False) else '⚠️ Fake' if getattr(user, 'is_fake', False) else '✅ Clean'}\n"
                        f"🕒 **Status:** {status}\n"
                        f"📅 **Account Created On:** {account_created_str}\n"
                        f"⏳ **Account Age:** {account_age}"
                    )
                    if user.is_bot:
                        response = (
                            "🌟 **Bot Information** 🌟\n\n"
                            f"🤖 **Bot Name:** {user.first_name} {user.last_name or ''}\n"
                            f"🆔 **Bot ID:** `{user.id}`\n"
                            f"🔖 **Username:** @{user.username}\n"
                            f"🌐 **Data Center:** {user.dc_id} ({dc_location})\n"
                            f"💎 **Premium User:** {premium_status}\n"
                            f"🛡 **Verified:** {verified_status}\n"
                            f"🚩 **Flags:** {'⚠️ Scam' if getattr(user, 'is_scam', False) else '⚠️ Fake' if getattr(user, 'is_fake', False) else '✅ Clean'}\n"
                            f"📅 **Account Created On:** {account_created_str}\n"
                            f"⏳ **Account Age:** {account_age}"
                        )
                    buttons = [
                        [InlineKeyboardButton("✨ Android Link", url=f"tg://openmessage?user_id={user.id}"), InlineKeyboardButton("⚡️ iOS Link", url=f"tg://user?id={user.id}")],
                        [InlineKeyboardButton("💥 Permanent Link", user_id=user.id)],
                    ]
                    photo = await client.download_media(user.photo.big_file_id) if user.photo else PROFILE_ERROR_URL
                    await client.send_photo(chat_id=message.chat.id, photo=photo, caption=response, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))
                    logger.info("Replied user info fetched successfully with buttons")
                elif len(message.command) > 1:
                    # Extract username from the command
                    logger.info("Extracting username from the command")
                    username = message.command[1].strip('@').replace('https://', '').replace('http://', '').replace('t.me/', '').replace('/', '').replace(':', '')

                    try:
                        # First, attempt to get user or bot info
                        logger.info(f"Fetching info for user or bot: {username}")
                        user = await client.get_users(username)
                        premium_status = "✅ Yes" if user.is_premium else "❌ No"
                        dc_location = DC_LOCATIONS.get(user.dc_id, "Unknown")
                        account_created = estimate_account_creation_date(user.id)
                        account_created_str = account_created.strftime("%B %d, %Y")
                        account_age = calculate_account_age(account_created)
                        
                        # Added verification and status
                        verified_status = "✅ Yes" if getattr(user, 'is_verified', False) else "❌ No"
                        
                        status = "⚪️ Unknown"
                        if user.status:
                            if user.status == UserStatus.ONLINE:
                                status = "🟢 Online"
                            elif user.status == UserStatus.OFFLINE:
                                status = "⚫️ Offline"
                            elif user.status == UserStatus.RECENTLY:
                                status = "🟡 Recently online"
                            elif user.status == UserStatus.LAST_WEEK:
                                status = "🟠 Last seen within week"
                            elif user.status == UserStatus.LAST_MONTH:
                                status = "🔴 Last seen within month"
                        
                        response = (
                            "🌟 **User Information** 🌟\n\n"
                            f"👤 **Full Name:** {user.first_name} {user.last_name or ''}\n"
                            f"🆔 **User ID:** `{user.id}`\n"
                            f"🔖 **Username:** @{user.username}\n"
                            f"💬 **Chat Id:** `{user.id}`\n"
                            f"🌐 **Data Center:** {user.dc_id} ({dc_location})\n"
                            f"💎 **Premium User:** {premium_status}\n"
                            f"🛡 **Verified:** {verified_status}\n"
                            f"🚩 **Flags:** {'⚠️ Scam' if getattr(user, 'is_scam', False) else '⚠️ Fake' if getattr(user, 'is_fake', False) else '✅ Clean'}\n"
                            f"🕒 **Status:** {status}\n"
                            f"📅 **Account Created On:** {account_created_str}\n"
                            f"⏳ **Account Age:** {account_age}"
                        )
                        if user.is_bot:
                            response = (
                                "🌟 **Bot Information** 🌟\n\n"
                                f"🤖 **Bot Name:** {user.first_name} {user.last_name or ''}\n"
                                f"🆔 **Bot ID:** `{user.id}`\n"
                                f"🔖 **Username:** @{user.username}\n"
                                f"🌐 **Data Center:** {user.dc_id} ({dc_location})\n"
                                f"💎 **Premium User:** {premium_status}\n"
                                f"🛡 **Verified:** {verified_status}\n"
                                f"🚩 **Flags:** {'⚠️ Scam' if getattr(user, 'is_scam', False) else '⚠️ Fake' if getattr(user, 'is_fake', False) else '✅ Clean'}\n"
                                f"📅 **Account Created On:** {account_created_str}\n"
                                f"⏳ **Account Age:** {account_age}"
                            )
                        buttons = [
                            [InlineKeyboardButton("✨ Android Link", url=f"tg://openmessage?user_id={user.id}"), InlineKeyboardButton("⚡️ iOS Link", url=f"tg://user?id={user.id}")],
                            [InlineKeyboardButton("💥 Permanent Link", user_id=user.id)],
                        ]
                        photo = await client.download_media(user.photo.big_file_id) if user.photo else PROFILE_ERROR_URL
                        await client.send_photo(chat_id=message.chat.id, photo=photo, caption=response, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))
                        logger.info("User/bot info fetched successfully with buttons")
                    except (PeerIdInvalid, UsernameNotOccupied, IndexError):
                        logger.info(f"Username '{username}' not found as a user/bot. Checking for chat...")
                        try:
                            chat = await client.get_chat(username)
                            dc_location = DC_LOCATIONS.get(chat.dc_id, "Unknown")
                            response = (
                                f"🌟 **Chat Information** 🌟\n\n"
                                f"📛 **{chat.title}**\n"
                                f"🆔 **ID:** `{chat.id}`\n"
                                f"📌 **Type:** {'Supergroup' if chat.type == ChatType.SUPERGROUP else 'Group' if chat.type == ChatType.GROUP else 'Channel'}\n"
                                f"👥 **Member count:** {chat.members_count}"
                            )
                            buttons = [
                                [InlineKeyboardButton("⚡️Joining Link", url=f"t.me/c/{str(chat.id).replace('-100', '')}/100"), InlineKeyboardButton("💥 Permanent Link", url=f"t.me/c/{str(chat.id).replace('-100', '')}/100")],
                            ]
                            photo = await client.download_media(chat.photo.big_file_id) if chat.photo else PROFILE_ERROR_URL
                            await client.send_photo(chat_id=message.chat.id, photo=photo, caption=response, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))
                            logger.info("Chat info fetched successfully with buttons")
                        except (ChannelInvalid, PeerIdInvalid):
                            await client.send_message(chat_id=message.chat.id, text="**Looks like I don't have control over that user.**", parse_mode=ParseMode.MARKDOWN)
                        except Exception as e:
                            logger.error(f"Error fetching chat info: {str(e)}")
                            await client.send_message(chat_id=message.chat.id, text=f"**Looks like I don't have control over that user**", parse_mode=ParseMode.MARKDOWN)
                    except Exception as e:
                        logger.error(f"Error fetching user or bot info: {str(e)}")
                        await client.send_message(chat_id=message.chat.id, text=f"**Looks like I don't have control over that user**", parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Unhandled exception: {str(e)}")
                await client.send_message(chat_id=message.chat.id, text=f"**Looks like I don't have control over that user**", parse_mode=ParseMode.MARKDOWN)
            else:
                await progress_message.delete()
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")

@app.on_message(filters.command("start", prefixes=["/", ".", ",", "!"]) & (filters.group | filters.private))
async def start(client, message):
    buttons = [
        [InlineKeyboardButton("Update Channel", url="https://t.me/Modvip_rm"), InlineKeyboardButton("My Dev👨‍💻", user_id=7303810912)]
    ]
    await client.send_message(message.chat.id, START_MESSAGE, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))

app = Client("info_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
setup_info_handler(app)

if __name__ == "__main__":
    app.run()
