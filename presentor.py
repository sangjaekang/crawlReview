#-*-coding utf-8-*-
'''
    presentor
        event-handler의 역할
        URL로 request가 들어온 것들을
        적절한 처리를 하도록 도와줌

'''
import json
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import sys, os
# get this file's directory independent of where it's run from
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here,"vendored"))

import crawl.crawl_storefarm as csf

def handler(event, context):
    '''
    
    Arguments:
        - event : Similar as Request
            람다가 실행되면서 전달되는 파라미터값들이 event를 통해서 넘겨받게 됨
            GET, POST, PUT, DELETE의 동작에서 넘겨지는 
            query, body, params 등의 값들을 event에서 가져올 수 있음．
        - context : Similar as Response
            
            reference : http://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    '''
    if event is None :
        log.debug("Received None event")
        return {
            'statusCode' : 200,
            'message' : "Hello, it is working!!"
        }
    elif 'queryStringParameters' in event:
        event_qsp = event['queryStringParameters']
        log.debug("Received event {}".format(json.dumps(event)))
        if 'keyword' in event_qsp:
            search_keyword = event_qsp['keyword']
        log.debug("Start to Search and crawl")
        result_list = csf.get_review_in_storefarm(search_keyword)

        return {
            'statusCode' : 200,
            'body' : json.dumps(result_list,ensure_ascii=False)
        }