import os
import random
import json
import time
import asyncio
from datetime import datetime, date
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import ContextTypes, PicklePersistence, CommandHandler, CallbackQueryHandler, MessageHandler, filters, Application

# Translations dictionary
TRANSLATIONS = {
    'pl': {
        'start': '👋 Witaj {}!\n\nJestem twoim botem. Wpisz /menu aby zobaczyć opcje.',
        'stop': '👋 Do zobaczenia, {}!',
        'daily_spins': '🎰 Masz 5 darmowych spinów dzisiaj!',
        'buy_5': '💰 Kup 5 spinów (5 ⭐️)',
        'no_spins': '❌ Nie masz już spinów.\n\nMożesz kupić więcej używając gwiazdek Telegram.',
        'spinning': '🎰 Kręcenie...',
        'win': '🎉 WYGRANA! {} siódemek!',
        'bonus': '✨ Pozostało spinów: {}',
        'loss': '😔 Nie tym razem. {} siódemek.',
        'remaining': '💫 Pozostało spinów: {}',
        'admin_bonus': '✅ Dodano 5 spinów! Pozostało: {}',
        'canceled': '❌ Anulowano',
        'choose_option': '📋 Wybierz opcję:',
        'commands_list': '📜 Lista komend:\n/start - Rozpocznij\n/stop - Zatrzymaj\n/spin - Zagraj w slot\n/checkspins - Sprawdź stan spinów\n/menu - Menu\n/langulagi - Zmień język\n/block - Zablokuj bota\n/unblock - Odblokuj bota',
        'games_list': '🎮 Lista gier:\n/game - Gra główna\n/gamedinorun - Dino Run\n/viemgame - Viem Game',
        'unknown_command': '❓ Nieznana komenda. Wpisz /menu aby zobaczyć dostępne opcje.',
        'unknown_message': '❓ Nie rozumiem. Wpisz /menu aby zobaczyć dostępne opcje.',
        'no_ads': '❌ Brak dostępnych reklam.',
        'ad_thanks': '✅ Dziękuję za obejrzenie! Otrzymałeś dodatkowy spin. Pozostało: {}',
        'language_selected': '✅ Język został zmieniony!',
        'payment_success': '✅ Płatność zakończona sukcesem! Masz teraz {} spinów.',
        'ads': []
    },
    'en': {
        'start': '👋 Hello {}!\n\nI am your bot. Type /menu to see options.',
        'stop': '👋 See you later, {}!',
        'daily_spins': '🎰 You have 5 free spins today!',
        'buy_5': '💰 Buy 5 spins (5 ⭐️)',
        'no_spins': '❌ You have no spins left.\n\nYou can buy more using Telegram stars.',
        'spinning': '🎰 Spinning...',
        'win': '🎉 WIN! {} sevens!',
        'bonus': '✨ Spins remaining: {}',
        'loss': '😔 Not this time. {} sevens.',
        'remaining': '💫 Spins remaining: {}',
        'admin_bonus': '✅ Added 5 spins! Remaining: {}',
        'canceled': '❌ Canceled',
        'choose_option': '📋 Choose an option:',
        'commands_list': '📜 Command list:\n/start - Start\n/stop - Stop\n/spin - Play slot\n/checkspins - Check spin balance\n/menu - Menu\n/langulagi - Change language\n/block - Block bot\n/unblock - Unblock bot',
        'games_list': '🎮 Games list:\n/game - Main game\n/gamedinorun - Dino Run\n/viemgame - Viem Game',
        'unknown_command': '❓ Unknown command. Type /menu to see available options.',
        'unknown_message': '❓ I don\'t understand. Type /menu to see available options.',
        'no_ads': '❌ No ads available.',
        'ad_thanks': '✅ Thanks for watching! You received an extra spin. Remaining: {}',
        'language_selected': '✅ Language changed!',
        'payment_success': '✅ Payment successful! You now have {} spins.',
        'ads': []
    },
    'ru': {
        'start': '👋 Привет {}!\n\nЯ твой бот. Напиши /menu чтобы увидеть опции.',
        'stop': '👋 До скорого, {}!',
        'daily_spins': '🎰 У тебя 5 бесплатных спинов сегодня!',
        'buy_5': '💰 Купить 5 спинов (5 ⭐️)',
        'no_spins': '❌ У тебя не осталось спинов.\n\nТы можешь купить больше используя звезды Telegram.',
        'spinning': '🎰 Прокрутка...',
        'win': '🎉 ВЫИГРЫШ! {} семерок!',
        'bonus': '✨ Осталось спинов: {}',
        'loss': '😔 Не в этот раз. {} семерок.',
        'remaining': '💫 Осталось спинов: {}',
        'admin_bonus': '✅ Добавлено 5 спинов! Осталось: {}',
        'canceled': '❌ Отменено',
        'choose_option': '📋 Выбери опцию:',
        'commands_list': '📜 Список команд:\n/start - Начать\n/stop - Остановить\n/spin - Играть в слот\n/checkspins - Проверить баланс спинов\n/menu - Меню\n/langulagi - Сменить язык\n/block - Заблокировать бота\n/unblock - Разблокировать бота',
        'games_list': '🎮 Список игр:\n/game - Основная игра\n/gamedinorun - Dino Run\n/viemgame - Viem Game',
        'unknown_command': '❓ Неизвестная команда. Напиши /menu чтобы увидеть доступные опции.',
        'unknown_message': '❓ Я не понимаю. Напиши /menu чтобы увидеть доступные опции.',
        'no_ads': '❌ Нет доступных рекламных объявлений.',
        'ad_thanks': '✅ Спасибо за просмотр! Ты получил дополнительный спин. Осталось: {}',
        'language_selected': '✅ Язык изменен!',
        'payment_success': '✅ Платеж успешен! Теперь у тебя {} спинов.',
        'ads': []
    }
}

async def killmeasege(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /killmeasege command - asks for confirmation to delete bot messages"""
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    # Initialize message tracking if not exists
    if 'bot_messages' not in context.user_data:
        context.user_data['bot_messages'] = []
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Tak", callback_data="killmsg_yes"),
            InlineKeyboardButton("Nie", callback_data="killmsg_no")
        ]
    ])
    
    msg_count = len(context.user_data['bot_messages'])
    confirm_msg = await update.message.reply_text(
        f"⚠️ Czy na pewno chcesz usunąć wiadomości od bota?\n\nŚledzonych wiadomości: {msg_count}",
        reply_markup=keyboard
    )
    
    # Try to delete the command message
    try:
        await update.message.delete()
    except:
        pass

async def button_killmeasege_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "killmsg_yes":
        chat_id = query.message.chat_id
        deleted = 0
        
        # Initialize if not exists
        if 'bot_messages' not in context.user_data:
            context.user_data['bot_messages'] = []
        
        # Delete all tracked bot messages
        for msg_id in context.user_data.get('bot_messages', []):
            try:
                await context.bot.delete_message(chat_id, msg_id)
                deleted += 1
            except Exception:
                pass
        
        # Clear the list
        context.user_data['bot_messages'] = []
        
        # Delete the confirmation message
        await query.edit_message_text(f"✅ Usunięto {deleted} wiadomości.")
    
    elif query.data == "killmsg_no":
        await query.edit_message_text("❌ Anulowano.")

def get_text(context, key, *args):
    """Get translated text based on user's language preference"""
    lang = context.user_data.get('language', 'pl')  # Default to Polish
    text = TRANSLATIONS.get(lang, TRANSLATIONS['pl']).get(key, key)
    if args:
        return text.format(*args)
    return text

async def track_message(msg, context):
    """Track bot message for later deletion with /killmeasege"""
    if 'bot_messages' not in context.user_data:
        context.user_data['bot_messages'] = []
    context.user_data['bot_messages'].append(msg.message_id)
    # Keep only last 100 messages to avoid memory issues
    if len(context.user_data['bot_messages']) > 100:
        context.user_data['bot_messages'] = context.user_data['bot_messages'][-100:]
    return msg

def get_user_spins(user_id, context):
    """Get total spin count for user (combining user_data and transferred spins from bot_data)"""
    today = str(date.today())
    
    # Initialize user_data if needed
    if 'spin_uses' not in context.user_data:
        context.user_data['spin_uses'] = 5
        context.user_data['spin_date'] = today
    
    # Reset daily spins if new day
    if context.user_data.get('spin_date') != today:
        context.user_data['spin_uses'] = 5
        context.user_data['spin_date'] = today
    
    # Get transferred spins from bot_data
    transferred_spins = 0
    if 'user_spins' in context.bot_data and user_id in context.bot_data['user_spins']:
        transferred_spins = context.bot_data['user_spins'][user_id].get('spin_uses', 0)
    
    return context.user_data['spin_uses'] + transferred_spins

def use_user_spin(user_id, context):
    """Use one spin - prefer using transferred spins first"""
    # First try to use transferred spins
    if 'user_spins' in context.bot_data and user_id in context.bot_data['user_spins']:
        if context.bot_data['user_spins'][user_id].get('spin_uses', 0) > 0:
            context.bot_data['user_spins'][user_id]['spin_uses'] -= 1
            return
    
    # Otherwise use daily spins
    if context.user_data.get('spin_uses', 0) > 0:
        context.user_data['spin_uses'] -= 1

def add_user_spins(user_id, context, amount):
    """Add spins to user (to daily pool)"""
    if 'spin_uses' not in context.user_data:
        context.user_data['spin_uses'] = 5
        context.user_data['spin_date'] = str(date.today())
    
    context.user_data['spin_uses'] += amount

def remove_user_spins(user_id, context, amount):
    """Remove spins from user (from daily pool first, then transferred)"""
    # First try to remove from daily pool
    daily_spins = context.user_data.get('spin_uses', 0)
    if daily_spins >= amount:
        context.user_data['spin_uses'] -= amount
    else:
        # Remove what we can from daily pool
        context.user_data['spin_uses'] = 0
        remaining = amount - daily_spins
        
        # Remove rest from transferred spins
        if 'user_spins' in context.bot_data and user_id in context.bot_data['user_spins']:
            transferred_spins = context.bot_data['user_spins'][user_id].get('spin_uses', 0)
            if transferred_spins >= remaining:
                context.bot_data['user_spins'][user_id]['spin_uses'] -= remaining
            else:
                context.bot_data['user_spins'][user_id]['spin_uses'] = 0

async def reply_and_track(update, context, text, **kwargs):
    """Send reply and automatically track it"""
    msg = await update.message.reply_text(text, **kwargs)
    await track_message(msg, context)
    return msg

async def send_and_track(bot, context, chat_id, text, **kwargs):
    """Send message and automatically track it"""
    msg = await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    await track_message(msg, context)
    return msg


async def check_language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user has selected a language. If not, ask them to choose.
    Returns True if language is selected, False otherwise."""
    if 'language' not in context.user_data:
        # First time user - ask for language
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_pl")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
        ])
        
        await update.message.reply_text(
            "🌍 Choose your language / Wybierz język / Выберите язык:",
            reply_markup=keyboard
        )
        return False
    return True

async def check_if_blocked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user has blocked the bot. If blocked, do nothing (silence).
    Returns True if blocked, False otherwise."""
    if context.user_data.get('bot_blocked', False):
        # Bot is blocked - don't respond to anything except /unblock
        return True
    return False

def get_random_ad(context):
    """Get a random advertisement based on user's language"""
    lang = context.user_data.get('language', 'pl')  # Default to Polish
    ads = TRANSLATIONS.get(lang, TRANSLATIONS['pl']).get('ads', [])
    if ads:
        return random.choice(ads)
    return None

async def send_ad_if_lucky(update, context, chance_percent=30):
    """Send advertisement with chance_percent probability"""
    if random.randint(1, 100) <= chance_percent:
        ad = get_random_ad(context)
        if ad:
            # Return ad data to be included in main message
            return f"\n\n📢 {ad['text']}", InlineKeyboardMarkup([[InlineKeyboardButton(ad['button_text'], url=ad['url'])]])
    return "", None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    user_name = update.effective_user.first_name
    print(f"/start omfr {user_name}")
    
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    ad_text, ad_keyboard = await send_ad_if_lucky(update, context)
    message_text = get_text(context, 'start', user_name) + ad_text
    
    if ad_keyboard:
        await reply_and_track(update, context, message_text, reply_markup=ad_keyboard)
    else:
        await reply_and_track(update, context, message_text)

async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /block command - blocks the bot for the user"""
    user_name = update.effective_user.first_name
    context.user_data['bot_blocked'] = True
    await reply_and_track(update, context,
        "🚫 Bot jest zablokowany.\n\nNapisz komendę: /unblock aby odblokować bota."
    )
    print(f"/block from {user_name} - bot blocked")

async def unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /unblock command - unblocks the bot for the user"""
    user_name = update.effective_user.first_name
    context.user_data['bot_blocked'] = False
    await reply_and_track(update, context, "✅ Bot został odblokowany! Możesz teraz korzystać ze wszystkich komend.")
    print(f"/unblock from {user_name} - bot unblocked")

async def checkspins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /checkspins command - shows current spin balance"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    today = str(date.today())
    
    # Get total spins using helper function
    total_spins = get_user_spins(user_id, context)
    
    # Get breakdown
    daily_spins = context.user_data.get('spin_uses', 0)
    transferred_spins = 0
    if 'user_spins' in context.bot_data and user_id in context.bot_data['user_spins']:
        transferred_spins = context.bot_data['user_spins'][user_id].get('spin_uses', 0)
    
    last_date = context.user_data.get('spin_date', 'nieznana')
    
    message = f"🎰 Twój stan spinów:\n\n"
    message += f"💫 Całkowite spiny: {total_spins}\n"
    message += f"   └ Dzienne spiny: {daily_spins}\n"
    if transferred_spins > 0:
        message += f"   └ Dodatkowe spiny: {transferred_spins}\n"
    message += f"📅 Ostatnia aktualizacja: {last_date}\n"
    message += f"🆔 Twoje ID: {user_id}"
    
    await reply_and_track(update, context, message)
    print(f"/checkspins from {user_name} (ID: {user_id}) - total spins: {total_spins}")

async def langulagi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /langulagi command - language selection"""
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_pl")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ])
    
    ad_text, ad_keyboard = await send_ad_if_lucky(update, context)
    message_text = "🌍 Choose your language / Wybierz język / Выберите язык:" + ad_text
    
    # Combine language selection keyboard with ad keyboard if ad is present
    if ad_keyboard:
        # Add ad button to existing keyboard
        combined_keyboard = InlineKeyboardMarkup(
            keyboard.inline_keyboard + ad_keyboard.inline_keyboard
        )
        await reply_and_track(update, context, message_text, reply_markup=combined_keyboard)
    else:
        await reply_and_track(update, context, message_text, reply_markup=keyboard)

def get_total_wins(user_id):
    """Get total number of wins for a user"""
    data_file = "spin_data.json"
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return sum(1 for record in data if record.get('user_id') == user_id and record.get('result') == 'win')
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_spin_data(user_id, user_name, result, seven_count, remaining_uses):
    """Save spin game data to JSON file"""
    data_file = "spin_data.json"
    
    # Przygotuj dane
    spin_record = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "user_name": user_name,
        "result": result,  # "win" lub "loss"
        "seven_count": seven_count,
        "remaining_uses": remaining_uses
    }
    
    # Wczytaj istniejące dane
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # Dodaj nowy rekord
    data.append(spin_record)
    
    # Zapisz do pliku
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /stop command"""
    user_name = update.effective_user.first_name
    print(f"/stop from {user_name}")
    
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    ad_text, ad_keyboard = await send_ad_if_lucky(update, context)
    message_text = get_text(context, 'stop', user_name) + ad_text
    
    if ad_keyboard:
        await reply_and_track(update, context, message_text, reply_markup=ad_keyboard)
    else:
        await reply_and_track(update, context, message_text)

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /game command"""
    user_name = update.effective_user.first_name
    print(f"/game from {user_name}")
    
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    # Wyślij przycisk z linkiem do gry
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Zagraj w grę", url="https://marks-game.base44.app/")]
    ])

    await reply_and_track(update, context,
        "Kliknij przycisk poniżej, aby zagrać:",
        reply_markup=keyboard
    )
async def gamedinorun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /gamedinorun command"""
    user_name = update.effective_user.first_name
    print(f"/gamedinorun from {user_name}")
    
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    await reply_and_track(update, context, "https://game.zhasan.online/Projekt%20Scratch%20final.html")

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /spin command - slot machine game with daily limit"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    today = str(date.today())
    
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    # Get total spins using helper function
    total_spins = get_user_spins(user_id, context)
    
    # Jeśli saldo = 5, wyślij powiadomienie (tylko dla dziennych spinów)
    if context.user_data.get('spin_uses', 0) == 5 and context.user_data.get('spin_date') == today:
        transferred_spins = 0
        if 'user_spins' in context.bot_data and user_id in context.bot_data['user_spins']:
            transferred_spins = context.bot_data['user_spins'][user_id].get('spin_uses', 0)
        
        if transferred_spins == 0:  # Only show daily message if no transferred spins
            await reply_and_track(update, context, get_text(context, 'daily_spins'))
    
    # Sprawdź czy ma jeszcze użycia
    if total_spins <= 0:
        # Inicjalizuj listę obejrzanych reklam
        if 'viewed_ads' not in context.user_data:
            context.user_data['viewed_ads'] = []
        
        # Pokaż przycisk zakupu
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text(context, 'buy_5'), callback_data="buy_spin_5")]
        ])
        
        message_text = get_text(context, 'no_spins')
        
        await reply_and_track(update, context, message_text, reply_markup=keyboard)
        return
    
    # Zmniejsz licznik using helper function
    use_user_spin(user_id, context)
    
    # Emoji do slot machine
    emojis = ["🍒", "⭐️", "💎", "🍀", "🍋", "7️⃣"]
    

    # Wyślij wiadomość o kręceniu
    spin_msg = await reply_and_track(update, context, get_text(context, 'spinning') + "\n\n🎲 🎲 🎲\n🎲 🎲 🎲\n🎲 🎲 🎲")
    
    # Ani/comandsmacja kręcenia (5 klatek)
    for _ in range(5):
        await asyncio.sleep(0.3)
        random_board = [[random.choice(emojis) for _ in range(3)] for _ in range(3)]
        board_str = ""
        for row in random_board:
            board_str += "|" + "|".join(row) + "|\n"
        
        await spin_msg.edit_text(f"{get_text(context, 'spinning')}\n\n{board_str}")
    
    # Generuj losową planszę 3x3 - końcowy wynik
    board = [[random.choice(emojis) for _ in range(3)] for _ in range(3)]
    
    # Wyświetl planszę
    board_str = ""
    seven_count = 0
    
    for row in board:
        row_str = "|" + "|".join(row) + "|"
        board_str += row_str + "\n"
        seven_count += row.count("7️⃣")
    
    # Sprawdź wygraną
    if seven_count >= 4:
        result = get_text(context, 'win', seven_count)
        add_user_spins(user_id, context, 2)  # +2 bonus za wygraną
        remaining = get_user_spins(user_id, context)
        message = f"```\n{board_str}```\n{result}\n{get_text(context, 'bonus', remaining)}"
        print(f"/spin from {user_name} - WYGRANA: {seven_count}x 7️⃣ (bonus +2)")
        save_spin_data(user_id, user_name, "win", seven_count, remaining)
        
        # Check if user has won exactly 3 times total
        total_wins = get_total_wins(user_id)
        if total_wins == 3:
            print(f"User {user_name} (ID: {user_id}) has won {total_wins} times!")
            # Note: Removed input() call as it blocks async bot
            # TODO: Implement proper reward system without blocking
            print("Note: User eligible for 5 Telegram stars reward")
    else:
        remaining = get_user_spins(user_id, context)
        result = get_text(context, 'loss', seven_count)
        message = f"```\n{board_str}```\n{result}\n{get_text(context, 'remaining', remaining)}"
        print(f"/spin from {user_name} - przegrana: {seven_count}x 7️⃣ (pozostało {remaining})")
        save_spin_data(user_id, user_name, "loss", seven_count, remaining)
    
    await spin_msg.edit_text(message, parse_mode="Markdown")

def is_admin(user_id):
    """Check if user is admin"""
    admin_id = os.getenv('ADMIN_USER_ID')
    if admin_id:
        try:
            return int(admin_id) == user_id
        except ValueError:
            return False
    return False

async def print_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /print command - admin only - send message to user"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Check if user is admin
    if not is_admin(user_id):
        await reply_and_track(update, context, "❌ Nie masz uprawnień do tej komendy.")
        print(f"UNAUTHORIZED: /print attempt by {user_name} (ID: {user_id})")
        return
    
    # Start conversation - ask for username
    context.user_data['print_state'] = 'waiting_for_username'
    context.user_data['print_type'] = 'normal'
    
    await reply_and_track(update, context, "📨 Wysyłanie wiadomości\n\nWpisz username odbiorcy (np. @username) lub ID użytkownika:")
    
    print(f"ADMIN: /print started by {user_name} (ID: {user_id})")
    
    # Delete command message
    try:
        await update.message.delete()
    except:
        pass

async def printsecret_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /printsecret command - admin only - send spoiler message to user"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Check if user is admin
    if not is_admin(user_id):
        await reply_and_track(update, context, "❌ Nie masz uprawnień do tej komendy.")
        print(f"UNAUTHORIZED: /printsecret attempt by {user_name} (ID: {user_id})")
        return
    
    # Start conversation - ask for username
    context.user_data['print_state'] = 'waiting_for_username'
    context.user_data['print_type'] = 'spoiler'
    
    await reply_and_track(update, context, "🔒 Wysyłanie tajnej wiadomości\n\nWpisz username odbiorcy (np. @username) lub ID użytkownika:")
    
    print(f"ADMIN: /printsecret started by {user_name} (ID: {user_id})")
    
    # Delete command message
    try:
        await update.message.delete()
    except:
        pass

async def spinaddon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /spinaddon12346405459054059049 command - admin command to add 5 spin uses"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Inicjalizuj dane użytkownika jeśli nie istnieją
    if 'spin_uses' not in context.user_data:
        context.user_data['spin_uses'] = 5
        context.user_data['spin_date'] = str(date.today())
    
    # Dodaj 5 użyć
    context.user_data['spin_uses'] += 5
    remaining = context.user_data['spin_uses']
    
    await reply_and_track(update, context, get_text(context, 'admin_bonus', remaining))
    
    print(f"ADMIN: /spinaddon from {user_name} (ID: {user_id}) - added 5 uses, total: {remaining}")
    
    # Usuń wiadomość z komendą
    await update.message.delete()

async def spinaddon_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /spinaddon12334445849583958495 command - admin command to transfer spins to another user"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Start conversation - ask for user ID
    context.user_data['spinaddon_state'] = 'waiting_for_user_id'
    
    await reply_and_track(update, context, "🔧 Transfer spinów\n\nWpisz ID użytkownika, któremu chcesz przekazać spiny:")
    
    print(f"ADMIN: /spinaddon_transfer started by {user_name} (ID: {user_id})")
    
    # Usuń wiadomość z komendą
    try:
        await update.message.delete()
    except:
        pass

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /cancel command - shows menu"""
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎡 Spin", callback_data="btn_spin"),
            InlineKeyboardButton("📋 Commands", callback_data="btn_comands"),
            InlineKeyboardButton("🎮 Play", callback_data="btn_play")
        ]
    ])
    
    await reply_and_track(update, context, get_text(context, 'canceled'), reply_markup=keyboard)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /menu command - shows menu without 'canceled' message"""
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎡 Spin", callback_data="btn_spin"),
            InlineKeyboardButton("📋 Commands", callback_data="btn_comands"),
            InlineKeyboardButton("🎮 Play", callback_data="btn_play")
        ]
    ])
    
    await reply_and_track(update, context, get_text(context, 'choose_option'), reply_markup=keyboard)

async def comands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /comands command"""
    user_name = update.effective_user.first_name
    print(f"/comands from {user_name}")
    
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    ad_text, ad_keyboard = await send_ad_if_lucky(update, context)
    message_text = get_text(context, 'commands_list') + ad_text
    
    if ad_keyboard:
        await reply_and_track(update, context, message_text, reply_markup=ad_keyboard)
    else:
        await reply_and_track(update, context, message_text)

async def viemgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /viemgame command - list of all games"""
    user_name = update.effective_user.first_name
    print(f"/viemgame from {user_name}")
    
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    # Check if language is selected
    if not await check_language_selected(update, context):
        return
    
    ad_text, ad_keyboard = await send_ad_if_lucky(update, context)
    message_text = get_text(context, 'games_list') + ad_text
    
    if ad_keyboard:
        await reply_and_track(update, context, message_text, reply_markup=ad_keyboard)
    else:
        await reply_and_track(update, context, message_text)

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for unknown commands"""
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    await reply_and_track(update, context, get_text(context, 'unknown_command'))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for text messages - checks for specific words and handles conversation states"""
    # Check if bot is blocked
    if await check_if_blocked(update, context):
        return
    
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    # Handle print conversation states (admin only)
    if 'print_state' in context.user_data:
        state = context.user_data['print_state']
        print_type = context.user_data.get('print_type', 'normal')
        
        if state == 'waiting_for_username':
            # User entered username or user ID
            target = message_text
            context.user_data['print_target'] = target
            context.user_data['print_state'] = 'waiting_for_message'
            await reply_and_track(update, context, f"✅ Odbiorca: {target}\n\nWpisz wiadomość do wysłania:")
            print(f"PRINT: {user_name} (ID: {user_id}) - target: {target}")
            return
        
        elif state == 'waiting_for_message':
            # User entered message to send
            target = context.user_data.get('print_target')
            
            try:
                # Try to send message to target
                if target.startswith('@'):
                    # It's a username - we need to use chat_id
                    # Unfortunately, we can't directly send to username without chat_id
                    # So we'll inform admin to use user ID instead
                    await reply_and_track(update, context, 
                        "❌ Nie można wysłać wiadomości bezpośrednio do username.\n"
                        "Użyj ID użytkownika zamiast username.")
                    del context.user_data['print_state']
                    del context.user_data['print_target']
                    del context.user_data['print_type']
                    return
                else:
                    # It's a user ID
                    target_id = int(target)
                    
                    # Prepare message
                    if print_type == 'spoiler':
                        # Use HTML spoiler tag
                        message_to_send = f"<tg-spoiler>{message_text}</tg-spoiler>"
                        parse_mode = "HTML"
                    else:
                        message_to_send = message_text
                        parse_mode = None
                    
                    # Send message to target user
                    if parse_mode:
                        await context.bot.send_message(chat_id=target_id, text=message_to_send, parse_mode=parse_mode)
                    else:
                        await context.bot.send_message(chat_id=target_id, text=message_to_send)
                    
                    # Confirm to admin
                    msg_type = "tajną wiadomość" if print_type == 'spoiler' else "wiadomość"
                    await reply_and_track(update, context, 
                        f"✅ Wysłano {msg_type} do użytkownika {target_id}")
                    
                    print(f"PRINT: {user_name} (ID: {user_id}) - sent {print_type} message to {target_id}")
                    
            except ValueError:
                await reply_and_track(update, context, "❌ Nieprawidłowe ID użytkownika.")
            except Exception as e:
                await reply_and_track(update, context, f"❌ Błąd wysyłania: {str(e)}")
                print(f"PRINT ERROR: {e}")
            
            # Clear state
            del context.user_data['print_state']
            del context.user_data['print_target']
            del context.user_data['print_type']
            return
    
    # Handle spinaddon conversation states
    if 'spinaddon_state' in context.user_data:
        state = context.user_data['spinaddon_state']
        
        if state == 'waiting_for_user_id':
            # User entered a user ID
            try:
                target_user_id = int(message_text)
                context.user_data['spinaddon_target_id'] = target_user_id
                context.user_data['spinaddon_state'] = 'waiting_for_amount'
                await reply_and_track(update, context, f"✅ ID użytkownika: {target_user_id}\n\nIle spinów chcesz przekazać na to konto?")
                print(f"SPINADDON: {user_name} (ID: {user_id}) - entered target ID: {target_user_id}")
            except ValueError:
                await reply_and_track(update, context, "❌ Nieprawidłowe ID. Wpisz prawidłowy numer ID użytkownika.")
            return
        
        elif state == 'waiting_for_amount':
            # User entered amount of spins to transfer
            try:
                amount = int(message_text)
                if amount <= 0:
                    await reply_and_track(update, context, "❌ Liczba spinów musi być większa niż 0.")
                    return
                
                target_user_id = context.user_data.get('spinaddon_target_id')
                
                # Load persistence data to access target user's data
                # We need to use bot_data to store cross-user transfers
                if 'user_spins' not in context.bot_data:
                    context.bot_data['user_spins'] = {}
                
                # Add spins to target user
                if target_user_id not in context.bot_data['user_spins']:
                    context.bot_data['user_spins'][target_user_id] = {'spin_uses': 0, 'spin_date': str(date.today())}
                
                context.bot_data['user_spins'][target_user_id]['spin_uses'] += amount
                
                # Clear state
                del context.user_data['spinaddon_state']
                del context.user_data['spinaddon_target_id']
                
                await reply_and_track(update, context, 
                    f"✅ Pomyślnie dodano {amount} spinów dla użytkownika {target_user_id}\n\n"
                    f"Nowe saldo: {context.bot_data['user_spins'][target_user_id]['spin_uses']} spinów")
                
                print(f"SPINADDON: {user_name} (ID: {user_id}) - added {amount} spins to user {target_user_id}")
                
                # Try to notify target user if possible
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"🎁 Otrzymałeś {amount} spinów od administratora!\n\nTwoje nowe saldo: {context.bot_data['user_spins'][target_user_id]['spin_uses']} spinów"
                    )
                except:
                    print(f"Could not notify user {target_user_id} about spin transfer")
                
            except ValueError:
                await reply_and_track(update, context, "❌ Nieprawidłowa liczba. Wpisz liczbę spinów (np. 5).")
            return
    
    if "гей" in message_text.lower():
        print(f"'{update.message.text}' from {user_name}")

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for unknown messages"""
    await reply_and_track(update, context, get_text(context, 'unknown_message'))

async def button_buy_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buy spin button click - send invoice for 5 stars"""
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    await query.answer()
    
    # Send invoice for 5 Telegram Stars
    try:
        await context.bot.send_invoice(
            chat_id=user_id,
            title="Kup 5 użyć /spin",
            description="Otrzymaj 5 dodatkowych użyć komendy /spin",
            payload="spin_5_uses",
            provider_token="",  # Not needed for stars
            currency="XTR",
            prices=[LabeledPrice("5 użyć /spin", 5)]  # 5 stars
        )
        print(f"Invoice sent to {user_name} (ID: {user_id})")
    except Exception as e:
        print(f"Failed to send invoice to {user_name} (ID: {user_id}): {e}")
        await send_and_track(context.bot, context, user_id, "Błąd podczas wysyłania faktury. Spróbuj ponownie później.")

async def button_ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ad button click"""
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    # Inicjalizuj listę obejrzanych reklam
    if 'viewed_ads' not in context.user_data:
        context.user_data['viewed_ads'] = []
    
    if query.data == "ad_luckystars1":
        # Sprawdź czy już obejrzał
        if 'luckystars1' in context.user_data['viewed_ads']:
            # Już oglądał - pokaż alert
            await query.answer(get_text(context, 'no_ads'), show_alert=True)
            return
        
        # Oznacz jako obejrzane
        context.user_data['viewed_ads'].append('luckystars1')
            
        # Dodaj 5 użyć /spin using helper function
        add_user_spins(user_id, context, 5)
        remaining = get_user_spins(user_id, context)
        
        # Odpowiedz na callback
        await query.answer()
        
        # Wyślij link do bota
        await send_and_track(
            context.bot, context, user_id,
            get_text(context, 'ad_thanks', remaining)
        )
        
        print(f"Ad viewed by {user_name} - luckystars1 (+5 spin uses, total: {remaining})")

async def button_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    if query.data == "btn_spin":
        # Wykonaj /spin - wyślij jako nową wiadomość
        today = str(date.today())
        
        # Get total spins using helper function
        total_spins = get_user_spins(user_id, context)
        
        # Jeśli saldo = 5, wyślij powiadomienie (tylko dla dziennych spinów)
        if context.user_data.get('spin_uses', 0) == 5 and context.user_data.get('spin_date') == today:
            transferred_spins = 0
            if 'user_spins' in context.bot_data and user_id in context.bot_data['user_spins']:
                transferred_spins = context.bot_data['user_spins'][user_id].get('spin_uses', 0)
            
            if transferred_spins == 0:  # Only show daily message if no transferred spins
                await send_and_track(context.bot, context, user_id, get_text(context, 'daily_spins'))
        
        # Sprawdź czy ma jeszcze użycia
        if total_spins <= 0:
            # Inicjalizuj listę obejrzanych reklam
            if 'viewed_ads' not in context.user_data:
                context.user_data['viewed_ads'] = []
            
            # Pokaż przycisk zakupu
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(context, 'buy_5'), callback_data="buy_spin_5")]
            ])
            
            message_text = get_text(context, 'no_spins')
            
            await send_and_track(
                context.bot, context, user_id,
                message_text,
                reply_markup=keyboard
            )
            return
        
        # Zmniejsz licznik using helper function
        use_user_spin(user_id, context)
        
        # Emoji do slot machine
        emojis = ["🍒", "⭐️", "💎", "🍀", "🍋", "7️⃣"]
        
        # Wyślij wiadomość o kręceniu
        spin_msg = await send_and_track(
            context.bot, context, user_id,
            get_text(context, 'spinning') + "\n\n🎲 🎲 🎲\n🎲 🎲 🎲\n🎲 🎲 🎲"
        )
        
        # Animacja kręcenia (5 klatek)
        for _ in range(5):
            await asyncio.sleep(0.3)
            random_board = [[random.choice(emojis) for _ in range(3)] for _ in range(3)]
            board_str = ""
            for row in random_board:
                board_str += "|" + "|".join(row) + "|\n"
            
            await spin_msg.edit_text(f"{get_text(context, 'spinning')}\n\n{board_str}")
        
        # Generuj losową planszę 3x3 - końcowy wynik
        board = [[random.choice(emojis) for _ in range(3)] for _ in range(3)]
        
        # Wyświetl planszę
        board_str = ""
        seven_count = 0
        
        for row in board:
            row_str = "|" + "|".join(row) + "|"
            board_str += row_str + "\n"
            seven_count += row.count("7️⃣")
        
        # Sprawdź wygraną
        if seven_count >= 4:
            result = get_text(context, 'win', seven_count)
            add_user_spins(user_id, context, 2)  # +2 bonus za wygraną
            remaining = get_user_spins(user_id, context)
            message = f"```\n{board_str}```\n{result}\n{get_text(context, 'bonus', remaining)}"
            print(f"/spin from {user_name} - WYGRANA: {seven_count}x 7️⃣ (bonus +2)")
            save_spin_data(user_id, user_name, "win", seven_count, remaining)
        else:
            remaining = get_user_spins(user_id, context)
            result = get_text(context, 'loss', seven_count)
            message = f"```\n{board_str}```\n{result}\n{get_text(context, 'remaining', remaining)}"
            print(f"/spin from {user_name} - przegrana: {seven_count}x 7️⃣ (pozostało {remaining})")
            save_spin_data(user_id, user_name, "loss", seven_count, remaining)
        
        await spin_msg.edit_text(message, parse_mode="Markdown")
    
    elif query.data == "btn_comands":
        # Wykonaj /comands
        print(f"/comands from {user_name}")
        await send_and_track(context.bot, context, user_id, get_text(context, 'commands_list'))
    
    elif query.data == "btn_play":
        # Wykonaj /viemgame
        print(f"/viemgame from {user_name}")
        await send_and_track(context.bot, context, user_id, get_text(context, 'games_list'))

async def button_language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection button clicks"""
    query = update.callback_query
    user_name = query.from_user.first_name
    
    if query.data == "lang_en":
        context.user_data['language'] = 'en'
        await query.answer()
        await query.edit_message_text(get_text(context, 'language_selected'))
        print(f"Language set to English for {user_name}")
    elif query.data == "lang_pl":
        context.user_data['language'] = 'pl'
        await query.answer()
        await query.edit_message_text(get_text(context, 'language_selected'))
        print(f"Language set to Polish for {user_name}")
    elif query.data == "lang_ru":
        context.user_data['language'] = 'ru'
        await query.answer()
        await query.edit_message_text(get_text(context, 'language_selected'))
        print(f"Language set to Russian for {user_name}")

async def button_undo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Undo button clicks"""
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    # Get undo data from bot_data (global)
    undo_key = f"undo_{user_id}"
    undo_data = context.bot_data.get(undo_key)
    
    if query.data == "undo_payment":
        # First click on Undo - show dice animation
        current_time = time.time()
        
        print(f"🔔 UNDO BUTTON CLICKED by {user_name} (ID: {user_id})")
        print(f"   Current time: {current_time}")
        print(f"   Undo key: {undo_key}")
        print(f"   Has undo data: {undo_data is not None}")
        
        if undo_data:
            timeout = undo_data.get('timeout', 0)
            is_valid = current_time <= timeout
            
            print(f"   Timeout value: {timeout}")
            print(f"   Time remaining: {timeout - current_time}s")
            print(f"   Is valid: {is_valid}")
        else:
            print(f"   ❌ No undo data found in bot_data")
        
        if undo_data and time.time() <= undo_data.get('timeout', 0):
            
            # Mark that user clicked Undo
            undo_data['in_progress'] = True
            print(f"Undo in progress for {user_name}")
            
            # Create dice board
            dice_board = """|🎲|🎲|🎲|
|🎲|🎲|🎲|
|🎲|🎲|🎲|"""
            
            # Create second undo button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Undo (10s)", callback_data="undo_payment_confirm")]
            ])
            
            await query.answer()
            await query.edit_message_text(dice_board, reply_markup=keyboard)
            
            # Mark that dice animation is shown
            undo_data['dice_shown'] = True
            undo_data['dice_shown_at'] = time.time()
            
            # Wait 10 seconds (increased from 3)
            await asyncio.sleep(10)
            
            # Check if user didn't click second undo
            if undo_data.get('dice_shown', False):
                # User didn't cancel - keep payment, remove undo
                del context.bot_data[undo_key]
                
                try:
                    await query.edit_message_text("✅ Płatność potwierdzona.")
                except:
                    pass
        else:
            print(f"❌ UNDO REJECTED for {user_name}:")
            if undo_data:
                print(f"   Timeout exceeded: {time.time()} > {undo_data.get('timeout', 0)}")
            else:
                print(f"   No undo data in bot_data")
            await query.answer("⏰ Czas na anulowanie minął.", show_alert=True)
    
    elif query.data == "undo_payment_confirm":
        # Second click on Undo during dice animation - cancel payment
        if undo_data and undo_data.get('dice_shown', False):
            charge_id = undo_data.get('charge_id')
            if charge_id:
                try:
                    # Refund the payment
                    await context.bot.refund_star_payment(user_id, charge_id)
                    
                    # Remove the 5 spins using helper function
                    remove_user_spins(user_id, context, 5)
                    
                    # Clear undo data from bot_data
                    del context.bot_data[undo_key]
                    
                    await query.answer()
                    await query.edit_message_text("❌ Płatność anulowana. Gwiazdki zwrócone.")
                    print(f"✅ Payment undone for {user_name} (ID: {user_id})")
                except Exception as e:
                    await query.answer("Błąd podczas anulowania płatności.", show_alert=True)
                    print(f"Failed to undo payment for {user_name}: {e}")
            else:
                await query.answer("Brak informacji o płatności.", show_alert=True)
        else:
            await query.answer("⏰ Za późno na anulowanie.", show_alert=True)

async def handle_pre_checkout_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout query - must answer to allow payment to proceed"""
    query = update.pre_checkout_query
    await query.answer(ok=True)
    print(f"Pre-checkout approved for user {query.from_user.first_name}")

async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    charge_id = payment.telegram_payment_charge_id
    
    print(f"=== PAYMENT RECEIVED ===")
    print(f"User: {user_name} (ID: {user_id})")
    print(f"Charge ID: {charge_id}")
    print(f"Payload: {payment.invoice_payload}")
    print(f"Before payment - spin_uses: {context.user_data.get('spin_uses', 'NOT SET')}")
    
    if payment.invoice_payload == "spin_5_uses":
        try:
            # Get current spins
            old_spins = get_user_spins(user_id, context)
            
            # Dodaj 5 użyć using helper function
            add_user_spins(user_id, context, 5)
            new_spins = get_user_spins(user_id, context)
            
            print(f"Added 5 spins: {old_spins} -> {new_spins}")
            
            # Wymuś zapisanie persistence
            context.application.persistence.update_user_data(user_id, context.user_data)
            await context.application.persistence.flush()
            print(f"Persistence saved successfully")
            
            # Weryfikacja - sprawdź czy spiny zostały dodane
            expected_spins = old_spins + 5
            actual_spins = get_user_spins(user_id, context)
            
            if actual_spins != expected_spins:
                # Błąd - spiny nie zostały dodane poprawnie
                print(f"⚠️ VERIFICATION FAILED! Expected: {expected_spins}, Got: {actual_spins}")
                raise Exception(f"Spin verification failed: expected {expected_spins}, got {actual_spins}")
            
            print(f"✅ Verification passed: {actual_spins} spins")
            
            # Clean up old undo data for this user if exists
            undo_key = f"undo_{user_id}"
            if undo_key in context.bot_data:
                print(f"🧹 Cleaning up old undo data for user {user_id}")
                del context.bot_data[undo_key]
            
            # Create Undo button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("↩️ Undo (10s)", callback_data="undo_payment")]
            ])
            
            # Store payment info for potential undo
            # Use bot_data (global) instead of user_data to avoid sync issues
            undo_key = f"undo_{user_id}"
            context.bot_data[undo_key] = {
                'charge_id': charge_id,
                'timeout': time.time() + 10,
                'spin_uses': get_user_spins(user_id, context)
            }
            
            print(f"🔔 UNDO DATA SAVED to bot_data['{undo_key}']:")
            print(f"   Timeout: {context.bot_data[undo_key]['timeout']} (current: {time.time()}, diff: {context.bot_data[undo_key]['timeout'] - time.time()}s)")
            
            # Send success message with Undo button
            undo_msg = await reply_and_track(update, context,
                get_text(context, 'payment_success', get_user_spins(user_id, context)),
                reply_markup=keyboard
            )
            
            print(f"Payment successful: {user_name} (ID: {user_id}) - 5 stars received")
            print(f"Final spin_uses: {get_user_spins(user_id, context)}")
            print(f"======================")
            
            # Wyślij powiadomienie właścicielowi
            owner_id = int(os.getenv('OWNER_ID', '0'))
            if owner_id:
                try:
                    await context.bot.send_message(
                        chat_id=owner_id,
                        text=f"💫 Nowa płatność!\nUżytkownik: {user_name} (ID: {user_id})\nGwiazdki: ⭐️5\nPrzypis: @markzhos"
                    )
                except:
                    pass
            
            # Wait 10 seconds then remove Undo button (but keep data for safety)
            await asyncio.sleep(10)
            
            # Just remove the button, keep undo data (will be cleaned on next payment or manually)
            undo_key = f"undo_{user_id}"
            try:
                await undo_msg.edit_reply_markup(reply_markup=None)
                await undo_msg.edit_text(get_text(context, 'payment_success', context.user_data['spin_uses']))
                print(f"✅ Undo button removed after 10s for user {user_id}")
            except:
                pass
                        
        except Exception as e:
            print(f"Error adding spins for {user_name} (ID: {user_id}): {e}")
            print(f"Stack trace:", exc_info=True)
            # Refund the payment
            try:
                await context.bot.refund_star_payment(user_id, charge_id)
                await reply_and_track(update, context,
                    "❌ Błąd podczas przetwarzania płatności.\n\n"
                    "✅ Twoje gwiazdki zostały zwrócone.\n\n"
                    "Spróbuj ponownie za chwilę lub skontaktuj się z supportem."
                )
                print(f"✅ Refunded payment for {user_name} (ID: {user_id})")
            except Exception as refund_error:
                print(f"❌ Failed to refund payment for {user_name} (ID: {user_id}): {refund_error}")
                await reply_and_track(update, context,
                    "❌ Błąd podczas przetwarzania płatności i zwrotu pieniędzy.\n\n"
                    f"Skontaktuj się z supportem podając ID: {user_id}"
                )

def main():
    """Start the bot"""
    # Load environment variables from .env file
    load_dotenv()

    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        print("Error: Set the TELEGRAM_BOT_TOKEN environment variable")
        return

    # Create persistence to save user data
    persistence = PicklePersistence(filepath='bot_data.pkl')

    # Create application with persistence
    application = Application.builder().token(token).persistence(persistence).build()

    # Register command handlers
    application.add_handler(CommandHandler("killmeasege", killmeasege))
    application.add_handler(CallbackQueryHandler(button_killmeasege_handler, pattern="killmsg_yes|killmsg_no"))
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("game", game))
    application.add_handler(CommandHandler("gamedinorun", gamedinorun))
    application.add_handler(CommandHandler("viemgame", viemgame))
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(CommandHandler("spinaddon128138027103739247239", spinaddon))
    application.add_handler(CommandHandler("spinaddon12334445849583958495", spinaddon_transfer))
    application.add_handler(CommandHandler("print", print_command))
    application.add_handler(CommandHandler("printsecret", printsecret_command))
    application.add_handler(CommandHandler("cancel", cancel))

    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("comands", comands))
    application.add_handler(CommandHandler("langulagi", langulagi))
    application.add_handler(CommandHandler("block", block))
    application.add_handler(CommandHandler("unblock", unblock))
    application.add_handler(CommandHandler("checkspins", checkspins))
    
    # Register callback handlers for buttons
    application.add_handler(CallbackQueryHandler(button_buy_spin, pattern="buy_spin_5"))
    application.add_handler(CallbackQueryHandler(button_ad_handler, pattern="ad_.*"))
    application.add_handler(CallbackQueryHandler(button_menu_handler, pattern="btn_spin|btn_comands|btn_play"))
    application.add_handler(CallbackQueryHandler(button_language_handler, pattern="lang_.*"))
    application.add_handler(CallbackQueryHandler(button_undo_handler, pattern="undo_.*"))
    
    # Register payment handlers
    from telegram.ext import PreCheckoutQueryHandler
    application.add_handler(PreCheckoutQueryHandler(handle_pre_checkout_query))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))
    
    # Register handler for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))
    
    # Register handler for text messages (checks for keywords)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register handler for unknown messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))
    
    # Start the bot
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()