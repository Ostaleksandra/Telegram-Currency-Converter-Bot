import requests

class ConversionException(Exception):
    pass

class CurrencyConverter:

    def __init__(self, currency_keys: dict):
        self.currency_keys = currency_keys

    def parse_message(self, text: str):
        parts = text.lower().split()

        if len(parts) != 3:
            raise ConversionException(
                "Формат ввода:\n<валюта_из> <валюта_в> <количество>"
            )

        return parts

    def validate_amount(self, amount: str):
        try:
            value = float(amount)
            if value <= 0:
                raise ConversionException("Количество должно быть больше нуля")
            return value
        except ValueError:
            raise ConversionException("Количество должно быть числом")

    def build_url(self, quote_code: str, base_code: str):
        return (
            "https://min-api.cryptocompare.com/data/price"
            f"?fsym={quote_code}&tsyms={base_code}"
        )

    def convert(self, quote: str, base: str, amount: float):

        if quote not in self.currency_keys:
            raise ConversionException(f"Валюта '{quote}' не поддерживается")

        if base not in self.currency_keys:
            raise ConversionException(f"Валюта '{base}' не поддерживается")

        url = self.build_url(
            self.currency_keys[quote],
            self.currency_keys[base]
        )

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            raise ConversionException(
                "Ошибка подключения к сервису курсов"
            )

        try:
            data = response.json()
        except ValueError:
            raise ConversionException("Некорректный ответ от сервиса")

        if self.currency_keys[base] not in data:
            raise ConversionException("Не удалось получить курс валют")

        rate = data[self.currency_keys[base]]
        return rate * amount, rate