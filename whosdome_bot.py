from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
import threading
import random
import html

API_TOKEN = ''
bot = TeleBot(API_TOKEN)

game_players = defaultdict(set)
message_tracker = {}
game_state = defaultdict(lambda: "idle")  # There 3 game states - idle, registering, playing
registration_timers = {}
game_mode = {}  # There are 2 game modes - intrigue and non-intrigue
chat_questions = {}  # list of questions uploaded from files questions.txt and questions1.txt (depends on game mode)

def load_questions_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{e}")
        return []

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def block_private_usage(message):
    bot.send_message(message.chat.id, "➕ Добавь меня в группу, и только тогда мы сможем играть!")

@bot.message_handler(commands=['start_game'])
def handle_start_game(message):
    chat_id = message.chat.id
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    if message.chat.type not in ['group', 'supergroup']:
        bot.send_message(chat_id, "⛔ Эта команда доступна только в группах.")
        return
    if game_state[chat_id] in ("registering", "playing"):
        sent_msg = bot.send_message(chat_id, "⚠️ Игра уже идёт или регистрация открыта. Завершите текущую игру командой /reset_game перед началом новой.")
        threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()
        return
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎭 Интрига", callback_data=f"mode:intrigue:{chat_id}"),
        InlineKeyboardButton("🎲 Обычная", callback_data=f"mode:non-intrigue:{chat_id}")
    )
    bot.send_message(chat_id, "🕹️ Выберите режим игры:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mode:"))
def handle_mode_selection(call):
    try:
        _, mode, chat_id = call.data.split(":")
        chat_id = int(chat_id)
    except:
        return
    if game_state[chat_id] != "idle":
        bot.answer_callback_query(call.id, text="Игра уже активна.")
        return
    game_mode[chat_id] = mode
    game_state[chat_id] = "registering"
    filename = "questions1.txt" if mode == "intrigue" else "questions.txt"
    chat_questions[chat_id] = load_questions_from_file(filename)
    game_players[chat_id].clear()
    timer = registration_timers.get(chat_id)
    if timer:
        timer.cancel()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎮 Присоединиться", callback_data=f"join:{chat_id}"))
    msg = bot.send_message(chat_id, build_player_list(chat_id), reply_markup=markup)
    message_tracker[chat_id] = msg.message_id
    bot.answer_callback_query(call.id, text="✅ Режим выбран. Регистрация началась!")
    timer = threading.Timer(60.0, auto_start_game, args=(chat_id,))
    registration_timers[chat_id] = timer
    timer.start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("join:"))
def handle_join_callback(call):
    chat_id = int(call.data.split(":")[1])
    user = call.from_user
    if game_state.get(chat_id) != "registering":
        bot.answer_callback_query(call.id, text="⏳ Регистрация закрыта.")
        return
    player = (user.id, user.full_name)
    if player in game_players[chat_id]:
        bot.answer_callback_query(call.id, text="✅ Ты уже в игре!")
        return
    game_players[chat_id].add(player)
    try:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎮 Присоединиться", callback_data=f"join:{chat_id}"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_tracker[chat_id],
            text=build_player_list(chat_id),
            reply_markup=markup
        )
    except Exception as e:
        print(f"[ERROR] Failed to edit message: {e}")
    bot.answer_callback_query(call.id, text="✅ Ты в игре!")

@bot.message_handler(commands=['join_game'])
def join_game_after_registration(message):
    chat_id = message.chat.id
    user = message.from_user
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    if game_state.get(chat_id) != "playing":
        sent_msg = bot.send_message(chat_id, "⚠️ Игра ещё не началась. Сейчас можно присоединяться только через кнопку.")
        threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()
        return
    player = (user.id, user.full_name)
    if player in game_players[chat_id]:
        sent_msg = bot.send_message(chat_id, "✅ Ты уже в игре!")
        threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()
    else:
        game_players[chat_id].add(player)
        bot.send_message(chat_id, f"🎮 {user.full_name} присоединился к игре!")

@bot.message_handler(commands=['leave_game'])
def leave_game(message):
    chat_id = message.chat.id
    user = message.from_user
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    if game_state.get(chat_id) != "playing":
        sent_msg = bot.send_message(chat_id, "⚠️ Игра не идёт. Ты не можешь выйти.")
        threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()
        return
    player = (user.id, user.full_name)
    if player in game_players[chat_id]:
        game_players[chat_id].remove(player)
        bot.send_message(chat_id, f"👋 {user.full_name} покинул(а) игру.")
    else:
        bot.send_message(chat_id, "❌ Ты не в игре.")

@bot.message_handler(commands=['members'])
def show_members_count(message):
    chat_id = message.chat.id
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    if game_state.get(chat_id) != "playing":
        sent_msg = bot.send_message(chat_id, "⚠️ Игра не идёт. Команда /members доступна только во время игры.")
        threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()
        return
    count = len(game_players.get(chat_id, set()))
    bot.send_message(chat_id, f"👥 Сейчас в игре {count} участник(ов).")

@bot.message_handler(commands=['question'])
def send_random_question(message):
    chat_id = message.chat.id
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    if game_state.get(chat_id) != "playing":
        sent_msg = bot.send_message(chat_id, "⚠️ Игра ещё не началась. Пожалуйста, дождитесь окончания регистрации.")
        threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()
        return
    result = pick_random_question(chat_id)
    bot.send_message(chat_id, result, parse_mode="HTML")

@bot.message_handler(commands=['reset_game'])
def reset_game(message):
    chat_id = message.chat.id
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    if game_state[chat_id] == "idle":
        sent_msg = bot.send_message(chat_id, "⚠️ Нет активной игры для сброса.")
        threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()
        return
    game_players[chat_id].clear()
    game_state[chat_id] = "idle"
    message_tracker.pop(chat_id, None)
    game_mode.pop(chat_id, None)
    chat_questions.pop(chat_id, None)
    timer = registration_timers.get(chat_id)
    if timer:
        timer.cancel()
        registration_timers.pop(chat_id, None)
    sent_msg = bot.send_message(chat_id, "♻️ Игра сброшена. Можете начать заново с /start_game")
    #threading.Timer(5.0, lambda: bot.delete_message(chat_id, sent_msg.message_id)).start()

@bot.message_handler(commands=['instructions'])
def show_instructions(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    instructions = (
        "📘 <b>Инструкции по командам:</b>\n\n"
        "• /start_game - начать новую игру и выбрать режим\n"
        "• /join_game - присоединиться к игре (во время активной игры)\n"
        "• /leave_game - покинуть игру (во время активной игры)\n"
        "• /members - показать количество игроков (только во время игры)\n"
        "• /question - задать случайный вопрос случайному участнику\n"
        "• /reset_game - сбросить текущую игру\n"
        "• /instructions - показать это сообщение\n"
    )
    bot.send_message(message.chat.id, instructions, parse_mode="HTML")

def auto_reset_game(chat_id):
    game_players[chat_id].clear()
    game_state[chat_id] = "idle"
    message_tracker.pop(chat_id, None)
    game_mode.pop(chat_id, None)
    chat_questions.pop(chat_id, None)
    timer = registration_timers.get(chat_id)
    if timer:
        timer.cancel()
        registration_timers.pop(chat_id, None)
    try:
        bot.send_message(chat_id, "♻️ Игра автоматически сброшена из-за недостаточного количества игроков.")
    except Exception as e:
        print(f"[ERROR] Failed to notify auto-reset: {e}")

def auto_start_game(chat_id):
    players = game_players.get(chat_id, set())
    if len(players) < 1:
        auto_reset_game(chat_id)
        return
    game_state[chat_id] = "playing"
    timer = registration_timers.get(chat_id)
    if timer:
        timer.cancel()
        registration_timers.pop(chat_id, None)
    text = build_player_list(chat_id)
    text += (
        "\n\n🚀 Игра началась! Регистрация закрыта.\n"
        "Используйте /question, чтобы задать вопрос.\n"
        "Используйте /reset_game, чтобы закончить игру.\n"
        "Команда /join_game позволяет новым участникам присоединиться.\n"
        "Команда /leave_game позволяет выйти из игры."
    )
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=message_tracker[chat_id], text=text)
    except Exception as e:
        print(f"[ERROR] Failed to start game in chat {chat_id}: {e}")

def build_player_list(chat_id):
    players = game_players.get(chat_id, set())
    if not players:
        return "🎯 Пока никто не зарегистрировался.\nНажмите кнопку ниже, чтобы присоединиться!"
    return "👥 Зарегистрированные игроки:\n" + "\n".join([f"• {html.escape(name)}" for _, name in players])

def pick_random_question(chat_id):
    players = game_players.get(chat_id, set())
    questions = chat_questions.get(chat_id, [])
    if not players or not questions:
        return "😐 Нет зарегистрированных игроков или вопросов."
    user_id, random_name = random.choice(list(players))
    question = random.choice(questions)
    mention = f'<a href="tg://user?id={user_id}">{html.escape(random_name)}</a>'
    return f"🎲 Вопрос для: {mention}\n\n<i>{html.escape(question)}</i>"

bot.infinity_polling()
