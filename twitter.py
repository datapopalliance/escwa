import requests
import json
import pandas as pd
import numpy as np
import os
from requests_oauthlib import OAuth1
from src.keywords import TAGS_EN,TAGS_AR
from src.constants import POLICY_DATES
from google.cloud import language_v1
from google.cloud.language_v1 import enums

def query(keywords,fromDate,toDate=None):
    body={
        'query':keywords,
        'fromDate': fromDate, 
        'toDate': toDate, 
    }
    response = requests.post(
        'https://api.twitter.com/1.1/tweets/search/fullarchive/development.json',
        json=body,
        headers={'Content-Type':'application/json'},
    )
    json.dump(response.json(),filepath,ensure_ascii=False)

def en_sentiment(row):
    document = {'content':row['text'],'type':enums.Document.Type.PLAIN_TEXT}
    response = client.analyze_sentiment(document, encoding_type=enums.EncodingType.UTF8)
    return response.document_sentiment.score