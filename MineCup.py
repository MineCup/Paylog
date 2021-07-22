from vk_api import VkApi
from random import randint
from requests import get, Session
from time import sleep
from os import environ
from bs4 import BeautifulSoup
from re import findall

vk = VkApi(token=str(environ.get("vk_token")))

key = str(environ.get("key"))
captcha = get(
    f"http://rucaptcha.com/in.php?key={key}&method=userrecaptcha&googlekey=6LeriWUUAAAAAJMt8OpbkWrWxVePsE_TRUVEX2sp&pageurl=https://cp.vimeworld.ru/login&json=1").json()
print("Запуск решения капчи.")
sleep(30)
answer = get(f"http://rucaptcha.com/res.php?key={key}&action=get&id={captcha['request']}&json=1").json()
while answer["request"] == "CAPCHA_NOT_READY":
    sleep(5)
    answer = get(f"http://rucaptcha.com/res.php?key={key}&action=get&id={captcha['request']}&json=1").json()
else:
    print("Капча решена.")
data = {
    "username": str(environ.get("username")),
    "password": str(environ.get("password")),
    "g-recaptcha-response": answer["request"],
    "login": "Войти",
    "remember": "true",
    "server": "lobby"
}
session = Session()
session.post(url="https://cp.vimeworld.ru/login", data=data)
account = session.get(url="https://cp.vimeworld.ru/index")
if "MineCup" in str(account.content):
    print("Сессия авторизована.")

    give = session.get(url="https://cp.vimeworld.ru/real?give", data={"give": ""})
    csfr_token = findall("'.{64}'", give.text)[-1][1:-1]

    payload = session.get("https://cp.vimeworld.ru/real?paylog")  # просмотр транзакций
    soup = BeautifulSoup(payload.text, 'lxml')
    vims = 0
    for tag in soup.find_all("b"):
        if "." in tag.text:
            vims = tag.text[:-3]
            break
    send_vimers = {"csrf_token": csfr_token,
                   "usrnm": "eLs",
                   "amount": int(vims),
                   "process": ""}
    send_vim = session.post("https://cp.vimeworld.ru/real?give", data=send_vimers)  # отправка вимеров
    vk.method('messages.send', {'chat_id': 5, 'message': f"🟢 Бот запущен. При запуске бот перевел {vims} вимеров eLs",
                                'random_id': randint(0, 2147483647)})
    print(f"Отправлено вимеров: {vims}")


def write_msg(message):
    if "игрока" in message[4]:
        vk.method('messages.send', {'chat_id': 5, 'message': f"➕ {message[3][1:]} {message[4][17:]} ({message[2]})",
                                    'random_id': randint(0, 2147483647)})
    elif "игроку" in message[4]:
        vk.method('messages.send', {'chat_id': 5, 'message': f"➖ {message[3][1:]} {message[4][14:]} ({message[2]})",
                                    'random_id': randint(0, 2147483647)})


payload = session.get("https://cp.vimeworld.ru/real?paylog")
soup = BeautifulSoup(payload.text, 'lxml').find_all("tr")
latest = soup[1].text.split("\n")
while True:
    sleep(3)
    payload = session.get("https://cp.vimeworld.ru/real?paylog")
    soup = BeautifulSoup(payload.text, 'lxml').find_all("tr")
    latest_new = soup[1].text.split("\n")
    if latest == latest_new:
        continue
    else:
        print(latest_new)
        latest = latest_new
        write_msg(latest_new)
