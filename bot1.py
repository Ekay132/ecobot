import telebot
from predict_image import get_class

bot = telebot.TeleBot("")

GUIDE = {
    "batteries": "Батарейки: только в спецпункты (ВкусВилл, М.Видео). Нельзя в обычный мусор!",
    "biological": "Биоотходы: компостируйте или в спецконтейнеры для органики.",
    "cardboard": "Картон: очистите от скотча, сдавайте в синие баки для макулатуры.",
    "clothes": "Одежда: в хорошем состоянии — на благотворительность, остальное — в спецконтейнеры.",
    "glass": "Стекло: мойте, снимайте крышки, в зелёные баки.",
    "metal": "Металл: очистите, алюминиевые банки сплющите, в синие баки.",
    "paper": "Бумага: без скрепок и пластика, в синие баки (сухая!).",
    "plastic": "Пластик: мойте, сплющите бутылки, ищите маркировку 1–7.",
    "trash": "Смешанные отходы: в серый контейнер. Опасные отходы — в спецпункты."
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет, отправь фото мусора — скажу, как утилизировать.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if not message.photo:
        bot.send_message(message.chat.id, "Загрузите картинку!")
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    file_name = file_info.file_path.split('/')[-1]
    
    with open(file_name, 'wb') as f:
        f.write(bot.download_file(file_info.file_path))

    # Получаем результат от модели
    result = get_class("./keras_model.h5", "labels.txt", file_name)
    
    # Нормализуем результат:
    # 1. Если это список — берём первый элемент
    if isinstance(result, (list, tuple)):
        result = result[0]
    # 2. Преобразуем в строку, убираем пробелы и переводим в нижний регистр
    result_str = str(result).strip().lower()
    
    # Ищем инструкцию
    response = GUIDE.get(result_str, "Не удалось определить тип мусора. Сделайте чёткое фото.")
    
    bot.send_message(message.chat.id, response)

bot.polling()

