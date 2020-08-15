# -*- coding: utf-8 -*-
# author: kojewang

from selenium import webdriver
from urllib.parse import quote, unquote
from lxml import etree
import re

dmo_uri = 'https://www.amazon.com/'
key_word = "corn light"


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


if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path='/Users/juphoon/pp/spider/chromedriver')
    tmp_uri = dmo_uri + '/s?k=%s&ref=nb_sb_noss_2' % quote(key_word)
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
                driver.get(pro_url)
                pro_content = driver.page_source
        except Exception as e:
            print(str(e))
