# find other in-house packages in directory path
import os, sys, inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


import os
import pandas as pd
from io import StringIO
from datetime import date
from pprint import pprint

# import packages for hitting websites
import requests
import pyppdf.patch_pyppeteer
from requests_html import HTMLSession
from urllib.parse import unquote

# import Mixins
import _initialize  # hold initialization-checking methods


def checkdir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return


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
        ]  # update with allowed file types as add capability

        # call mixin InitializeCheck class from _initialize.py to make sure user inputs are valid
        # if invalid, returns message letting user know error
        # if all okay, prints url and file type to screen as confirmation
        self.init_check(params, params_file)

        # print to screen confirmation that initialization worked
        print(f"url set to '{self.url}'")
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
                df = self.fetch_html_stream()
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

    def fetch_html_stream(self):

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

        session = HTMLSession()
        r = session.get(self.url)
        r.html.render()
        links = r.html.links

        for link in links:
            if link.startswith(self.key_phrase):
                link = link.lstrip(self.key_phrase)
                stream = unquote(link)
                data = StringIO(stream)
                df = pd.read_csv(data, sep=",")

        return df

    def save(self, df, fname, ftype="csv", fpath="./", index=False):

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

        return


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
    # yaml_file = ["../url_filefetch.yml", "covid_exit_strat_testing"]

    # file = FileFetch(params_file=yaml_file)
    # # file = FileFetch(params)

    # # file.get_description()
    # # file.get_webref()

    # df = file.fetch()
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

    files = [rt_file, tat_file, ces_file, ces_file2, ces_file3]

    fnames = [
        "rtlive",
        "testandtrace",
        "covidexitstrategy",
        "covidexitstrategy",
        "covidexitstrategy",
    ]

    fpaths = [
        "./rt_live",
        "./test_trace",
        "./covid_exit_strategy_testing",
        "./covid_exit_strategy_healthcare",
        "./covid_exit_strategy_spread",
    ]

    for i in range(len(files)):
        print(f"\n****START*****\n")
        file = FileFetch(params_file=files[i])
        df = file.fetch()
        file.save(df, fname=fnames[i], fpath=fpaths[i])
        print(f"\n****END*****\n")
