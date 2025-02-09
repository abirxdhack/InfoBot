from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied, ChannelInvalid
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN

def setup_info_handler(app: Client):
    @app.on_message(filters.command("info", prefixes=["/", "."]) & (filters.private | filters.group))
    async def handle_info_command(client, message: Message):
        if message.command is None or (len(message.command) == 1 and not message.reply_to_message):
            if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                # Show group info if in a group and no user info is provided
                chat = message.chat
                response = (
                    f"📛 <b>Group Name:</b> <code>{chat.title}</code>\n"
                    f"🆔 <b>Group ID:</b> <code>{chat.id}</code>\n"
                    f"👥 <b>Member Count:</b> <code>{chat.members_count}</code>"
                )
                await message.reply_text(response, parse_mode=ParseMode.HTML)
            else:
                # No username or chat provided, show current user info
                user = message.from_user
                response = (
                    f"🌟 <b>Full Name:</b> <code>{user.first_name} {user.last_name or ''}</code>\n"
                    f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
                    f"🔖 <b>Username:</b> <code>@{user.username}</code>\n"
                    f"💬 <b>Chat Id:</b> <code>{user.id}</code>"
                )
                await message.reply_text(response, parse_mode=ParseMode.HTML)
        elif message.reply_to_message:
            # Show info of the replied user or bot
            user = message.reply_to_message.from_user
            response = (
                f"🌟 <b>Full Name:</b> <code>{user.first_name} {user.last_name or ''}</code>\n"
                f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
                f"🔖 <b>Username:</b> <code>@{user.username}</code>\n"
                f"💬 <b>Chat Id:</b> <code>{user.id}</code>"
            )
            if user.is_bot:
                response = (
                    f"🤖 <b>Bot Name:</b> <code>{user.first_name} {user.last_name or ''}</code>\n"
                    f"🆔 <b>Bot ID:</b> <code>{user.id}</code>\n"
                    f"🔖 <b>Username:</b> <code>@{user.username}</code>"
                )
            await message.reply_text(response, parse_mode=ParseMode.HTML)
        else:
            # Extract username from the command
            username = message.command[1].strip('@').replace('https://', '').replace('http://', '').replace('t.me/', '').replace('/', '').replace(':', '')

            try:
                # First, attempt to get user or bot info
                user = await client.get_users([username])
                if user:
                    user = user[0]
                    response = (
                        f"🌟 <b>Full Name:</b> <code>{user.first_name} {user.last_name or ''}</code>\n"
                        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
                        f"🔖 <b>Username:</b> <code>@{user.username}</code>\n"
                        f"💬 <b>Chat Id:</b> <code>{user.id}</code>"
                    )
                    if user.is_bot:
                        response = (
                            f"🤖 <b>Bot Name:</b> <code>{user.first_name} {user.last_name or ''}</code>\n"
                            f"🆔 <b>Bot ID:</b> <code>{user.id}</code>\n"
                            f"🔖 <b>Username:</b> <code>@{user.username}</code>"
                        )
                    await message.reply_text(response, parse_mode=ParseMode.HTML)
                else:
                    # If not a user, try fetching chat info (group/channel)
                    try:
                        chat = await client.get_chat(username)

                        if chat.type == ChatType.CHANNEL:
                            response = (
                                f"📛 <b>{chat.title}</b>\n"
                                f"━━━━━━━━━━━━━━━━━━\n"
                                f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
                                f"📌 <b>Type:</b> <code>Channel</code>\n"
                                f"👥 <b>Member count:</b> <code>{chat.members_count}</code>"
                            )
                        elif chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
                            response = (
                                f"📛 <b>{chat.title}</b>\n"
                                f"━━━━━━━━━━━━━━━━━━\n"
                                f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
                                f"📌 <b>Type:</b> <code>{'Supergroup' if chat.type == ChatType.SUPERGROUP else 'Group'}</code>\n"
                                f"👥 <b>Member count:</b> <code>{chat.members_count}</code>"
                            )
                        else:
                            response = "<b>Invalid chat type</b>"
                        await message.reply_text(response, parse_mode=ParseMode.HTML)
                    except (ChannelInvalid, PeerIdInvalid):
                        await message.reply_text(
                            "<b>Sorry Bro Wrong Username ❌</b>",
                            parse_mode=ParseMode.HTML
                        )
                    except Exception:
                        await message.reply_text(f"<b>Sorry Bro Wrong Username ❌</b>", parse_mode=ParseMode.HTML)
            
            except (PeerIdInvalid, UsernameNotOccupied):
                # Show group info if user info cannot be fetched
                if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    chat = message.chat
                    response = (
                        f"📛 <b>Group Name:</b> <code>{chat.title}</code>\n"
                        f"🆔 <b>Group ID:</b> <code>{chat.id}</code>\n"
                        f"👥 <b>Member Count:</b> <code>{chat.members_count}</code>"
                    )
                    await message.reply_text(response, parse_mode=ParseMode.HTML)
                else:
                    await message.reply_text(
                        "<b>Sorry Bro Wrong Username ❌</b>",
                        parse_mode=ParseMode.HTML
                    )
            except Exception:
                await message.reply_text(f"<b>Sorry Bro Wrong Username ❌</b>", parse_mode=ParseMode.HTML)

app = Client("info_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
setup_info_handler(app)

if __name__ == "__main__":
    app.run()