# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup

import re
import json

import time
import logging

# Crawling URL Pattern
# 네이버 스토어 팜 검색창 URL
STOREFARM_SEARCH_URL_PTR = "http://storefarm.naver.com/iloom65/search?q={}"
# 네이버 스토어 팜 프리미엄 리뷰 URL
STOREFARM_PREMIUM_RV_URL_PTR = "http://storefarm.naver.com/iloom65/products/{}/purchasereviews/premium.json?page.page={}"
# 네이버 스토어 팜 일반 리뷰 URL
STOREFARM_GENERAL_RV_URL_PTR = "http://storefarm.naver.com/iloom65/products/{}/purchasereviews/general.json?page.page={}"

def get_review_in_storefarm(search_keyword):
    global STOREFARM_PREMIUM_RV_URL_PTR, STOREFARM_GENERAL_RV_URL_PTR
    logging.debug("'get_review_in_storefarm' starts")

    reviews = []
    
    product_nums = get_product_nums_in_storefarm(search_keyword)
    if product_nums is None:
        # get_product_nums_in_storefarm()에서 Error 발생할 경우，
        # empty list 반환
        return reviews
    
    for product_num in product_nums:
        # PREMIUM 리뷰 크롤링
        reviews.extend(get_review_json_in_storefarm(product_num,STOREFARM_PREMIUM_RV_URL_PTR))
        # GENERAL 리뷰 크롤링
        reviews.extend(get_review_json_in_storefarm(product_num,STOREFARM_GENERAL_RV_URL_PTR))

    return reviews


def get_product_nums_in_storefarm(search_keyword):
    # 검색 keyword에 해당하는 제품의 고유식별번호를 찾는 함수
    global STOREFARM_SEARCH_URL_PTR
    logging.debug("'get_product_nums_in_storefarm' starts")

    storefarm_search_url = STOREFARM_SEARCH_URL_PTR.format(search_keyword)
    try:
        html = urlopen(storefarm_search_url)
    except HTTPError as e:
        logging.debug("주소({})에 접속이 되지 않습니다．")
        return None
    try:
        bsObj = BeautifulSoup(html, "html.parser")
        search_list =\
            bsObj.find("div",{"class":"sec_dis_list"}).\
            find_all('div',{'class':'img_center'})

        for content in search_list:
            product_href = content.a.attrs['href']
            product_num = product_href.split("/")[-1]
            yield product_num
    
    except AttributeError as e:
        logging.debug("이 제품명({})의 상품 정보가 네이버 스토어에 없습니다.".format(product_name))
        return None


def get_review_json_in_storefarm(product_num,review_url_ptr):
    # 네이버 스토어팜에서 JSON 형식의 review들을 끌어오는 함수
    
    result_list = []

    page_num = 1
    while True:
        try:
            response = urlopen(
                review_url_ptr.format(product_num,page_num))
            charset = response.info().get_content_charset()
            logging.debug("response-Charset : {}".format(charset))
            
            if charset == "" or charset is None :
                response_content = response.read()
            else:
                response_content = response.read().decode(charset)

            # 한글문제로　encoding을　utf-8로　지정
            json_contents = json.loads(response_content,encoding='utf-8')
            review_contents = json_contents['htReturnValue']['pagedResult']['content']

            if len(review_contents) == 0 :
                # review 평이 없는 경우 종료
                break

            result_list.extend(review_contents)
        except AttributeError as e:
            logging.debug("Json({}) 내에 해당하는 정보가 없습니다.")
            break
        else:
            page_num += 1
            time.sleep(0.2)
        
    return result_list