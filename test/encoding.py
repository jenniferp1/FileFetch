import chardet
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import re

def unicodify(seq, min_confidence=0.5):

    guess = chardet.detect(seq)
    if guess["confidence"] < min_confidence:
        # chardet isn't confident enough in its guess, so:
        raise UnicodeDecodeError

    decoded = seq.decode(guess["encoding"])

    return decoded

def fetch_csv(url):


    try:
        req = requests.get(url)
        if req.ok:
            rawdata = req.content
            data = unicodify(rawdata)
            # charenc = data['encoding']
            # .decode("utf8") #'cp1252'
            df = pd.read_csv(StringIO(data))
            # TODO return data and create method for converting to dataframe
        else:
            print("Error: CSV was not fetched for some reason\n")
            df = pd.DataFrame()
    except requests.exceptions.Timeout as er:
        print("WARNING:  Requests Timeout Error")
        print(er)
        df = pd.DataFrame()

    return df

def scan_csv_list(url):
    # Issue request: r => requests.models.Response
    r = requests.get(url)

    # Extract text: html_doc => str
    html_doc = r.text

    # Parse the HTML: soup => bs4.BeautifulSoup
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Find all 'a' tags (which define hyperlinks): a_tags => bs4.element.ResultSet
    a_tags = soup.find_all('a')

    # Store a list of urls ending in .csv: urls => list
    urls = ['https://raw.githubusercontent.com'+re.sub('/blob', '', link.get('href'))
            for link in a_tags  if '.csv' in link.get('href')]

    # Store a list of file names
    list_names = [url.split('.csv')[0].split('/')[url.count('/')] for url in urls]

    return urls, list_names

def date_in_str(pattern, prev_date, string):

    if re.match(pattern, string):
        m = re.match(pattern, string).group(0)
        if m > prev_date:
            return m
    return None

def fetch_csv_git_scan(url, key_phrase):

    url = check_last_load(url, key_phrase)

    if url:
        df = fetch_csv(url)
        return df

    return "You have most recent version of data"

def check_last_load(url, key_phrase):

    urls, names = scan_csv_list(url)
    new_date = None
    pos = -999
    for i, name in reversed(list(enumerate(names))):
        if name[:4].isdigit():
            new_date = date_in_str(key_phrase["pattern"],key_phrase["last_date"],name)
            if new_date:
                pos = i
                break

    if pos >= 0:
        url = urls[pos]
    else:
        url = None
    return url

# url = "https://raw.githubusercontent.com/COVID19StatePolicy/SocialDistancing/master/data/USstatesCov19distancingpolicyBETA.csv"
# df = fetch_csv(url)
# print(df)

url = "https://github.com/KFFData/COVID-19-Data/tree/kff_master/State%20Policy%20Actions/State%20Social%20Distancing%20Actions"
key_phrase = {"pattern":"\\d{4}-\\d{2}-\\d{2}", "last_date":"2020-08-31"}

df = fetch_csv_git_scan(url, key_phrase)
# print(df)
# print(type(df))

if isinstance(df, pd.DataFrame):
    print(df.head())
else:
    print("not a dataframe")
    print(df)
