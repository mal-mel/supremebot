import datetime
import re
import sys
import time

import PyQt5
import bs4
import grab
import requests
from jinja2 import Environment, FileSystemLoader

from bot import order
from db.database import DB, CONNECTION
from request_threads import multi_request
from windows import *

DATA = {}

_ENV = Environment(loader=FileSystemLoader(''))

TEMPLATE_ITEMS = _ENV.get_template('webview.html')

TEMPLATE_TIME = _ENV.get_template('time.html')


class SupremeBot(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):
    '''Main class for bot operation'''

    def __init__(self):
        PyQt5.QtWidgets.QWidget.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Run a separate thread for timer operation:
        self.thread_timer = TimerThread()
        self.thread_timer.html.connect(self.set_html_timer)
        self.thread_timer.start()

        # Items list update:
        self.start_update()

        self.ui.pushButton.clicked.connect(self.start_button)

        self.ui.pushButton_2.clicked.connect(self.ship_info)

        self.ui.pushButton_3.clicked.connect(self.back_page)

        self.ui.pushButton_4.clicked.connect(self.ui.lineEdit.clear)

        self.ui.pushButton_5.clicked.connect(self.update_main_view)

        self.ui.radioButton.setChecked(True)

        # Filling fields in the settings from the database:
        if DB.execute('select * from USER_DATA where id=2').fetchall():
            db_data = DB.execute('select * from USER_DATA where id=2').fetchall()

            self.ui.lineEdit_2.setText(db_data[0][1])
            self.ui.lineEdit_3.setText(db_data[0][2])
            self.ui.lineEdit_4.setText(db_data[0][3])
            self.ui.lineEdit_5.setText(db_data[0][4])
            self.ui.lineEdit_6.setText(db_data[0][5])
            self.ui.lineEdit_7.setText(str(db_data[0][6]))

            self.ui.comboBox_4.setCurrentText(db_data[0][7])
            self.ui.comboBox_3.setCurrentText(db_data[0][8])

            self.ui.lineEdit_8.setText(db_data[0][9])

            self.ui.comboBox.setCurrentText('0' + str(db_data[0][10]) if len(str(db_data)) < 2 else '')
            self.ui.comboBox_2.setCurrentText(str(db_data[0][11]))

            self.ui.lineEdit_9.setText(str(db_data[0][12]))

    def update_main_view(self):
        self.start_update()

    def back_page(self):
        if self.ui.webView.history().canGoBack():
            self.start_update()

    def start_button(self):
        link = self.ui.lineEdit.text()

        if re.search('https://www.supremenewyork.com/shop/(.+?)', link):

            # Getting all the values from the database to fill in the delivery information with the bot:
            db_data = DB.execute('select * from USER_DATA where id=2').fetchall()

            DATA['url_1'] = link
            DATA['name'] = db_data[0][1]
            DATA['email'] = db_data[0][2]
            DATA['tel'] = db_data[0][3]
            DATA['address'] = db_data[0][4]
            DATA['city'] = db_data[0][5]
            DATA['post_code'] = db_data[0][6]
            DATA['country'] = db_data[0][7]
            DATA['card'] = db_data[0][8]
            DATA['card_number'] = db_data[0][9]
            DATA['valid_month'] = db_data[0][10]
            DATA['valid_year'] = db_data[0][11]
            DATA['cvv'] = db_data[0][12]

            if self.ui.radioButton_8.isChecked():
                DATA['size'] = 'Medium'

            elif self.ui.radioButton_9.isChecked():
                DATA['size'] = 'Large'

            elif self.ui.radioButton_10.isChecked():
                DATA['size'] = 'XLarge'

            if self.ui.radioButton.isChecked():
                DATA['img'] = 'on'

            elif self.ui.radioButton_2.isChecked():
                DATA['img'] = 'off'

            # Check proxy valid:
            if self.ui.lineEdit_12.text():
                checker = grab.Grab()
                checker.setup(proxy=self.ui.lineEdit_12.text().strip(), proxy_type='http', connect_timeout=5, timeout=5)

                try:
                    checker.go('https://www.supremenewyork.com/')

                    DATA['proxy'] = self.ui.lineEdit_12.text().strip()

                    self.bot_thread = OrderThread()
                    self.bot_thread.start()
                except grab.GrabError:
                    self.proxy_error = ProxyError()
                    self.proxy_error.show()
            else:
                self.bot_thread = OrderThread()
                self.bot_thread.start()

    def ship_info(self):
        all_lines = self.ui.lineEdit_2.text() and self.ui.lineEdit_3.text() and self.ui.lineEdit_4.text() and \
                    self.ui.lineEdit_5.text() and self.ui.lineEdit_6.text() and self.ui.lineEdit_7.text() and \
                    self.ui.lineEdit_8.text() and self.ui.lineEdit_9.text()

        # Saving information about the delivery to the database is preliminarily checked for filling in all the fields:
        if not DB.execute('select * from USER_DATA where id=2').fetchall():
            if all_lines:
                DB.execute(f'''
                            INSERT INTO USER_DATA VALUES ("{self.ui.lineEdit_2.text()}", "{self.ui.lineEdit_3.text()}",
                            "{self.ui.lineEdit_4.text()}", "{self.ui.lineEdit_5.text()}", "{self.ui.lineEdit_6.text()}",
                            {self.ui.lineEdit_7.text()}, "{self.ui.comboBox_4.currentText()}",
                            "{self.ui.comboBox_3.currentText()}", "{self.ui.lineEdit_8.text()}", 
                            {self.ui.comboBox.currentText()}, {self.ui.comboBox_2.currentText()},
                            {self.ui.lineEdit_9.text()})
                            ''')

                CONNECTION.commit()

                self.success = SuccessWindow()
                self.success.show()
            else:
                self.error = ErrorWindow()
                self.error.show()
        else:
            if not all_lines:
                self.error = ErrorWindow()
                self.error.show()
            else:
                DB.execute(f'''
                            UPDATE USER_DATA 
                            SET name="{self.ui.lineEdit_2.text()}",
                            email="{self.ui.lineEdit_3.text()}",
                            tel="{self.ui.lineEdit_4.text()}",
                            address="{self.ui.lineEdit_5.text()}",
                            city="{self.ui.lineEdit_6.text()}",
                            post_code={self.ui.lineEdit_7.text()},
                            country="{self.ui.comboBox_4.currentText()}",
                            card="{self.ui.comboBox_3.currentText()}",
                            card_number="{self.ui.lineEdit_8.text()}", 
                            valid_month={self.ui.comboBox.currentText()},
                            valid_year={self.ui.comboBox_2.currentText()},
                            cvv={self.ui.lineEdit_9.text()}
                            WHERE id=2
                            ''')

                CONNECTION.commit()

                self.success = SuccessWindow()
                self.success.show()

    def set_html_timer(self, html):
        self.ui.webView_2.setHtml(html)

    def start_update(self):
        # Run a separate thread to update the list of items:
        self.thread_parse = ParseThread()
        self.thread_parse.html_view.connect(self.ui.webView.setHtml)
        self.thread_parse.button.connect(self.ui.pushButton_5.setEnabled)
        self.thread_parse.progress_bar.connect(self.ui.progressBar.setValue)
        self.thread_parse.start()


class SuccessWindow(PyQt5.QtWidgets.QMainWindow, Ui_SuccessWindow):
    def __init__(self):
        PyQt5.QtWidgets.QWidget.__init__(self)
        self.ui = Ui_SuccessWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.agree)

    def agree(self):
        self.close()


class ErrorWindow(PyQt5.QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self):
        PyQt5.QtWidgets.QWidget.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.agree)

    def agree(self):
        self.close()


class ProxyError(PyQt5.QtWidgets.QMainWindow, Ui_ProxyError):
    def __init__(self):
        PyQt5.QtWidgets.QWidget.__init__(self)
        self.ui = Ui_ProxyError()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.close)


class TimerThread(PyQt5.QtCore.QThread):
    '''Separate class for timer operation'''

    html = PyQt5.QtCore.pyqtSignal(str)
    drop_day = datetime.datetime(2019, 4, 4, 13, 0, 0, 0)

    def run(self):
        while True:
            today = datetime.datetime.today()

            if today.date() >= self.drop_day.date():
                self.drop_day = self.drop_day + datetime.timedelta(days=7)
            remain = self.drop_day - today

            if remain.days >= 0:
                result = {
                    'days': remain.days,
                    'hours': str(remain).split(',')[1].split(':')[0].strip() if len(str(remain).split(',')) == 2
                    else str(remain).split(':')[0],
                    'minutes': str(remain).split(',')[1].split(':')[1],
                    'seconds': str(remain).split(',')[1].split(':')[2].split('.')[0]
                }
            else:
                result = {
                    'days': 0,
                    'hours': str(remain).split(':')[0].strip() if len(str(remain).split(',')) == 2
                    else str(remain).split(':')[0],
                    'minutes': str(remain).split(':')[1],
                    'seconds': str(remain).split(':')[2].split('.')[0]
                }

            self.html.emit(TEMPLATE_TIME.render(time=result))
            time.sleep(1)


class ParseThread(PyQt5.QtCore.QThread):
    '''A separate class for the work function of updating the list of items'''

    html_view = PyQt5.QtCore.pyqtSignal(str)
    button = PyQt5.QtCore.pyqtSignal(bool)
    progress_bar = PyQt5.QtCore.pyqtSignal(int)

    def run(self):
        # Parsing a list of items with supremenewyork.com:

        self.button.emit(False)

        url = 'https://www.supremenewyork.com/shop'

        content = requests.get(url).text.replace('\n', '')
        soup = bs4.BeautifulSoup(content, 'html.parser')
        links = soup.find(id='shop-scroller').find_all('a')

        urls = []
        completed = 0

        for link in links:
            true_link = re.findall('href="/shop/(.+?)"', str(link))

            urls.append(f'https://www.supremenewyork.com/shop/{true_link[0]}')

            completed += 1
            self.progress_bar.emit(completed)

        # Multi-threaded queries:
        responses = multi_request(urls)

        i = 0
        jackets, pants, hats, bags, accessories, shirts, tops_sweaters, sweatshirts = [], [], [], [], [], [], [], []

        for response in responses:
            link = re.findall('href="/shop/(.+?)"', str(links[i]))

            '''If the length of the array of the found lines is add, then the basket is in the html code more than two,
             then the product is available for purchase, otherwise I simply do not add it to the list of items.'''
            if len(re.findall('add to basket', response.text)) == 2:
                if 'jackets' in link[0]:
                    jackets.append(link[0])
                elif 'pants' in link[0]:
                    pants.append(link[0])
                elif 'hats' in link[0]:
                    hats.append(link[0])
                elif 'bags' in link[0]:
                    bags.append(link[0])
                elif 'accessories' in link[0]:
                    accessories.append(link[0])
                elif 'shirts' in link[0] and 'sweatshirts' not in link[0]:
                    shirts.append(link[0])
                elif 'tops-sweaters' in link[0]:
                    tops_sweaters.append(link[0])
                elif 'sweatshirts' in link[0]:
                    sweatshirts.append(link[0])

            i += 1
            completed += 1
            self.progress_bar.emit(completed)

        html = TEMPLATE_ITEMS.render(jackets=jackets, pants=pants, hats=hats, bags=bags, accessories=accessories,
                                     shirts=shirts, tops_sweaters=tops_sweaters, sweatshirts=sweatshirts)

        self.html_view.emit(html)

        self.button.emit(True)


class OrderThread(PyQt5.QtCore.QThread):

    def run(self):
        order(DATA)


def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    window = SupremeBot()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
