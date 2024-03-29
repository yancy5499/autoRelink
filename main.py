#!venv/Scripts/python.exe
import os
import subprocess
from time import sleep, asctime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import getpass


def fill(browser, username, password, service_value):
    # 输入用户名
    user = browser.find_element(by=By.CSS_SELECTOR,  # 检查元素后右键复制为selector
                                value='#edit_body > div:nth-child(3) > div.edit_loginBox.ui-resizable-autohide > form > input:nth-child(2)')
    user.send_keys(username)
    # 输入密码
    pwd = browser.find_element(by=By.CSS_SELECTOR,
                               value='#edit_body > div:nth-child(3) > div.edit_loginBox.ui-resizable-autohide > form > input:nth-child(3)')
    pwd.send_keys(password)
    # 选择运营商
    if service_value:
        service = browser.find_element(by=By.CSS_SELECTOR,
                                       value='#edit_body > div:nth-child(3) > div.edit_loginBox.ui-resizable-autohide > select')
        Select(service).select_by_value(value=service_value)
    return user


def login(url, username, password, service_value):
    browser = webdriver.Edge()
    browser.get(url)
    browser.implicitly_wait(10)
    user = fill(browser, username, password, service_value)
    # 登录
    # 如果有序列表<li>和无序列表<ul>组成了一个form表单，登录按钮为submit，那么提交任意一个元素会整个表单一起提交
    user.submit()
    sleep(5)
    try:
        back = browser.find_element(by=By.XPATH,  # 不知道为什么此处不能用css定位
                                    value='//*[@id="edit_body"]/div[2]/div[2]/form/input')
        # 登录后注销的按钮XPATH与返回相同，需要判断按钮名字
        button_name = back.get_attribute('value')
        # 校园网偶尔抽风需要返回重登，但一般第二次就成功了
        if button_name == '返  回':
            back.click()
            sleep(10)
            # 第二次登录
            print('back and relink!')
            fill(browser, username, password, service_value).submit()
        elif button_name == '注  销':
            print('relink ok!')
        else:
            raise Exception
    except:
        print('second login error')
    # 登录成功之后就可以关闭浏览器了
    sleep(5)
    browser.close()


def user_input():
    username = None
    password = None
    service_value = None
    keylist = [username, password, service_value]
    if os.path.exists('key.txt'):
        print('Password file detected!')
        with open('key.txt', 'r', encoding='utf-8') as f:
            for i in range(len(keylist)):
                keylist[i] = f.readline().split('\n')[0]
    else:
        print('''
        # 输入用户密码登录，密码输入时会隐藏
        # 运营商选择如下：
        # 校园网回车就行
        # 移动@cmcc
        # 联通@unicom
        # 电信@telecom
        ''')
        keylist[0] = input('username:')
        keylist[1] = getpass.getpass(prompt='password:')  # 只支持在控制台中使用，在IDE中会看不到
        keylist[2] = input('service:')
        with open('key.txt', 'w', encoding='utf-8') as f:
            for key in keylist:
                f.write(key)
                f.write('\n')
        print('The password file has been saved in key.txt!')
    return keylist


if __name__ == '__main__':
    url = 'http://172.17.0.2/'
    # # 账户密码
    # username = '学号'
    # password = '密码'
    # # 运营商选择
    # # 校园网填False就行
    # # 移动@cmcc
    # # 联通@unicom
    # # 电信@telecom
    # service_value = '@cmcc'

    username, password, service_value = user_input()

    # 判断是否断网
    while True:
        r = subprocess.run('ping www.bilibili.com',
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE,
                           shell=True)
        if r.returncode:
            print('relink:', asctime())
            try:
                login(url, username, password, service_value)
            except:
                input('first login error, Enter any key to exit')
                break
        else:
            print('linked:', asctime())
        sleep(60 * 3)  # 判断网络的时间间隔
