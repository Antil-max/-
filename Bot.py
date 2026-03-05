import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("8351853660:AAERVwrBgc-Roj6AsniqnolQwQSR8_FagO4")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1957240625"))


PAYMENT_INFO = """💳 Реквизиты для оплаты:
Сбербанк: +7 (XXX) XXX-XX-XX
Тинькофф: +7 (XXX) XXX-XX-XX

📸 После оплаты пришлите скриншот сюда!"""

# Структура: Предмет → Учитель → Товары
SUBJECTS = {
    "Русский язык": {
        "teacher": "Е. А. Пантелеева",
        "products": {
            "pen": {"name": "Ручка", "price": 50},
            "notebook": {"name": "Блокнот", "price": 100},
            "sticker": {"name": "Стикер", "price": 30},
            "badge": {"name": "Значок", "price": 80}
        }
    },
    "Литература": {
        "teacher": "П. Ф. Подковыркин",
        "products": {
            "pen": {"name": "Ручка", "price": 50},
            "notebook": {"name": "Блокнот", "price": 100},
            "sticker": {"name": "Стикер", "price": 30},
            "badge": {"name": "Значок", "price": 80}
        }
    },
    "Теория познания": {
        "teacher": "И. С. Курилович",
        "products": {
            "pen": {"name": "Ручка", "price": 50},
            "notebook": {"name": "Блокнот", "price": 100},
            "sticker": {"name": "Стикер", "price": 30},
            "badge": {"name": "Значок", "price": 80}
        }
    }
}

user_carts = {}

def get_main_keyboard():
    """Главное меню - 4 кнопки"""
    keyboard = [
        [InlineKeyboardButton("👨‍🏫 Учителя", callback_data='menu_teachers')],
        [InlineKeyboardButton("📦 Виды товаров", callback_data='menu_products')],
        [InlineKeyboardButton("🛒 Корзина", callback_data='view_cart')],
        [InlineKeyboardButton("💡 Ваши идеи", callback_data='ideas')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_subjects_keyboard():
    """Список предметов"""
    keyboard = []
    for subject_name in SUBJECTS.keys():
        keyboard.append([InlineKeyboardButton(subject_name, callback_data=f'subject_{subject_name}')])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='back_main')])
    return InlineKeyboardMarkup(keyboard)

def get_subject_products_keyboard(subject_name):
    """Товары конкретного предмета/учителя"""
    subject = SUBJECTS[subject_name]
    teacher = subject['teacher']
    
    keyboard = []
    for product_id, product_info in subject['products'].items():
        button_text = f"{product_info['name']} - {product_info['price']}₽"
        callback_data = f"add_{subject_name}_{product_id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='menu_teachers')])
    keyboard.append([InlineKeyboardButton("🛒 Корзина", callback_data='view_cart')])
    return InlineKeyboardMarkup(keyboard)

def get_cart_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data='checkout')],
        [InlineKeyboardButton("🗑️ Очистить корзину", callback_data='clear_cart')],
        [InlineKeyboardButton("⬅️ Продолжить покупки", callback_data='back_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_carts[user_id] = []
    
    await update.message.reply_text(
        "🎓 *Добро пожаловать в магазин учителей!*\n\n"
        "Выберите раздел:",
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = update.effective_user
    data = query.data
    
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    # ═══════════════════════════════════════════════════
    # ГЛАВНОЕ МЕНЮ
    # ═══════════════════════════════════════════════════
    if data == 'menu_teachers':
        await query.edit_message_text(
            "📚 *Выберите предмет:*\n\n"
            "Покажу учителя и его товары:",
            reply_markup=get_subjects_keyboard(),
            parse_mode='Markdown'
        )
    
    elif data == 'menu_products':
        # ═══════════════════════════════════════════════
        # ПРОСТО ТЕКСТ СПИСКА ТОВАРОВ (НЕКЛИКАБЕЛЬНО)
        # ═══════════════════════════════════════════════
        products_text = "📦 *Виды товаров:*\n\n"
        # Берём цены из первого предмета (они везде одинаковые)
        first_subject = list(SUBJECTS.values())[0]
        for product_info in first_subject['products'].values():
            products_text += f"• {product_info['name']} — {product_info['price']}₽\n"
        
        products_text += "\n_Чтобы купить, выберите раздел «Учителя»_"
        
        # Кнопка только для возврата назад
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_main')]]
        
        await query.edit_message_text(
            products_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == 'ideas':
        await query.edit_message_text(
            "💡 *Ваши идеи*\n\n"
            "[Здесь](https://disk.yandex.ru/d/6S4bjhT8TRnnuw) вы можете оставить ваши идеи и предлрдерия по улучшению нашего магазина!\n"
            "Мы обязательно рассмотрим их.",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
    
    # ═══════════════════════════════════════════════════
    # ВЫБОР ПРЕДМЕТА → ПОКАЗЫВАЕМ ТОВАРЫ УЧИТЕЛЯ
    # ═══════════════════════════════════════════════════
    elif data.startswith('subject_'):
        subject_name = data.replace('subject_', '')
        subject = SUBJECTS[subject_name]
        teacher = subject['teacher']
        
        await query.edit_message_text(
            f"👨‍🏫 *{teacher}*\n"
            f"📚 Предмет: {subject_name}\n\n"
            f"Выберите товар:",
            reply_markup=get_subject_products_keyboard(subject_name),
            parse_mode='Markdown'
        )
    
    # ═══════════════════════════════════════════════════
    # ДОБАВЛЕНИЕ В КОРЗИНУ
    # ═══════════════════════════════════════════════════
    elif data.startswith('add_'):
        parts = data.split('_')
        subject_name = parts[1]
        product_id = parts[2]
        
        subject = SUBJECTS[subject_name]
        teacher = subject['teacher']
        product = subject['products'][product_id]
        
        cart_item = {
            "teacher": teacher,
            "subject": subject_name,
            "name": product['name'],
            "price": product['price']
        }
        user_carts[user_id].append(cart_item)
        
        await query.answer(f"✅ Добавлено: {product['name']}!")
        await query.edit_message_text(
            f"✅ *Добавлено в корзину:*\n"
            f"📦 {product['name']}\n"
            f"👨‍🏫 {teacher}\n"
            f"📚 {subject_name}\n"
            f"💰 {product['price']}₽\n\n"
            f"🛒 В корзине: {len(user_carts[user_id])} товар(ов)",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
    
    # ═══════════════════════════════════════════════════
    # КОРЗИНА
    # ═══════════════════════════════════════════════════
    elif data == 'view_cart':
        cart = user_carts[user_id]
        if not cart:
            await query.edit_message_text(
                "🛒 *Корзина пуста!*",
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        total = sum(item['price'] for item in cart)
        cart_text = "🛒 *Ваша корзина:*\n\n"
        
        for i, item in enumerate(cart, 1):
            cart_text += f"{i}. {item['name']} ({item['teacher']}) - {item['price']}₽\n"
        
        cart_text += f"\n💰 *Итого: {total}₽*"
        
        await query.edit_message_text(
            cart_text,
            reply_markup=get_cart_keyboard(),
            parse_mode='Markdown'
        )
    
    elif data == 'clear_cart':
        user_carts[user_id] = []
        await query.answer("🗑️ Корзина очищена!")
        await query.edit_message_text(
            "🛒 *Корзина очищена!*",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
    
    # ═══════════════════════════════════════════════════
    # ОФОРМЛЕНИЕ ЗАКАЗА
    # ═══════════════════════════════════════════════════
    elif data == 'checkout':
        cart = user_carts[user_id]
        if not cart:
            await query.answer("❌ Корзина пуста!")
            return
        
        total = sum(item['price'] for item in cart)
        
        # Отправляем заказ админу
        order_text = "📦 *НОВЫЙ ЗАКАЗ!*\n\n"
        order_text += f"👤 Покупатель: @{user.username or 'нет username'}\n"
        order_text += f"🆔 ID: `{user_id}`\n\n"
        
        for i, item in enumerate(cart, 1):
            order_text += f"{i}. {item['name']}\n"
            order_text += f" Учитель: {item['teacher']}\n"
            order_text += f" Цена: {item['price']}₽\n\n"
        
        order_text += f"💰 *ИТОГО: {total}₽*"
        
        try:
            await context.bot.send_message(ADMIN_ID, order_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Ошибка отправки заказа: {e}")
        
        # Подтверждаем пользователю
        await query.edit_message_text(
            f"✅ *Заказ оформлен!*\n\n"
            f"💰 Сумма: {total}₽\n\n"
            f"{PAYMENT_INFO}\n\n"
            f"Спасибо за покупку! 🎓",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
        
        user_carts[user_id] = []
    
    # ═══════════════════════════════════════════════════
    # НАЗАД
    # ═══════════════════════════════════════════════════
    elif data == 'back_main':
        await query.edit_message_text(
            "🎓 *Главное меню*",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()

