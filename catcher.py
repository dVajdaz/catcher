from __future__ import annotations

import datetime
import json
import random
import re
import time

import requests

courses: list[str]
cookies_string: str

with open('config.json', 'r') as f:
    config = json.load(f)
    courses = config['courses']
    cookies_string = config['cookie_string']

headers = {
    'Host': 'students.technion.ac.il',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Content-Type': 'application/json',
    'Origin': 'https://students.technion.ac.il',
}

cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies_string.split('; ')}
data = '[{"index":0,"methodname":"local_tregister_process_cart_items","args":{}}]'


def is_available(course_number: str) -> bool:
    result = requests.get(f'https://students.technion.ac.il/local/technionsearch/course/{course_number}/202301',
                          cookies=cookies, headers=headers)
    if '<div class="text-success" role="alert">' in result.text:
        return True
    elif '<div class="text-muted" role="alert">' in result.text:
        return False
    print('Something went wrong!')


def is_any_available(course_numbers: list[str]) -> bool:
    for course_number in course_numbers:
        if is_available(course_number):
            return True
    return False


def fetch_key() -> str:
    result = requests.get('https://students.technion.ac.il/local/tregister/cart', cookies=cookies, headers=headers)
    return re.findall('"sesskey":"([^"]*)"', str(result.content))[0]


def register(sesskey: str) -> None:
    result = requests.post(
        f'https://students.technion.ac.il/lib/ajax/service.php?sesskey={sesskey}&info=local_tregister_process_cart_items',
        cookies=cookies, headers=headers, data=data)
    print(f'[{datetime.datetime.now()}] {result.content}')


key: str
last_updated: str


def update_key():
    global key, last_updated
    key = fetch_key()
    last_updated = time.time()
    print('!', end='')


update_key()
while True:
    try:
        if is_any_available(courses):
            print('\nTRY!')
            register(key)
            update_key()
            register(key)
        else:
            print('.', end='')
        if time.time() - last_updated > 60 * 5:
            update_key()
        time.sleep(2 * random.random())
    except Exception as e:
        print(e)
        print("Oh no, an error!")
