# find other in-house packages in directory path
import os, sys, inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


import os
import time
import re
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime, date
import calendar
from pprint import pprint

# import packages for hitting websites
import requests
from bs4 import BeautifulSoup
from urllib.parse import  urljoin
# import pyppdf.patch_pyppeteer
from requests_html import AsyncHTMLSession
from urllib.parse import unquote
import camelot

# import Mixins
import _initialize  # hold initialization-checking methods

# import other homegrown modules
import vdh


def checkdir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return


def get_absolute_path(url, doc_url):
    return urljoin(url,doc_url)


def parse_pdf(url, txt, pdf_name):

    if "www.health.state.mn.us" in url:
        pdf_page = "7"
        day = re.findall(r"(\d{1,2}\/\d{1,2}\/\d{4})", txt)[0]
        day = datetime.strptime(day,"%m/%d/%Y")
        day = day.strftime("%Y%m%d")
        file_weeklypos = f"./mdh_weekly_positivity_{day}.csv"
        mn = parse_mn_weekly_report(pdf_name, pdf_page)  # method to parse table from pdf
        mn.to_csv(file_weeklypos,index=False)
        mn = clean_mn_weekly_report(file_weeklypos)
        return mn

    return pd.DataFrame()


def parse_mn_weekly_report(pdf_name, pgs, ws=101):

    tables = camelot.read_pdf(pdf_name, pages=pgs)
    datatable = pd.DataFrame()

    for t in tables:
        whitespace = t.parsing_report["whitespace"]
        if whitespace < ws:
            ws = whitespace
            datatable = t

    return datatable.df


def clean_mn_weekly_report(file_weeklypos):

    mn = pd.read_csv(file_weeklypos, skiprows=1)

    partitions = 2
    dfs = np.array_split(mn, partitions, axis=1)

    dfs[0].columns = ["County","Positive"]
    dfs[1].columns = ["County","Positive"]

    mn = dfs[0].append(dfs[1], ignore_index=True)

    mn.replace("%", "", regex=True, inplace=True)
    mn.replace("\n", "", regex=True, inplace=True)
    mn.replace("\t", "", regex=True, inplace=True)

    mn['County'] = mn['County'].str.replace("\-?(\d+\.?\d*|\d*\.?\d+)", "")

    mn = mn[~mn.County.str.startswith("Unknown")]

    fips = pd.read_csv("../selenium/county_fips.csv", dtype={"fips":str})
    fips = fips[fips.stateiso=="MN"]
    fips["county"] = fips["county"].str.replace(" County","")

    mn = pd.merge(mn, fips, left_on="County", right_on="county", how="left")
    mn.drop(columns=["county"], inplace=True)

    # print(mn.head())

    return mn


#######################################################
# UPDATE INSTRUCTIONS (if you need to add sources):
# To add a fetch file type to class FileFetch:
# 1. self.file_list - a list with allowable file types. Add file type to list.
# 2. fetch() - method to download data; has 'if clause' for each file type.
#    Add file type to 'if clause'
# 3. fetch_*() - specific file type method called by fetch().
#    Add a new fetch_*() method for retrieving new file type
#####################################################


class FileFetch(_initialize.InitializeCheck):
    def __init__(self, params=None, params_file=None):

        # params is user supplied dictionary: url and file type (e.g., csv, text, html-stream)
        # params_file = list: location of yaml & header to grab

        self.file_list = [
            "csv",
            "html-stream",
            "findlink",
        ]  # update with allowed file types as add capability

        # call mixin InitializeCheck class from _initialize.py to make sure user inputs are valid
        # if invalid, returns message letting user know error
        # if all okay, prints url and file type to screen as confirmation
        self.init_check(params, params_file)

        # print to screen confirmation that initialization worked
        print(f"\nurl set to '{self.url}'")
        print(f"file type to download is '{self.file_type}'")
        if self.key_phrase:
            print(f"key_phrase is '{self.key_phrase}'")

        return

    def get_description(self):
        if self.desc:
            print(f"data description: {self.desc}")
        else:
            print("No description provided by user")

        return

    def get_webref(self):
        if self.webref:
            print(f"reference site url: {self.webref}")
        else:
            print("No reference site provided by user")

        return

    def fetch(self):
        # TODO add optional key_phrase for use with html-stream

        # if you need to add a file type at to if clause
        # and create a new "fetch" method to download the data
        if self.file_type in self.file_list:
            if self.file_type == "csv":
                df = self.fetch_csv()

            if self.file_type == "html-stream":
                self.session = AsyncHTMLSession()
                results = self.session.run(self.fetch_html_stream)
                df = self.link_to_df(results)

            if self.file_type == "findlink":
                doc_url, txt = self.fetch_link()
                if doc_url:
                    if self.file_ext == "csv":
                        df = self.fetch_csv_stream(doc_url)
                    if self.file_ext == "pdf":
                        front = doc_url.split("/")[2]
                        front = front.replace("www.","")
                        front = front.replace(".","-")
                        back = doc_url.split("/")[-1]
                        pdf_name = f"{front}_{back}"
                        self.download_pdf(doc_url, pdf_name)
                        df = parse_pdf(self.url, txt, pdf_name)

                else:
                    print("Error: findlink did not return a document link\n")
                    df = pd.DataFrame()


        else:
            # pp = pprint.PrettyPrinter(indent=1)
            print(
                f"\nError: currently no capability to download this file type: {self.file_type}"
            )
            print(f"Allowable file types are:  ")
            pprint(self.file_list, width=5)
            print("Exiting....")
            exit()

        print("Data fetched! Saved to DataFrame.\n")

        return df

    def fetch_csv(self):

        if self.file_type != "csv":
            print(
                f"\nError: called function to fetch csv but your file type is: {self.file_type}"
            )
            print("Exiting....")
            exit()

        print("Fetching file...\n")

        req = requests.get(self.url)
        if req.ok:
            data = req.content.decode("utf8")
            df = pd.read_csv(StringIO(data))
            # TODO return data and create method for converting to dataframe

        return df

    def fetch_csv_stream(self, doc_url):

        time.sleep(1)
        try:
            req = requests.get(doc_url, timeout=(3,30))
            data = str(BeautifulSoup(req.content, 'html.parser'))
            df = pd.read_csv(StringIO(data))

        except requests.exceptions.Timeout as er:
            print("WARNING:  Requests Timeout Error")
            print(er)
            df = pd.DataFrame()

        return df

    async def fetch_html_stream(self):

        if self.file_type != "html-stream":
            print(
                f"\nError: called function to fetch html-stream but your file type is: {self.file_type}"
            )
            print("Exiting....")
            exit()

        if self.key_phrase == None:
            print("Error:  key_phrase is None")
            print(
                "\tFetching html-stream requires a key_phrase to search on"
            )
            print("Exiting....")
            exit()

        print("Fetching file...\n")
        # TODO modify call to this method so requires input: key_phrase

        r = await self.session.get(self.url)
        await r.html.arender(wait=3.0, timeout=5.0)

        return r

    def fetch_link(self):

        if self.file_type != "findlink":
            print(
                f"\nError: called function to fetch findlink but your file type is: {self.file_type}"
            )
            print("Exiting....")
            exit()

        if self.tag == None:
            print("Error:  tag is None")
            print(
                "\tFetching link requires a css tag to search on"
            )
            print("Exiting....")
            exit()

        if self.search == None:
            print("Error:  search terms is None")
            print(
                "\tFetching link requires a class or id term to search on"
            )
            print("Exiting....")
            exit()

        if self.tag2 == None:
            print("Error:  you did not provide if this is a nested search")
            print(
                "\tFetching link requires setting nested to 'yes' or 'no'"
            )
            print("Exiting....")
            exit()

        if self.file_ext == None:
            print("Error:  file extension type is None")
            print(
                "\tFetching link requires a file extension, e.g., 'pdf', 'csv'..."
            )
            print("Exiting....")
            exit()

        print("Fetching link...\n")

        req = requests.get(self.url)
        soup = BeautifulSoup(req.content, 'html.parser')

        whole_section = soup.find_all(self.tag, self.search)

        if self.tag2:
            for section in whole_section:
                nested_tag = section.find_all("a")
                for link in nested_tag:
                    doc = link.get("href")
                    txt = str(link.text)
                    if doc.lower().endswith(self.file_ext):
                        if not doc.startswith("http"):
                            doc = get_absolute_path(url, doc)
                        return doc, txt
        else:
            for self.tag in whole_section:
                doc = self.tag.find("a").get("href")
                txt = str(self.tag.find("a").text)
                if doc.lower().endswith(self.file_ext):
                    if not doc.startswith("http"):
                        doc = get_absolute_path(self.url, doc)
                    return doc, txt

        return None, None


    def link_to_df(self, results):

        for r in results:
            links = r.html.links

            for link in links:
                if link.startswith(self.key_phrase):
                    link = link.lstrip(self.key_phrase)
                    stream = unquote(link)
                    data = StringIO(stream)
                    df = pd.read_csv(data, sep=",")

                    return df

        return pd.DataFrame()

    def download_pdf(self, pdf_url, pdf_name):
        response = requests.get(pdf_url)

        with open(pdf_name, "wb") as p:
            p.write(response.content)

        return print(f"pdf saved as {pdf_name}\n")

    def save(self, df, fname, ftype="csv", fpath="./", index=False):

        if df.size == 0:
            print("\n\t*** WARNING *** DataFrame is empty. Trying again.\n")
            return False

        today = date.today()
        save_as = f"{fname}_{today}.{ftype}"

        if "\\" in fpath:
            fpath = fpath.replace("\\", "/")

        checkdir(fpath)  # create folder if fpath does not exist

        if fpath.endswith("/"):
            full_path = f"{fpath}{save_as}"
        else:
            full_path = f"{fpath}/{save_as}"

        if ftype == "csv":
            df.to_csv(full_path, index=index)
        elif ftype == "excel":
            df.to_excel(full_path, index=index)

        print(f"File saved to:\t{full_path}\n")

        return True


if __name__ == "__main__":
    # execute only if run as a script

    """
    ########################################################
    # Uncomment to test                                    #
    ########################################################
    """

    # # key_phrase = "data:application/octet-stream;charset=utf-8,"
    # key_phrase = None
    # params = {
    #     "url": "http",
    #     "file_type": "html-stream",
    #     "key_phrase": key_phrase,
    # }
    # yaml_file = ["../url_filefetch.yml", "covid_tracking_proj_hist"]
    #
    # file = FileFetch(params_file=yaml_file)
    # file = FileFetch(params)

    # file.get_description()
    # file.get_webref()

    # df = file.fetch()
    # print(df.head())
    # # print(df.dtypes)
    # file.save(df, fname="testrun", fpath="./covid_exit_strategy_testing")

    # TODO throw specified error (code) if url connection has a problem
    # TODO merge, drop columns, calculate 7-day moving average positivity,
    # TODO 7-day moving average for new cases, 14-day % change
    # TODO post-processor to clean up files (e.g., change dtypes, header names, merges/joins)
    # TODO Load to database - combine with supercharge package

    # TODO move methods external to class to util.py

    # TODO: add csv-googledocs for covid tracking project
    # TODO: add ability to append a date for reading github JHU

    """
    ########################################################
    # Daily upload code comment out above test code to run #
    ########################################################
    """

    rt_file = ["../url_filefetch.yml", "rt_live"]
    tat_file = ["../url_filefetch.yml", "test_and_trace"]
    ces_file = ["../url_filefetch.yml", "covid_exit_strat_testing"]
    ces_file2 = ["../url_filefetch.yml", "covid_exit_strat_healthcare"]
    ces_file3 = ["../url_filefetch.yml", "covid_exit_strat_spread"]
    ctp = ["../url_filefetch.yml", "covid_tracking_proj_race"]
    ctph = ["../url_filefetch.yml", "covid_tracking_proj_hist"]
    mn = ["../url_filefetch.yml", "minnesota"]
    va = ["../url_filefetch.yml", "virginia"]

    files = [rt_file, tat_file, ces_file, ces_file2, ces_file3, ctp, ctph, mn, va]

    fnames = [
        "rtlive",
        "testandtrace",
        "covidexitstrategy",
        "covidexitstrategy",
        "covidexitstrategy",
        "covidtrackproj",
        "covidtrackproj",
        "MinnesotaCountyTestData",
        "VirginiaHealthDistrictTestData"
    ]

    fpaths = [
        "./rt_live",
        "./test_trace",
        "./covid_exit_strategy_testing",
        "./covid_exit_strategy_healthcare",
        "./covid_exit_strategy_spread",
        "./covid_tracking_proj_race",
        "./covid_tracking_proj_hist",
        "./minnesota",
        "./virginia"
    ]

    dayofweek = date.today()
    dayofweek = calendar.day_name[dayofweek.weekday()]


    for i in range(len(files)):

        if (files[i][1] == "minnesota") and (dayofweek != "Thursday"):
            print(f"Today is not Thursday. Skipping Minnesota weekly update.")
            continue
        if (files[i][1] == "covid_tracking_proj_race") and (dayofweek != "Sunday" and dayofweek != "Thursday"):
            print(f"Today is not Sunday or Thursday. Skipping Covid Tracking Proj Race data update.")
            continue
        print(f"\n****START*****\n")
        verify = False
        counter = 1
        while verify is False:
            print(f"~~ Attempt {counter} ~~\n")
            counter = counter + 1
            file = FileFetch(params_file=files[i])
            df = file.fetch()
            verify = file.save(df, fname=fnames[i], fpath=fpaths[i])
            if (counter == 6) and (verify == False):
                print("Additional attempts also failed.  Giving up.\n")
                verify = True
        print(f"\n****END*****\n")

    vdh.clean_vdh("./virginia/*.csv")
