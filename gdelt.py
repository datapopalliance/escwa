import re
import os
import math

import pandas as pd
import numpy as np
import requests
import json

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def fetch(row):
    url=row["SOURCEURL"]
    req=Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response=urlopen(req, timeout = 60)
    html_page=response.read()
    soup=BeautifulSoup(html_page, 'html.parser')
    row['content']=soup.find_all(text=True)
    return row

def ar_sentiment(row):
    url="http://mazajak.inf.ed.ac.uk:8000/api/predict"
    data=json.dumps({'data':row['content']})
    headers={'content-type':'application/json'}
    response=requests.post(url=url,data=data,headers=headers)
    mazaj=json.loads(response.content)['data']
    return mazaj