import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8628159718:AAH8tPnTX0fReDzpByMG44A-iF6HG-Pm5-8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========== КНОПКИ ГЛАВНОГО МЕНЮ ==========
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Список клиентов")],
        [KeyboardButton(text="➕ Добавить клиента")],
        [KeyboardButton(text="📊 Статистика")],
    ],
    resize_keyboard=True
)

# ========== ХРАНИЛИЩЕ ==========
clients = {}
next_id = 1
waiting_for = {}

# ========== КОМАНДА /start ==========
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🤖 *Добро пожаловать в CRM-бот!*\n\n"
        "👇 Нажми на кнопку ниже, чтобы начать",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

# ========== СПИСОК КЛИЕНТОВ ==========
@dp.message(lambda msg: msg.text == "📋 Список клиентов")
async def show_list(message: types.Message):
    if not clients:
        await message.answer("📭 Пока нет клиентов.\nНажми «➕ Добавить клиента»")
        return
    
    text = "📋 *Мои клиенты:*\n\n"
    for cid, client in clients.items():
        text += f"🆔 `{cid}` — *{client['name']}*\n"
        text += f"📞 {client['phone']}\n"
        text += f"📌 {client['status']}\n\n"
    
    # Кнопки для каждого клиента
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"👤 #{cid} {client['name']}", callback_data=f"view_{cid}")]
        for cid, client in clients.items()
    ])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

# ========== ДОБАВЛЕНИЕ КЛИЕНТА ==========
@dp.message(lambda msg: msg.text == "➕ Добавить клиента")
async def add_start(message: types.Message):
    user_id = message.from_user.id
    waiting_for[user_id] = {}
    await message.answer("✍️ Введи *имя* клиента:", parse_mode="Markdown")

# ========== ОБРАБОТКА ВВОДА ==========
@dp.message()
async def handle_input(message: types.Message):
    user_id = message.from_user.id
    
    # Пропускаем команды и кнопки меню
    if message.text in ["📋 Список клиентов", "➕ Добавить клиента", "📊 Статистика"]:
        return
    if message.text.startswith("/"):
        return
    
    if user_id not in waiting_for:
        return
    
    global next_id
    
    if "name" not in waiting_for[user_id]:
        waiting_for[user_id]["name"] = message.text
        await message.answer("📞 Введи *телефон* клиента:", parse_mode="Markdown")
    else:
        name = waiting_for[user_id]["name"]
        phone = message.text
        
        clients[next_id] = {
            "name": name,
            "phone": phone,
            "status": "Новый",
            "note": ""
        }
        
        await message.answer(
            f"✅ *Клиент добавлен!*\n\n"
            f"🆔 ID: `{next_id}`\n"
            f"📛 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"📌 Статус: Новый",
            parse_mode="Markdown",
            reply_markup=main_kb
        )
        
        del waiting_for[user_id]
        next_id += 1

# ========== СТАТИСТИКА ==========
@dp.message(lambda msg: msg.text == "📊 Статистика")
async def show_stats(message: types.Message):
    total = len(clients)
    if total == 0:
        await message.answer("📊 *Статистика*\n\nПока нет клиентов.", parse_mode="Markdown")
        return
    
    status_count = {}
    for client in clients.values():
        status_count[client["status"]] = status_count.get(client["status"], 0) + 1
    
    text = f"📊 *Статистика*\n\n👥 Всего: *{total}*\n\n"
    for status, count in status_count.items():
        text += f"• {status}: {count}\n"
    
    await message.answer(text, parse_mode="Markdown")

# ========== ПРОСМОТР КЛИЕНТА ==========
@dp.callback_query(lambda call: call.data.startswith("view_"))
async def view_client(call: types.CallbackQuery):
    client_id = int(call.data.split("_")[1])
    client = clients.get(client_id)
    
    if not client:
        await call.answer("Клиент не найден", show_alert=True)
        return
    
    # Кнопки статусов
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Новый", callback_data=f"status_{client_id}_Новый")],
        [InlineKeyboardButton(text="🟡 В работе", callback_data=f"status_{client_id}_В работе")],
        [InlineKeyboardButton(text="🔵 Договор", callback_data=f"status_{client_id}_Договор")],
        [InlineKeyboardButton(text="✅ Закрыт", callback_data=f"status_{client_id}_Закрыт")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_list")]
    ])
    
    text = f"*🆔 Клиент #{client_id}*\n\n"
    text += f"📛 *Имя:* {client['name']}\n"
    text += f"📞 *Телефон:* {client['phone']}\n"
    text += f"📌 *Статус:* {client['status']}"
    
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await call.answer()

# ========== ИЗМЕНЕНИЕ СТАТУСА ==========
@dp.callback_query(lambda call: call.data.startswith("status_"))
async def change_status(call: types.CallbackQuery):
    parts = call.data.split("_")
    client_id = int(parts[1])
    new_status = parts[2]
    
    if client_id in clients:
        clients[client_id]["status"] = new_status
        await call.answer(f"✅ Статус изменён на {new_status}")
        
        # Обновляем карточку
        client = clients[client_id]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Новый", callback_data=f"status_{client_id}_Новый")],
            [InlineKeyboardButton(text="🟡 В работе", callback_data=f"status_{client_id}_В работе")],
            [InlineKeyboardButton(text="🔵 Договор", callback_data=f"status_{client_id}_Договор")],
            [InlineKeyboardButton(text="✅ Закрыт", callback_data=f"status_{client_id}_Закрыт")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_list")]
        ])
        
        text = f"*🆔 Клиент #{client_id}*\n\n"
        text += f"📛 *Имя:* {client['name']}\n"
        text += f"📞 *Телефон:* {client['phone']}\n"
        text += f"📌 *Статус:* {client['status']}"
        
        await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await call.answer("❌ Клиент не найден", show_alert=True)

# ========== НАЗАД ==========
@dp.callback_query(lambda call: call.data == "back_to_list")
async def back_to_list(call: types.CallbackQuery):
    if not clients:
        await call.message.edit_text("📭 Пока нет клиентов")
        return
    
    text = "📋 *Мои клиенты:*\n\n"
    for cid, client in clients.items():
        text += f"🆔 `{cid}` — *{client['name']}*\n"
        text += f"📞 {client['phone']}\n"
        text += f"📌 {client['status']}\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"👤 #{cid} {client['name']}", callback_data=f"view_{cid}")]
        for cid, client in clients.items()
    ])
    
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await call.answer()

# ========== ЗАПУСК ==========
async def main():
    print("🤖 CRM-бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    