import time

from selenium import webdriver

driver = webdriver.PhantomJS()
driver.set_window_size(1024, 768)

driver.get('https://www.supremenewyork.com/shop/jackets/f9d7nzc4j/ffh6c2zoj')

driver.find_element_by_xpath('//*[@id="add-remove-buttons"]/input').click()

time.sleep(0.2)

driver.find_element_by_xpath('//*[@id="cart"]/a[2]').click()

driver.save_screenshot('test')
