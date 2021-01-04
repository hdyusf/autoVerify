import random
from time import sleep
import base64

from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from PIL import Image


class Crack():
    def __init__(self, username, passwd):
        self.url = 'http://192.168.1.200:9001/user/login'
        self.browser = webdriver.Chrome()
        self.BORDER = 6
        self.ERROR = 0
        self.passwd = passwd
        self.username = username

    def open(self):
        """
        打开浏览器 输入内容 点击登陆
        """
        self.browser.get(self.url)
        # 输入账号
        user = self.browser.find_element_by_xpath('//*[@name="user"]')
        user.send_keys(self.username)
        # 输入密码
        password = self.browser.find_element_by_xpath('//*[@type="password"]')
        password.send_keys(self.passwd)
        # 点击登陆
        sleep(1)
        login = self.browser.find_element_by_class_name('login_btn')
        login.click()

    def crack(self):
        """
        破解
        """
        # 获取偏移量
        diff = self.getDiff()
        # 生成移动轨迹
        track = self.getTrack(diff)
        # 获取滑块
        self.awaitElement('geetest_slider_button')
        slider = self.browser.find_element_by_class_name(
            'geetest_slider_button')
        # 拖动滑块到指定位置
        self.moveTo(slider, track)

        # 重置
        self.isReset()

    def getDiff(self):
        """
        name: 获取偏移量
        """
        self.awaitElement('geetest_canvas_bg')
        sleep(1)
        image1 = self.getImageData('geetest_canvas_bg')
        image2 = self.getImageData('geetest_canvas_fullbg')

        distance = self.diffPixel(image1, image2)
        if self.ERROR >= 3:
            self.ERROR = -3
        if self.ERROR < -3:
            self.ERROR = 3
        distance = distance - (self.BORDER + self.BORDER / 2 * self.ERROR)
        return distance

    def getTrack(self, distance):
        """
        name: 根据偏移量计算移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 加速度
        move = 0
        while current < distance:
            # 当前位移
            current += move
            if current > distance:
                current = distance
            # 加入轨迹
            track.append(round(move))
            move += 0.1
        move = 0
        return track

    def moveTo(self, slider, track):
        """
        name: 拖动滑块到指定位置
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        while track:
            x = random.choice(track)
            ActionChains(self.browser).move_by_offset(
                x, 0).perform()
            track.remove(x)
        sleep(1)
        ActionChains(self.browser).release(slider).perform()

    def isReset(self):
        sleep(3)
        try:
            # 排错
            ct = self.browser.find_element_by_class_name(
                'geetest_panel_error')
            if ct:
                display = ct.value_of_css_property('display')
                if display == 'block':
                    # 重试
                    sleep(1)
                    error = self.browser.find_element_by_class_name(
                        'geetest_panel_error_content')
                    error.click()
                    self.ERROR += 1
                    sleep(1)
                    self.crack()
                    return
            ct = self.browser.find_element_by_class_name(
                'geetest_panel_success')
            if ct:
                display = ct.value_of_css_property('display')
                if display == 'none':
                    # 重试
                    sleep(1)
                    self.ERROR += 1
                    self.crack()
                    return
        except Exception as e:
            print(e)

    def awaitElement(self, target):
        """
        name: 等待元素
        :params target:String 目标class名称
        :return 等待目标元素出现
        """
        return WebDriverWait(self.browser, 10).until(
            lambda x: x.find_element_by_class_name(target))

    def getImageData(self, target):
        """
        name: 获取图片信息
        intro:
          获取指定元素转换成图片
          将图片保存到本地
          读取图片信息并返回
        :params target:String 目标class名称
        :return res:Image 可读取的图片信息
        """
        JS = 'return document.getElementsByClassName("' + \
            target + '")[0].toDataURL("image/png");'
        canvasData = self.browser.execute_script(JS)
        # 获取base64编码的图片信息
        im_base64 = canvasData.split(',')[1]
        # 转成bytes类型
        im_bytes = base64.b64decode(im_base64)
        res = ''
        # 保存图片到本地 并读取图片信息后返回
        with open(target + '.png', 'wb') as f:
            f.write(im_bytes)
            sleep(0.5)
            res = Image.open(target + '.png')
            return res
        return res

    def diffPixel(self, image1, image2):
        """
        name: 比对像素
        intro:
            循环比对图片像素
            返回发现像素极差值的坐标
        :params image1:Image 图片信息
        :params image2:Image 图片信息
        :return 目标坐标
        """
        # 像素极差
        threshold = 70
        width = image1.size[0]
        height = image1.size[1]
        # 发现像素差的x轴坐标
        distance = 0
        for i in range(0, width):
            for j in range(0, height):
                pixel1 = image1.load()[i, j]
                pixel2 = image2.load()[i, j]
                if abs(pixel1[0] - pixel2[0]) > threshold or abs(pixel1[1] - pixel2[1]) > threshold or abs(pixel1[2] - pixel2[2]) > threshold:
                    distance = i
                    return distance
        print(distance)
        return distance


crack = Crack('18833332222', '000000000')
crack.open()
crack.crack()
print('验证成功')
