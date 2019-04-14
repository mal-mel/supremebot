import time

from selenium import webdriver, common


def order(data):

    options = webdriver.ChromeOptions()

    if data['img'] == 'off':
        options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
    else:
        options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 1})

    if 'proxy' in data.keys():
        options.add_argument('--proxy-server=http://' + data['proxy'])

    options.add_argument('--user-data-dir=./chrome_profile')

    options.add_argument('load-extension=./recaptcha')
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=options)

    driver.get(data['url_1'])

    if 'size' in data.keys():
        try:
            driver.find_element_by_xpath('//*[@id="size"]').send_keys(data['size'])
        except common.exceptions.NoSuchElementException or common.exceptions.WebDriverException:
            pass

    driver.find_element_by_xpath('//*[@id="add-remove-buttons"]/input').click()

    time.sleep(0.5)

    driver.find_element_by_xpath('//*[@id="cart"]/a[2]').click()

    driver.find_element_by_xpath('//*[@id="order_billing_name"]').send_keys(data['name'])

    driver.find_element_by_xpath('//*[@id="order_email"]').send_keys(data['email'])

    driver.find_element_by_xpath('//*[@id="order_tel"]').send_keys(data['tel'])

    driver.find_element_by_xpath('//*[@id="bo"]').send_keys(data['address'])

    driver.find_element_by_xpath('//*[@id="order_billing_city"]').send_keys(data['city'])

    driver.find_element_by_xpath('//*[@id="order_billing_zip"]').send_keys(data['post_code'])

    driver.find_element_by_xpath('//*[@id="order_billing_country"]').send_keys(data['country'])

    driver.find_element_by_xpath('//*[@id="credit_card_type"]').send_keys(data['card'])

    card_number = driver.find_element_by_xpath('//*[@id="cnb"]')
    card_number.send_keys(data['card_number'])
    card_number.clear()
    card_number.send_keys(data['card_number'])

    driver.find_element_by_xpath('//*[@id="credit_card_month"]').send_keys(data['valid_month'])

    driver.find_element_by_xpath('//*[@id="credit_card_year"]').send_keys(data['valid_year'])

    driver.find_element_by_xpath('//*[@id="vval"]').send_keys(data['cvv'])

    driver.find_element_by_xpath('//*[@id="cart-cc"]/fieldset/p/label/div/ins').click()
