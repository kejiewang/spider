# -*- coding: utf-8 -*-
# author: kojewang

from selenium import webdriver
from urllib.parse import quote, unquote
from lxml import etree
import pandas as pd
import xlsxwriter
import datetime
import os, base64
from PIL import Image
import time
import re

dmo_uri = 'https://www.amazon.com/'
key_word = "corn light"

driver = webdriver.Chrome(executable_path='/Users/juphoon/pp/spider/chromedriver')


def img_resize(infile, outfile):
    im = Image.open(infile)
    # (x, y) = im.size  # read image size
    x_s = 120  # define standard width
    y_s = 160  # calc height based on standard width
    out = im.resize((x_s, y_s), Image.ANTIALIAS)  # resize image with high-quality
    out.save(outfile)


def gen_xml(item_infos):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    book = xlsxwriter.Workbook('amazon%s.xlsx' % timestamp)
    worksheet = book.add_worksheet('sheet1')
    worksheet.write_row(0, 0, ['id', '名称', '技术细节', '链接', '图片'])
    worksheet.set_column('A:D', 15) # 列宽约等于8像素 行高约等于1.37像素
    worksheet.set_column('C:C', 20)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('F:F', 50)
    for i in range(len(item_infos)):
        col = i + 1
        try:
            item_info = item_infos[i]
            row = [item_info['id'], item_info['title'], item_info['pro_table'], item_info['uri'], '']
            worksheet.write_row(col, 0, row)
            worksheet.set_row(col, 120)
            if 'item_pic_base64' in item_info:
                item_pic_base64 = item_info["item_pic_base64"]
                try:
                    if 'https:' in item_pic_base64:
                        data = driver.get(item_pic_base64)
                    else:
                        data = base64.b64decode(item_pic_base64)
                    with open('test.png', 'wb') as f:
                        f.write(data)
                    img_resize('test.png', 'img/tmp%s.png' % i)
                    worksheet.insert_image(col, 4, 'img/tmp%s.png' % i)  # 名字必须不同
                except Exception as e:
                    print(str(e))
        except Exception as e:
            print(str(e))
    print('完成结果数,%s' % col)
    book.close()


def get_pro_table(content):
    tree = etree.HTML(content)
    table = tree.xpath('//table[@id="productDetails_techSpec_section_1"]')
    table = etree.tostring(table[0], encoding='utf-8').decode()
    df = pd.read_html(table, encoding='utf-8', header=0)[0]
    results = list(df.T.to_dict().values())
    out = ''
    for result in results:
        for key in result:

            out = out + str(key) + ': ' + str(result[key]) + '\n'

    return out


def get_xpath(path, content):
    tree = etree.HTML(content)
    out = []
    results = tree.xpath(path)
    for result in results:
        if 'ElementStringResult' in str(type(result)) or 'ElementUnicodeResult' in str(type(result)):
            out.append(result)
        else:
            out.append(etree.tostring(result))
    return out


def get_xpath_one(path, content):
    tree = etree.HTML(content)
    out = []
    results = tree.xpath(path)
    for result in results:
        if 'ElementStringResult' in str(type(result)) or 'ElementUnicodeResult' in str(type(result)):
            out.append(result)
        else:
            out.append(etree.tostring(result))
    if out:
        return out[0]
    return ''


def get_info(content):
    item_info = {"title": ""}
    title = get_xpath_one('//span[@id="productTitle"]/text()', content)
    item_info["title"] = title
    item_pic_base64 = get_xpath_one('//div[@id="imgTagWrapperId"]/img/@src', page).split('base64,')[-1]
    item_info["item_pic_base64"] = item_pic_base64
    pro_table = get_pro_table(content)
    item_info["pro_table"] = pro_table

    return item_info


if __name__ == '__main__':

    tmp_uri = dmo_uri + '/s?k=%s&ref=nb_sb_noss_2' % quote(key_word)
    item_infos = []
    driver.get(tmp_uri)
    page = driver.page_source
    item_urls = get_xpath('//span[@data-component-type="s-product-image"]/a/@href', page)
    if not item_urls:
        print('not find uri')
    curl = 0
    for item_url in item_urls:
        curl += 1
        try:
            if not 'qid' in item_url:
                continue
            else:
                pro_url = dmo_uri + item_url
                print(pro_url)
                time.sleep(5)
                driver.get(pro_url)
                pro_content = driver.page_source
                item_info = get_info(pro_content)
                item_info['id'] = str(curl)
                item_info['uri'] = pro_url
                item_infos.append(item_info)
        except Exception as e:
            print('id is ' + str(curl))
            print(str(e))

        if curl == 1:
            break

    gen_xml(item_infos)

    print(curl)
    driver.quit()
