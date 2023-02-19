from time import sleep

from selenium import webdriver
from threading import Thread, Lock

from selenium.webdriver.common.by import By

abc = 'abcdefghijklmnopqrstuvwxyz1234567890'
lock = Lock()


def get_next_promo():
    with open('current.txt', 'r') as f:  #read current promo from file
        promo = list(f.read())
    i = len(promo)

    while True:  #loop with next promo generation
        if i < 6: break
        if abc.find(promo[i-1]) < len(abc) - 1:
            promo[i-1] = abc[abc.find(promo[i-1])+1]
            break
        else:
            promo[i - 1] = abc[0]
            i -= 1

    promo = ''.join(promo)  #save next promo to file and return it

    with open('current.txt', 'w') as f:
        f.write(promo)
    return promo


def save_working_promo(promo):
    with open('res.txt', 'a') as f:
        f.write(promo + '\n')


def thread_func(token):
    print(f'thread with token "{token}" started')
    driver = webdriver.Firefox()
    driver.get('https://sbermarket.ru/')
    login_cookie = {'name': 'remember_user_token', 'value': token}
    driver.add_cookie(login_cookie)
    while True:
        driver.get("https://sbermarket.ru/")
        driver.implicitly_wait(10)
        checkout_button = driver.find_element(By.CLASS_NAME, 'Button_root__WicTg Button_default__fTaqt Button_primary__ifUNs Button_lgSize__ePPCL Button_block__48waA cart-checkout-link')
        checkout_button.click()
        sleep(10)


def main():
    tokens = open('remember_user_token.txt', 'r')
    threads = []
    for line in tokens.readlines():
        threads.append(Thread(target=thread_func, args=(line,)))
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    main()