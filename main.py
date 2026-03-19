import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
import random
import string

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "ВАШ_ТОКЕН"
CHANNEL = "@eazyw1n"

quizzes = {}
results = {}
user_lang = {}

TEXTS = {
    'ru': {
        'start': "👋 Привет! Я бот для создания викторин.",
        'choose_lang': "🌍 Выбери язык / Choose language:",
        'lang_set': "✅ Язык установлен: Русский",
        'not_subscribed': "❌ Для использования бота подпишись на канал @eazyw1n\n\nПосле подписки нажми /start",
        'menu': (
            "📋 Меню:\n\n"
            "/create — создать викторину\n"
            "/play КОД — пройти викторину\n"
            "/results КОД — результаты\n"
            "/support — поддержка и реклама\n"
            "/lang — сменить язык"
        ),
        'support': (
            "📞 Связь:\n\n"
            "💬 Поддержка: @an0n1mmno\n"
            "📢 Реклама: @an0n1mmno\n\n"
            "Пишите по любым вопросам!"
        ),
        'enter_name': "📝 Как назовём викторину?",
        'enter_question': "✅ Отлично! Напиши вопрос:",
        'enter_a1': "1️⃣ Первый вариант ответа:",
        'enter_a2': "2️⃣ Второй вариант:",
        'enter_a3': "3️⃣ Третий вариант:",
        'enter_a4': "4️⃣ Четвёртый вариант:",
        'enter_correct': "✅ Какой правильный? Напиши цифру (1-4):",
        'invalid_number': "Напиши только цифру 1, 2, 3 или 4:",
        'question_added': "Вопрос добавлен! Всего вопросов: ",
        'add_more': "➕ Добавить вопрос",
        'finish': "✅ Завершить создание",
        'quiz_created': "🎉 Викторина создана!\n\n📋 Название: {name}\n❓ Вопросов: {count}\n\n🔑 Код: `{code}`\n\nДрузья могут пройти: /play {code}",
        'no_code': "Напиши код: /play КОД",
        'not_found': "❌ Викторина не найдена. Проверь код.",
        'start_quiz': "🎮 Начинаем: *{name}*\nВопросов: {count}",
        'correct': "✅ Правильно!",
        'wrong': "❌ Неправильно! Правильный ответ: {answer}",
        'finished': "🏁 Готово!\n\nРезультат: {score}/{total}\n\nРезультаты всех: /results {code}",
        'no_results': "Пока никто не прошёл эту викторину.",
        'results_title': "🏆 Результаты: {name}\n\n",
        'question_label': "❓ Вопрос {n}:\n\n{q}",
    },
    'en': {
        'start': "👋 Hello! I'm a quiz bot.",
        'choose_lang': "🌍 Выбери язык / Choose language:",
        'lang_set': "✅ Language set: English",
        'not_subscribed': "❌ To use the bot, subscribe to @eazyw1n\n\nAfter subscribing press /start",
        'menu': (
            "📋 Menu:\n\n"
            "/create — create a quiz\n"
            "/play CODE — take a quiz\n"
            "/results CODE — leaderboard\n"
            "/support — support & ads\n"
            "/lang — change language"
        ),
        'support': (
            "📞 Contacts:\n\n"
            "💬 Support: @an0n1mmno\n"
            "📢 Advertising: @an0n1mmno\n\n"
            "Feel free to message us!"
        ),
        'enter_name': "📝 What's the quiz name?",
        'enter_question': "✅ Great! Write your question:",
        'enter_a1': "1️⃣ First answer option:",
        'enter_a2': "2️⃣ Second option:",
        'enter_a3': "3️⃣ Third option:",
        'enter_a4': "4️⃣ Fourth option:",
        'enter_correct': "✅ Which is correct? Enter number (1-4):",
        'invalid_number': "Enter only 1, 2, 3 or 4:",
        'question_added': "Question added! Total questions: ",
        'add_more': "➕ Add question",
        'finish': "✅ Finish quiz",
        'quiz_created': "🎉 Quiz created!\n\n📋 Name: {name}\n❓ Questions: {count}\n\n🔑 Code: `{code}`\n\nFriends can play: /play {code}",
        'no_code': "Enter code: /play CODE",
        'not_found': "❌ Quiz not found. Check the code.",
        'start_quiz': "🎮 Starting: *{name}*\nQuestions: {count}",
        'correct': "✅ Correct!",
        'wrong': "❌ Wrong! Correct answer: {answer}",
        'finished': "🏁 Done!\n\nYour score: {score}/{total}\n\nLeaderboard: /results {code}",
        'no_results': "Nobody has taken this quiz yet.",
        'results_title': "🏆 Results: {name}\n\n",
        'question_label': "❓ Question {n}:\n\n{q}",
    }
}

def t(user_id, key, **kwargs):
    lang = user_lang.get(user_id, 'ru')
    text = TEXTS[lang][key]
    return text.format(**kwargs) if kwargs else text

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

(QUIZ_NAME, QUESTION_TEXT, ANSWER_1, ANSWER_2, ANSWER_3, ANSWER_4, CORRECT_ANSWER) = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_lang:
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
             InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(
            TEXTS['ru']['choose_lang'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    subscribed = await check_subscription(user_id, context.bot)
    if not subscribed:
        await update.message.reply_text(t(user_id, 'not_subscribed'))
        return
    await update.message.reply_text(t(user_id, 'menu'))

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    await update.message.reply_text(TEXTS['ru']['choose_lang'], reply_markup=InlineKeyboardMarkup(keyboard))

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(t(user_id, 'support'))

async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribed = await check_subscription(user_id, context.bot)
    if not subscribed:
        await update.message.reply_text(t(user_id, 'not_subscribed'))
        return ConversationHandler.END
    await update.message.reply_text(t(user_id, 'enter_name'))
    return QUIZ_NAME

async def quiz_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quiz_name'] = update.message.text
    context.user_data['questions'] = []
    await update.message.reply_text(t(update.effective_user.id, 'enter_question'))
    return QUESTION_TEXT

async def question_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_question'] = update.message.text
    await update.message.reply_text(t(update.effective_user.id, 'enter_a1'))
    return ANSWER_1

async def answer_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answers'] = [update.message.text]
    await update.message.reply_text(t(update.effective_user.id, 'enter_a2'))
    return ANSWER_2

async def answer_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answers'].append(update.message.text)
    await update.message.reply_text(t(update.effective_user.id, 'enter_a3'))
    return ANSWER_3

async def answer_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answers'].append(update.message.text)
    await update.message.reply_text(t(update.effective_user.id, 'enter_a4'))
    return ANSWER_4

async def answer_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answers'].append(update.message.text)
    await update.message.reply_text(t(update.effective_user.id, 'enter_correct'))
    return CORRECT_ANSWER

async def correct_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        correct = int(update.message.text)
        if correct not in [1, 2, 3, 4]:
            await update.message.reply_text(t(user_id, 'invalid_number'))
            return CORRECT_ANSWER
    except:
        await update.message.reply_text(t(user_id, 'invalid_number'))
        return CORRECT_ANSWER
    context.user_data['questions'].append({
        'question': context.user_data['current_question'],
        'answers': context.user_data['answers'],
        'correct': correct - 1
    })
    lang = user_lang.get(user_id, 'ru')
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]['add_more'], callback_data="add_question")],
        [InlineKeyboardButton(TEXTS[lang]['finish'], callback_data="finish_quiz")]
    ]
    await update.message.reply_text(
        t(user_id, 'question_added') + str(len(context.user_data['questions'])),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "lang_ru":
        user_lang[user_id] = 'ru'
        await query.message.reply_text(TEXTS['ru']['lang_set'])
        subscribed = await check_subscription(user_id, context.bot)
        if subscribed:
            await query.message.reply_text(t(user_id, 'menu'))
        else:
            await query.message.reply_text(t(user_id, 'not_subscribed'))
        return

    if query.data == "lang_en":
        user_lang[user_id] = 'en'
        await query.message.reply_text(TEXTS['en']['lang_set'])
        subscribed = await check_subscription(user_id, context.bot)
        if subscribed:
            await query.message.reply_text(t(user_id, 'menu'))
        else:
            await query.message.reply_text(t(user_id, 'not_subscribed'))
        return

    if query.data == "add_question":
        await query.message.reply_text(t(user_id, 'enter_question'))
        return

    if query.data == "finish_quiz":
        code = generate_code()
        quizzes[code] = {
            'name': context.user_data['quiz_name'],
            'questions': context.user_data['questions'],
            'author': query.from_user.first_name
        }
        results[code] = []
        await query.message.reply_text(
            t(user_id, 'quiz_created',
              name=context.user_data['quiz_name'],
              count=len(context.user_data['questions']),
              code=code),
            parse_mode='Markdown'
        )
        return

    if query.data.startswith("play_"):
        parts = query.data.split("_")
        code = parts[1]
        q_index = int(parts[2])
        selected = int(parts[3])
        quiz = quizzes[code]
        question = quiz['questions'][q_index]
        if 'play_data' not in context.user_data:
            context.user_data['play_data'] = {}
        if code not in context.user_data['play_data']:
            context.user_data['play_data'][code] = {'score': 0, 'total': len(quiz['questions'])}
        if selected == question['correct']:
            context.user_data['play_data'][code]['score'] += 1
            await query.message.reply_text(t(user_id, 'correct'))
        else:
            correct_text = question['answers'][question['correct']]
            await query.message.reply_text(t(user_id, 'wrong', answer=correct_text))
        next_index = q_index + 1
        if next_index < len(quiz['questions']):
            await send_question(query.message, code, next_index, user_lang.get(user_id, 'ru'))
        else:
            score = context.user_data['play_data'][code]['score']
            total = context.user_data['play_data'][code]['total']
            results[code].append({'name': query.from_user.first_name, 'score': score, 'total': total})
            await query.message.reply_text(t(user_id, 'finished', score=score, total=total, code=code))

async def send_question(message, code, q_index, lang='ru'):
    quiz = quizzes[code]
    question = quiz['questions'][q_index]
    keyboard = []
    for i, answer in enumerate(question['answers']):
        keyboard.append([InlineKeyboardButton(answer, callback_data=f"play_{code}_{q_index}_{i}")])
    await message.reply_text(
        TEXTS[lang]['question_label'].format(n=q_index + 1, q=question['question']),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribed = await check_subscription(user_id, context.bot)
    if not subscribed:
        await update.message.reply_text(t(user_id, 'not_subscribed'))
        return
    if not context.args:
        await update.message.reply_text(t(user_id, 'no_code'))
        return
    code = context.args[0].upper()
    if code not in quizzes:
        await update.message.reply_text(t(user_id, 'not_found'))
        return
    quiz = quizzes[code]
    await update.message.reply_text(
        t(user_id, 'start_quiz', name=quiz['name'], count=len(quiz['questions'])),
        parse_mode='Markdown'
    )
    await send_question(update.message, code, 0, user_lang.get(user_id, 'ru'))

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text(t(user_id, 'no_code'))
        return
    code = context.args[0].upper()
    if code not in quizzes:
        await update.message.reply_text(t(user_id, 'not_found'))
        return
    if not results[code]:
        await update.message.reply_text(t(user_id, 'no_results'))
        return
    sorted_results = sorted(results[code], key=lambda x: x['score'], reverse=True)
    text = t(user_id, 'results_title', name=quizzes[code]['name'])
    for i, r in enumerate(sorted_results):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
        text += f"{medal} {r['name']}: {r['score']}/{r['total']}\n"
    await update.message.reply_text(text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create_start)],
        states={
            QUIZ_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_name)],
            QUESTION_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_text)],
            ANSWER_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_1)],
            ANSWER_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_2)],
            ANSWER_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_3)],
            ANSWER_4: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_4)],
            CORRECT_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, correct_answer)],
        },
        fallbacks=[]
    )
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('play', play))
    app.add_handler(CommandHandler('results', show_results))
    app.add_handler(CommandHandler('support', support))
    app.add_handler(CommandHandler('lang', lang_command))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
