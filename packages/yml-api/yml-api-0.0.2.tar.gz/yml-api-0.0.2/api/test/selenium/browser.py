# -*- coding: utf-8 -*-
import os
import time
import sys
import datetime
import traceback
from selenium import webdriver
from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException


class Browser(webdriver.Firefox):
    
    def __init__(self, server_url, options=None, verbose=True, slowly=False, maximize=True, headless=True):
        if not options:
            options = Options()
        if maximize:
            options.add_argument("--start-maximized")
        else:
            options.add_argument("--window-size=720x800")
        if headless and '-v' not in sys.argv:
            options.add_argument("--headless")

        super().__init__(options=options)

        self.cursor = None
        self.verbose = verbose
        self.slowly = slowly
        self.server_url = server_url
        self.headless = headless

        if maximize:
            self.maximize_window()
        else:
            self.set_window_position(700, 0)
            self.set_window_size(720, 800)
        self.switch_to.window(self.current_window_handle)

    def find_element(self, by, value):
        try:
            if self.cursor is None:
                self.cursor = super().find_element(By.TAG_NAME, 'html')
            self.cursor.tag_name
        except StaleElementReferenceException:
            self.cursor = super().find_element(By.TAG_NAME, 'html')
        while True:
            # print('CURRENT CURSOR:', self.cursor.tag_name)
            dialogs = super().find_elements(By.TAG_NAME, 'dialog')
            if dialogs:
                return dialogs[0].find_element(by, value)
            else:
                elements = self.cursor.find_elements(by, value)
                if elements:
                    # print('Element "{}" found in "{}"'.format(value, self.cursor.tag_name))
                    return elements[0]
            if self.cursor.tag_name != 'html':
                self.cursor = self.cursor.find_element('xpath', '..')
        # print('Element "{}" NOT found in "{}"'.format(value, self.cursor.tag_name))

    def wait(self, seconds=1):
        time.sleep(seconds)

    def watch(self, e):
        self.save_screenshot('/tmp/test.png')
        if self.headless:
            raise e
        else:
            breakpoint()

    def print(self, message):
        if self.verbose:
            print(message)

    def execute_script(self, script, *args):
        super().execute_script(script, *args)
        if self.slowly:
            self.wait(3)

    def open(self, url):
        if url.startswith('http'):
            self.get(url.replace('http://localhost:8000', self.server_url))
        else:
            self.get("{}{}".format(self.server_url, url))

    def enter(self, name, value, submit=False, count=4):
        if callable(value):
            value = value()
        if type(value) == datetime.date:
            value = value.strftime('%Y-%d-%m')
        self.print('{} "{}" for "{}"'.format('Entering', value, name))
        if value:
            value = str(value)
            if len(value) == 10 and value[2] == '/' and value[5] == '/':
                value = datetime.datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d')
        try:
            widget = self.find_element(By.CSS_SELECTOR, '.form-control[data-label="{}"]'.format(name))
            if widget.tag_name == 'input' and widget.get_property('type') == 'file':
                value = os.path.join(settings.BASE_DIR, value)
            widget.send_keys(value)
        except WebDriverException as e:
            if count:
                self.wait()
                self.enter(name, value, submit, count - 1)
            else:
                self.watch(e)
        if self.slowly:
            self.wait(2)

    def choose(self, name, value, count=4):
        self.print('{} "{}" for "{}"'.format('Choosing', value, name))
        try:
            widget = self.find_element(By.CSS_SELECTOR, '.form-control[data-label="{}"]'.format(name))
            if widget.tag_name.lower() == 'select':
                select = Select(widget)
                select.select_by_visible_text(value)
            else:
                widget.send_keys(value)
                for i in range(0, 6):
                    # print('Trying ({}) click at "{}"...'.format(i, value))
                    self.wait(0.5)
                    try:
                        super().find_element(By.CSS_SELECTOR, '.autocomplete-item[data-label*="{}"]'.format(value)).click()
                        break
                    except WebDriverException:
                        pass
        except WebDriverException as e:
            if count:
                self.wait()
                self.choose(name, value, count - 1)
            else:
                self.watch(e)
        if self.slowly:
            self.wait(2)

    def dont_see_error_message(self, testcase=None):
        elements = self.find_elements(By.CLASS_NAME, 'alert-danger')
        if elements:
            messages = [element.text for element in elements]
            if True:
                input('Type enter to continue...')
            elif testcase:
                exception_message = 'The following messages were found on the page: {}'.format(';'.join(messages))
                raise testcase.failureException(exception_message)

    def see(self, text, flag=True, count=4):
        if flag:
            self.print('See "{}"'.format(text))
            try:
                assert text in self.find_element(By.TAG_NAME, 'body').text
            except AssertionError as e:
                if count:
                    self.wait()
                    self.see(text, flag, count - 1)
                else:
                    self.watch(e)
            if self.slowly:
                self.wait(2)
        else:
            self.print('Can\'t see "{}"'.format(text))
            try:
                assert text not in self.find_element(By.TAG_NAME, 'body').text
            except AssertionError as e:
                if count:
                    self.wait()
                    self.see(text, flag, count - 1)
                else:
                    self.watch(e)
            if self.slowly:
                self.wait(2)

    def see_message(self, text, count=4):
        self.print('See message "{}"'.format(text))
        try:
            pass
        except WebDriverException as e:
            if count:
                self.wait()
                self.see_message(text, count - 1)
            else:
                self.watch(e)
        if self.slowly:
            self.wait(2)

    def see_dialog(self, count=4):
        self.print('Looking at popup window')
        try:
            pass
        except WebDriverException as e:
            if count:
                self.wait()
                self.look_at_popup_window(count - 1)
            else:
                self.watch(e)
        if self.slowly:
            self.wait(2)

    def look_at(self, text, count=4):
        self.print('Loking at "{}"'.format(text))
        try:
            self.cursor = self.find_element(By.CSS_SELECTOR, '[data-label="{}"]'.format(text))
        except WebDriverException as e:
            if count:
                self.wait()
                self.look_at(text, count - 1)
            else:
                self.watch(e)
        if self.slowly:
            self.wait(2)


    def search_menu(self, text, count=4):
        self.print('Searching "{}"'.format(text))
        try:
            self.enter('Buscar...', text)
            self.wait()
            self.click(text)
        except WebDriverException as e:
            if count:
                self.wait()
                self.search_menu(text, count=count - 1)
            else:
                self.watch(e)
        self.wait()


    def click(self, text, count=4):
        self.print('Clicking "{}"'.format(text))
        try:
            self.find_element(By.CSS_SELECTOR, '[data-label="{}"]'.format(text)).click()
        except WebDriverException as e:
            if count:
                self.wait()
                self.click(text, count=count - 1)
            else:
                self.watch(e)

    def logout(self, current_username):
        self.print('Logging out')
        self.click(current_username)
        self.click('Sair')

    def close(self, seconds=0):
        self.wait(seconds)
        super().close()
