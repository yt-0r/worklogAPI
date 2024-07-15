import base64


# Функция для кодирования строки в base64
def encode_to_base64(string):
    return base64.b64encode(string.encode()).decode()


# Функция для декодирования строки из base64
def decode_from_base64(encoded_string):
    return base64.b64decode(encoded_string).decode()
