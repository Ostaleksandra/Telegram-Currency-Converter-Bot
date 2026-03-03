import telebot
from config import TOKEN, CURRENCY_KEYS
from utils import CurrencyConverter, ConversionException


class CurrencyBot:

    def __init__(self, token: str, currency_keys: dict):
        self.bot = telebot.TeleBot(token)
        self.converter = CurrencyConverter(currency_keys)
        self._register_handlers()

    def _register_handlers(self):

        @self.bot.message_handler(commands=['start', 'help'])
        def help_handler(message):
            text = (
                "Введите команду в формате:\n"
                "<валюта_из> <валюта_в> <количество>\n\n"
                "Пример:\n"
                "доллар евро 100\n\n"
                "Список валют: /values"
            )
            self.bot.reply_to(message, text)

        @self.bot.message_handler(commands=['values'])
        def values_handler(message):
            text = "Доступные валюты:\n"
            text += "\n".join(sorted(self.converter.currency_keys.keys()))
            self.bot.reply_to(message, text)

        @self.bot.message_handler(content_types=['text'])
        def convert_handler(message):
            try:
                quote, base, amount = self.converter.parse_message(message.text)
                amount = self.converter.validate_amount(amount)

                total, rate = self.converter.convert(quote, base, amount)

                self.bot.send_message(
                    message.chat.id,
                    f"{amount} {quote} = {round(total, 2)} {base}\n"
                    f"Курс: 1 {quote} = {rate} {base}"
                )

            except ConversionException as e:
                self.bot.reply_to(message, str(e))

            except Exception as e:
                self.bot.reply_to(message, "Произошла непредвиденная ошибка.")


    def run(self):
        self.bot.polling(none_stop=True)

if __name__ == "__main__":
    bot = CurrencyBot(TOKEN, CURRENCY_KEYS)
    bot.run()
