# -*- coding: utf-8 -*-
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv
import json
import requests
from selenium.common.exceptions import NoSuchElementException


# 情感分析
def get_token():
    url = \
        "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=neR0VVGGMy6cKElsOkW0OSlB&client_secret=33Z3ZXKo6k1CrnuSNIHIDGGYIPlUkNLs"
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()["access_token"]
    return token


def emotion(text, token):
    url = f"https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token={token}&charset=UTF-8"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    new_each = {
        'text': text
    }
    new_each = json.dumps(new_each)
    try:
        response = requests.request("POST", url, headers=headers, data=new_each,timeout=10)
        result = response.json()
    except:
        for i in range(4):
            response = requests.request("POST", url, headers=headers, data=new_each, timeout=10)
            result = response.json()
            if response.status_code == 200:
                break
    try:
        confidence = result["items"][0]["confidence"]
        negative_prob = result["items"][0]["negative_prob"]
        positive_prob = result["items"][0]["positive_prob"]
        sentiment = result["items"][0]["sentiment"]
        status_node = 1
        # print(result)
        return confidence, negative_prob, positive_prob, sentiment, status_node
    except KeyError:
        confidence = "null"
        negative_prob = "null"
        positive_prob = "null"
        sentiment = "null"
        status_node = 1
        # print(confidence, negative_prob, positive_prob, sentiment)
        return confidence, negative_prob, positive_prob, sentiment, status_node


# 判断是否有展开全文
def is_exist_z(web):
    try:
        txt = web.find_element(By.XPATH, './div/div/div/article/div[2]/div[1]/a[3]').text
        if txt == '全文':
            return True
        else:
            return False
    except Exception:
        return False


# 获取评论
def get_comment(div, web, token, writer, writer_list):
    # 点击评论展开
    global comment_id
    button = div.find_element(By.XPATH, './div/div/div/article/div[2]/div[1]')
    web.execute_script("arguments[0].click()", button)
    # div.find_element(By.XPATH, './div/div/div/article/div[2]/div[1]').click()
    time.sleep(1)
    # comment_info = []
    comment_div_list = web.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div/div[4]/div[2]/div')
    div_list_count = 0
    while div_list_count < len(comment_div_list)-1:
        # 控制滑动
        web = scroll2(web)
        comment_div_list = web.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div/div[4]/div[2]/div')
        # print('length:', len(comment_div_list))
        for div_t in comment_div_list[div_list_count:]:
            # comment_info_test = []
            time.sleep(0.5)
            try:
                comment_user = div_t.find_element(By.XPATH, './div/div/div/div/div[2]/div[1]/div/div/h4').text
                comment_detail = div_t.find_element(By.XPATH, './div/div/div/div/div[2]/div[1]/div/div/h3').text
                comment_detail = comment_detail+" "  # 避免报错
                comment_id_list = \
                    div_t.find_element(By.XPATH, './div/div/div/div/div[2]/div[2]/div').text.split(' ', -1)
                length = len(div_t.find_element(By.XPATH, './div/div/div/div/div[2]/div[2]/div').text.split(' ', -1))
                comment_time = comment_id_list[0]
                # if length == 2:
                #     comment_id = comment_id_list[1].split("自", -1)[1]
                # elif length == 3:
                #     comment_id = comment_id_list[2].split("自", -1)[1]
                try:
                    if length == 2:
                        comment_id = comment_id_list[1].split("自", -1)[1]
                    elif length == 3:
                        comment_id = comment_id_list[2].split("自", -1)[1]
                except IndexError:
                    comment_id = "null"
                except NoSuchElementException:
                    comment_id = "null"
            except NoSuchElementException:
                time.sleep(2)
                comment_user = "null"
                comment_detail = "null"
                comment_id = "null"
                comment_time = "null"
            # print('user:',comment_user)
            print(comment_user)
            # print(comment_detail)
            con, neg, pos, sen, sta = emotion(comment_detail, token)
            # comment_info_test.append(comment_user)
            # comment_info_test.append(comment_detail)
            # comment_info_test.append(comment_time)
            # comment_info_test.append(comment_id)
            # comment_info_test.append(con)
            # comment_info_test.append(neg)
            # comment_info_test.append(pos)
            # comment_info_test.append(sen)
            # temp_list = comment_info_test[:]
            # # 保存数据
            # comment_info.append(temp_list)

            writer_list.append(comment_user)
            writer_list.append(comment_detail)
            writer_list.append(comment_time)
            try:
                writer_list.append(comment_id)
            except NameError:
                comment_id = "null"
                writer_list.append(comment_id)
            writer_list.append(con)
            writer_list.append(neg)
            writer_list.append(pos)
            writer_list.append(sen)
            # 写入文件
            writer.writerow(writer_list)
            # 删除并更新评论
            del writer_list[9:18]
            div_list_count += 1
            break
    web.back()
    # web.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/div[1]/div[1]/i').click()

# a.extend(b)     将b列表中的元素逐个追加到a列表
# a.append(b)     将对象添加到a列表


# 登录
def login():
    url = 'https://m.weibo.cn/'
    opt = Options()
    # opt.add_argument("--proxy-server=http://60.182.197.86:8888")
    # 删掉Chrome浏览器正在受到自动测试软件的控制
    opt.add_experimental_option('excludeSwitches', ['enable-automation'])
    # opt.add_argument('headless')
    # opt.add_argument('window-size=1920x1080')
    # 创建浏览器对象
    web = webdriver.Chrome(options=opt)
    web.get(url)
    input("是否完成登录？")
    return web


# 点击热门
def click_hot(web):
    # 点击热门
    web.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div/div/ul/li[5]/span').click()
    time.sleep(2)
    return web

# 控制滑动
def scroll(web, _count):
    count = 0
    # while count < int(_count):
    while count < 1:
        web.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        count += 1
    time.sleep(1)
    return web


def scroll2(web):
    count = 0
    while count < 1:
        web.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        time.sleep(0.5)
        count += 1
    return web


# 爬取数据
def page_spider():
    # 写入文件
    f = open('./data3.csv', mode='w', encoding='utf-8', newline='')
    writer = csv.writer(f)
    # writer.writerow(['用户名','微博内容','点赞数','评论数','转发数','评论用户','评论内容','评论时间'])
    writer.writerow(['用户名', '微博内容', '点赞数', '评论数', '转发数', '置信度', '消极类别概率', '积极类别概率', '情感极性分类结果',
                     '评论用户', '评论内容', '评论时间', '评论id', '评论置信度', '评论消极类别概率', '评论积极类别概率', '评论情感极性分类结果'])
    token = get_token()
    # 登录
    web = login()
    # 跳转到搜索页面
    web.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[1]/a/aside/label/div').click()
    time.sleep(1)
    data = input('请输入话题：')
    # data = '广东'

    web.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[1]/div/div/div[2]/form/input').send_keys(data, Keys.
                                                                                                          ENTER)
    time.sleep(3)

    # 点击热门
    web = click_hot(web)
    # 所有微博所在的div
    div_list = web.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div')
    # 要爬取的微博内容的div下标
    div_count = 2
    while div_count < len(div_list):
        time.sleep(2)
        # 点击热门并滑动
        try:
            web = click_hot(web)
        except NoSuchElementException:
            web.refresh()
            time.sleep(2)
            web = click_hot(web)
        web = scroll(web, div_count)
        # 所有微博所在的div
        div_list = web.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div')
        for div in div_list[div_count:]:
            time.sleep(1)
            try:
                user_name = div.find_element(By.XPATH, './div/div/div/header/div/div/a/h3').text
            except NoSuchElementException:
                web = click_hot(web)
                web.refresh()
                time.sleep(2)
                user_name = div.find_element(By.XPATH, './div/div/div/header/div/div/a/h3').text
            if is_exist_z(div):
                # 获得全文链接
                detail_page_content_url = \
                    div.find_element(By.XPATH, './div/div/div/article/div[2]/div[1]/a[3]').get_attribute('href')
                # 使用js语句打开全文链接
                js = "window.open('" + detail_page_content_url + "');"
                web.execute_script(js)
                time.sleep(1)
                # 切换窗口
                web.switch_to.window(web.window_handles[1])
                time.sleep(1)
                try:
                # 获取全文
                    page_detail = \
                        web.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div/article/div/div/div[1]').text
                except NoSuchElementException:
                    web.refresh()
                    time.sleep(2)
                    page_detail = \
                        web.find_element(By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div/article/div/div/div[1]').text
                web.close()
                # 切换回原来的窗口
                web.switch_to.window(web.window_handles[0])
                time.sleep(1)
            else:
                try:
                    page_detail = div.find_element(By.XPATH, './div/div/div/article/div/div[1]').text
                except NoSuchElementException:
                    web.refresh()
                    time.sleep(2)
                    page_detail = div.find_element(By.XPATH, './div/div/div/article/div/div[1]').text
            '''点赞，评论，转发数'''
            try:
                praise = div.find_element(By.XPATH, './div/div/div/footer/div[3]/h4').text
                comment = div.find_element(By.XPATH, './div/div/div/footer/div[2]/h4').text
                tran = div.find_element(By.XPATH, './div/div/div/footer/div[1]/h4').text
            except NoSuchElementException:
                web.refresh()
                time.sleep(2)
                praise = div.find_element(By.XPATH, './div/div/div/footer/div[3]/h4').text
                comment = div.find_element(By.XPATH, './div/div/div/footer/div[2]/h4').text
                tran = div.find_element(By.XPATH, './div/div/div/footer/div[1]/h4').text
            print('user name:', user_name)
            con, neg, pos, sen, sta = emotion(page_detail, token)
            writer_list = []
            if sta == 1:
                writer_list.append(user_name)
                writer_list.append(page_detail)
                writer_list.append(praise)
                writer_list.append(comment)
                writer_list.append(tran)
                writer_list.append(con)
                writer_list.append(neg)
                writer_list.append(pos)
                writer_list.append(sen)
                get_comment(div, web, token, writer, writer_list)
                # 这种方法是将一条微博全部爬完再写入，如果遇到反爬容易丢失数据
                # for detail in comment_info_detail:
                #     writer_list.append(detail[0])
                #     writer_list.append(detail[1])
                #     writer_list.append(detail[2])
                #     writer_list.append(detail[3])
                #     writer_list.append(detail[4])
                #     writer_list.append(detail[5])
                #     writer_list.append(detail[6])
                #     writer_list.append(detail[7])
                #     # 写入文件
                #     writer.writerow(writer_list)
                #     # 删除并更新评论
                #     del writer_list[9:17]
            else:
                writer_list.append(user_name)
                writer_list.append(page_detail)
                writer_list.append(praise)
                writer_list.append(comment)
                writer_list.append(tran)
                writer.writerow(writer_list)
            div_count += 1
            print("OK")
            break
    f.close()


if __name__ == '__main__':
    page_spider()
