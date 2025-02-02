import os
import sqlite3
import base64
import json
import re
from Crypto.Cipher import AES
import win32crypt
from Crypto.Util.Padding import unpad
import subprocess

def get_encryption_key():
    """Получение ключа шифрования из Local State"""
    local_state_path = os.path.join(
        os.environ['LOCALAPPDATA'],
        'Yandex\\YandexBrowser\\User Data\\Local State'
    )
    
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        return win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
    except Exception as e:
        print(f"Ошибка получения ключа: {str(e)}")
        return None

def decrypt_value(encrypted_value, key):
    """Расшифровка значения с обработкой бинарных префиксов"""
    try:
        # Режим AES-GCM
        if encrypted_value.startswith(b'v10'):
            nonce = encrypted_value[3:15]
            ciphertext = encrypted_value[15:-16]
            tag = encrypted_value[-16:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        else:
            # Режим AES-CBC
            iv = encrypted_value[3:19]
            ciphertext = encrypted_value[19:]
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypted = unpad(cipher.decrypt(ciphertext), 16)

        # Поиск текстовых данных в бинарной строке
        str_match = re.search(b'[\x20-\x7E]{5,}', decrypted)
        if str_match:
            return str_match.group().decode('utf-8', errors='replace')
            
        return decrypted.hex()  # Возвращаем hex если текст не найден
        
    except Exception as e:
        print(f"Ошибка расшифровки: {str(e)}")
        return None

def clean_cookie_value(value):
    """Очистка значений от бинарных артефактов"""
    if isinstance(value, str) and '' in value:
        return re.sub(r'[^\x00-\x7F]+', '', value)
    return value

def main():
    # Принудительное завершение процесса браузера
    try:
        subprocess.run(['taskkill', '/IM', 'browser.exe', '/F'], capture_output=True)
    except Exception as e:
        print(f"Ошибка при завершении браузера: {str(e)}")

    key = get_encryption_key()
    if not key:
        return

    cookie_path = os.path.join(
        os.environ['LOCALAPPDATA'],
        'Yandex\\YandexBrowser\\User Data\\Default\\Network\\Cookies'
    )
    
    try:
        conn = sqlite3.connect(cookie_path)
        conn.text_factory = bytes
        cursor = conn.cursor()
        cursor.execute('SELECT host_key, name, encrypted_value FROM cookies')
        
        decrypted_cookies = []
        for host, name, encrypted_value in cursor.fetchall():
            decrypted = decrypt_value(encrypted_value, key)
            if decrypted:
                decrypted_cookies.append({
                    'domain': host.decode('utf-8', errors='replace'),
                    'name': name.decode('utf-8', errors='replace'),
                    'value': clean_cookie_value(decrypted)
                })
        
        # Вывод результата в консоль
        print(json.dumps(
            decrypted_cookies,
            indent=2,
            ensure_ascii=False,
            default=lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
        ))
        
        # Сохранение результата в файл cookie.json
        with open('cookie.json', 'w', encoding='utf-8') as f:
            json.dump(
                decrypted_cookies, 
                f, 
                indent=2, 
                ensure_ascii=False, 
                default=lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
            )
    
    except Exception as e:
        print(f"Ошибка БД: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
