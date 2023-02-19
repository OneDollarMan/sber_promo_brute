from time import sleep
from selenium import webdriver
from threading import Thread, Lock
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get('https://sbermarket.ru/')
    login_cookie = {'name': 'remember_user_token', 'value': token}
    driver.add_cookie(login_cookie)

    # next is loopable
    sleep(10)
    checkout_button = driver.find_element(By.XPATH, "//button[@class='Button_root__WicTg Button_default__fTaqt Button_primary__ifUNs Button_lgSize__ePPCL Button_block__48waA cart-checkout-link']")
    checkout_button.submit()

    promo_input = driver.find_element(By.XPATH, "//input[@class='Input_root__xROBM FormGroup_input__H6r_Q PromoCode_input__b7H0S']")
    promo_input.send_keys(get_next_promo())
    WebDriverWait(driver, 1000000).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='Button_root__WicTg Button_default__fTaqt Button_secondary__f4KOQ Button_smSize__FV_id CheckoutButton_root__holGG PromoCode_button__ybZoC']"))).click()


def main():
    tokens = open('remember_user_token.txt', 'r')
    threads = []
    for line in tokens.readlines():
        threads.append(Thread(target=thread_func, args=(line,)))
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    main()
