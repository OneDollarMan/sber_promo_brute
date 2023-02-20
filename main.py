import logging
import random
import threading

from threading import Thread, Lock
from time import sleep

from selenium import webdriver
from selenium.common import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

PROMO_NOT_FOUND = 'Промокод не существует'
PROMO_USED = 'Данный промокод истек'
BAN = 'Сервер временно недоступен'

DICTIONARY = 'abcdefghijklmnopqrstuvwxyz1234567890'

MODE = 'RAND'  # 'RAND','BRUT'

THREAD_COUNT = 1  # not working

lock = Lock()


def get_next_promo():
    if MODE == 'BRUT':
        with open('current.txt', 'r') as f:  # read current promo from file
            promo = list(f.read())
        i = len(promo)

        while True:  # loop with next promo generation
            if i < 6: break
            if DICTIONARY.find(promo[i - 1]) < len(DICTIONARY) - 1:
                promo[i - 1] = DICTIONARY[DICTIONARY.find(promo[i - 1]) + 1]
                break
            else:
                promo[i - 1] = DICTIONARY[0]
                i -= 1

        promo = ''.join(promo)  # save next promo to file and return it
        with open('current.txt', 'w') as f:
            f.write(promo)
        return promo
    elif MODE == 'RAND':
        promo = 'opscc' + ''.join(random.choice(DICTIONARY) for i in range(6))
        return promo
    else:
        logging.critical('MODE value should be {BRUT} or {RAND}')
        exit()


def save_good_promo(promo):
    logging.critical('Thread[' + str(threading.get_ident()) + '] GOOD - ' + promo)
    with open('result/good.txt', 'a') as f:
        f.write(promo + '\n')


def save_bad_promo(promo):
    logging.info('Thread[' + str(threading.get_ident()) + '] BAD - ' + promo)
    with open('result/bad.txt', 'a') as f:
        f.write(promo + '\n')


def save_used_promo(promo):
    logging.warning('Thread[' + str(threading.get_ident()) + '] USED - ' + promo)
    with open('result/used.txt', 'a') as f:
        f.write(promo + '\n')


def thread_func(token):
    print(f'thread with token "{token}" started')
    options = Options()
    options.add_argument("window-size=1400,600")
    options.add_argument(f'user-agent={UserAgent().random}')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get('https://sbermarket.ru/')
    login_cookie = {'name': 'remember_user_token', 'value': token}
    driver.add_cookie(login_cookie)
    sleep(10)
    checkout_button = driver.find_element(By.XPATH, "//button[@class='Button_root__WicTg Button_default__fTaqt Button_primary__ifUNs Button_lgSize__ePPCL Button_block__48waA cart-checkout-link']")
    checkout_button.submit()

    while True:
        lock.acquire()
        promo = get_next_promo()
        lock.release()

        try:
            promo_input = driver.find_element(By.XPATH, "//input[@data-qa='checkout_page_sidebar_promocode_input']")
        except NoSuchElementException:
            continue
        promo_input.send_keys(promo)
        sleep(1)

        promo_btn = driver.find_element(By.CSS_SELECTOR, "button.Button_smSize__FV_id:nth-child(2)")
        sleep(1)
        try:
            promo_btn.click()
        except ElementClickInterceptedException:
            continue

        try:
            promo_description = driver.find_element(By.CSS_SELECTOR, ".FormGroup_description__tYxjD").text
        except Exception:
            continue
        lock.acquire()
        if PROMO_NOT_FOUND == promo_description:
            save_bad_promo(promo)
        elif PROMO_USED == promo_description:
            save_used_promo(promo)
        elif BAN == promo_description:
            logging.critical("----------------------------YOU ARE BANNED--------------------------------")
            sleep(3600)
        else:
            # Cancel and save actual working promo
            save_good_promo(promo)
            promo_btn.click()
        lock.release()
        promo_input.clear()
        sleep(9)


def main():
    tokens = open('user_token_list.txt', 'r')
    threads = []
    for line in tokens.readlines():
        threads.append(Thread(target=thread_func, args=(line.strip(),)))
    for thread in threads:
        thread.start()
        sleep(1)


if __name__ == '__main__':
    main()
