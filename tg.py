import json
import requests
import time
import urllib

TOKEN = "380540735:AAFhwCOUrjnLF_9F7yhPP1iFme0Lh-ygI8k"
URL = f"https://api.telegram.org/bot{TOKEN}/"


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf-8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    json_content = json.loads(content)
    return json_content


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset}"
    json_content = get_json_from_url(url)
    return json_content


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
        except Exception as e:
            print(e)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    message = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return message, chat_id


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + f"sendMessage?text={text}&chat_id={chat_id}"
    get_url(url)


def main():
    print("Starting tg-bot")
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
