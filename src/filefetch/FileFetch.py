"""Retrieve file or document from a given url.

When given a set of parameters or yaml file that contain one or more urls,
will navigate to the url and retrieve a file. File may be fetched using one of
several methods.
See :ref:`file_list <ff-attribute-label>` variable for available methods.
Retrieved file contents are saved to a pd.DataFrame with option to export to
a csv.

Classes:
    :class:`FileFetch.FileFetch` - Save data from a given url in a pd.DataFrame or csv

    :class:`_help.Helper` - Print user help information for FileFetch

    :class:`_initialize.InitializeCheck` - Validate user input to FileFetch

    :class:`_validate.ValidateCheck` - Validate data sources before save to DataFrame

Key Variables:
    :ref:`file_list <ff-attribute-label>` - (list) available file retrieval
    method key words (e.g., `csv`, `html-stream`, `findlink`)

    :ref:`file_desc <ff-attribute-label>` - (dict) method defintion and url
    example for each key word listed in file_list

See information on retrieval methods using

>>> python FileFetch.py file_list
Output:
    1. csv: A standard csv file. See 'csv-git-scan'.
            Example: https://www.site.com/myfile.csv
    2. html-stream: Largely used with DataWrapper where octet-stream;charset=utf-8
            Example: https://datawrapper.dwcdn.net/awNod/4/
    3. findlink: For searching html for link to file to download - can retrieve csv, xlsx, or pdf files
            Example: https://www.example.com/data/index.html
    4. findlinks: Same as findlink for multiple files on same page
    5. csv-git-scan: For scanning list of csv files on GitHub and downloading the most recent one. See 'csv'.
            Example: https://github.com/data/tree/master/ListOfFiles

Input Files:
    :ref:`params yaml <ff-note-label1>` - url and retrieval method for FileFetch

    :ref:`pdf_formatter.yml <ff-note-label2>` - information for extracting pdf
    data (must exist in launch directory to retrieve pdf)

.. _FileFetch-label:
"""

"""
############################################
# Set up paths to Modules & add to sys.path
############################################
"""
import sys
from os import scandir
modules = "/home/jennifp3/Documents/Python_scripts/Modules"
excludes = ["__pycache__",".ipynb_checkpoints"] # list of subdirs to ignore
dirls = [f.path for f in scandir(modules) if f.is_dir()]
includes = [d for d in dirls if not any(x in d for x in excludes)]
for d in includes:
    sys.path.insert(0,d)
sys.path.insert(0,modules)

# import standard Python packages
import os
import time
import re
import json
import pandas as pd
from pandas import json_normalize
from io import StringIO
from datetime import date #, datetime
import calendar
from pprint import pprint

# import packages for hitting websites
import requests
from bs4 import BeautifulSoup
# import pyppdf.patch_pyppeteer
from requests_html import AsyncHTMLSession
from urllib.parse import unquote
import urllib3
from urllib3 import request
import certifi

# import Mixins
from filefetch import _initialize  # holds initialization-checking methods
from filefetch import _help    # holds methods for printing help information
from filefetch import _validate # holds methods for validating user specified data sets

# import other homegrown modules
from utilsx.readin import checkdir, get_absolute_path
from utilsx.readin import read_yaml, unicodify, check_last_load
from utilsx.pdfx import parse_pdf



#######################################################
# UPDATE INSTRUCTIONS (if you need to add sources):
# To add a fetch file type to class FileFetch:
# 1a. self.file_list - a list with allowable file types. Add file type to list.
# 1b. self.file_desc - a dictionary with description of allowable file type.
#           Add corresponding descrption when add file type to list
# 2. fetch() - method to download data; has 'if clause' for each file type.
#    Add file type to 'if clause'
# 3. fetch_*() - specific file type method called by fetch().
#    Add a new fetch_*() method for retrieving new file type
#####################################################


class FileFetch(_initialize.InitializeCheck, _help.Helper, _validate.ValidateCheck):
    """Retrieve data file(s) from a url.

    Data is saved in a pd.DataFrame and may also
    be exported to a csv. There are several retrieval methods, which are
    defined in :ref:`file_list <ff-attribute-label>` and
    :ref:`file_desc <ff-attribute-label>`.
    Typical file type for retrieval is
    CSV, but using the findlink(s) option can retrive a PDF or XLSX.
    Additionally, there is a method to return JSON.
    See :ref:`Notes <ff-note-label>` for adding functionality
    to include new file sources or retrieval methods.

    .. _ff-attribute-label:

    Parameters
    ----------
    params : dict, optional
        Provides url and retrieval option; choose either params or params_file.
    params_file : list, optional
        Provides url and retrieval option; preferred over using params.

    Attributes
    ----------
    df : pd.DataFrame
        Contains data returned by the file retrieval method
        (See :ref:`fetch() <fetch-label>`).
    file_list : list
        Provides all available file retrieval method key words.
    file_desc : dict
        Provides method defintion and url example for each key word listed
        in file_list

    See Also
    --------
    :class:`_initialize.InitializeCheck`: Mixin class to verify input to FileFecth.
    :class:`_help.Helper`: Mixin class to provide help information on FileFetch.
    :class:`_validate.ValidateCheck`: Mixin class to validate data sources before save to DataFrame.


    .. _ff-note-label:

    Notes
    -----
    **Extending FileFetch capabilities**:

    * Add fetch method keyword to :ref:`file_list <ff-attribute-label>`.
    * Add a corresponding description to :ref:`file_desc <ff-attribute-label>`
      for method added to file_list
    * Update :ref:`fetch() <fetch-label>` to include addition to file_list
    * Write a :ref:`fetch_*() submethod <subfetch-label>` that will be called by fetch to do the work

    .. note:: A mixin class design is used in building FileFetch attributes. :ref:`ff-reference-label` provides more information on mixins.

    .. role:: hl

    .. _ff-note-label1:

    Recommend using yaml files (see :ref:`ff-example-label`) to provide input
    to :ref:`FileFetch() <FileFetch-label>`.
    Primary :hl:`params yaml` file format is

    **key_word_header**:

        **description**: <*summary for data being retrieved*>

        **website**: <*parent url*>

        **file_url**: <*url to file (may be same as website)*>

        **file_type**: <*e.g., csv, html-stream, findlink*>

        **key_phrase**: <*for html-stream, findlink(s), csv-git-scan; blank otherwise*>

    .. _ff-note-label2:

    .. note:: If retrieving a pdf table -- :hl:`pdf_formatter.yml` is required in your run directory. See :ref:`ff-example-label`.

    The pdf_formatter.yml structure is

    **url_key_header**:

      **description**: <*summary for data table being extracted from pdf*>

      **notes**: (optional) <*any additional notes on use, may leave blank*>

      **function**: <*name of function to use for extracting and formatting data tables*>

    .. _ff-reference-label:

    References
    ----------
    `Making Python classes more modular using mixins <https://www.residentmar.io/2019/07/07/python-mixins.html>`_

    `Multiple inheritance and mixin classes in Python <https://www.thedigitalcatonline.com/blog/2020/03/27/mixin-classes-in-python/>`_

    .. _ff-example-label:

    Examples
    --------
    For additional help and information on :ref:`FileFetch() <FileFetch-label>`:

    >>> python FileFetch.py file_list
    >>> python FileFetch.py doc
    >>> python FileFetch.py help

    Basic setup and usage:

    >>> yaml_file = ["url_list.yml", "header_key"]
    >>> file = FileFetch(params_file=yaml_file)
    >>> df = file.fetch()
    >>> print(df.head())
    >>> file.save(df, fname="mydata", fpath="./")

    Sample yaml file for primary input to :ref:`FileFetch() <FileFetch-label>`:

    .. code-block:: text

        data_in_csv:
            description: data stored in a csv
            website: https://example.com
            file_url: https://example.com/xyz/data.csv
            file_type: csv
            key_phrase:
        data_from_html_stream:
            description: data from DataWrapper
            website: https://example.com/state-data/
            file_url: https://datawrapper.setxs.net/owNad/2/
            file_type: html-stream
            key_phrase: data:application/octet-stream;charset=utf-8,
        finding_data_download_link:
            description: programmatically find data file download link in html
            website: https://example.com/
            file_url: https://example.com/xyz/dashboard
            file_type: findlink
            key_phrase: {"tag":"main","search":{"id":"main"},"ftype":"csv","nested":"yes"}
        searching_list_of_csvs:
            description: get most recent csv from a list
            website: https://www.example.org/data/issue-brief/state-data/
            file_url: https://github.com/MyData/2020-Data/tree/my_master/StateDataActions/
            file_type: csv-git-scan
            key_phrase: {"pattern":"\\d{4}-\\d{2}-\\d{2}", "last_date":"2020-08-31"}

    Sample pdf_formatter.yml required for fetching data from PDFs:

    .. code-block:: text

        https://www.your_pdf_url/data/xyz/stats/index.html:
            description: pdf data table on test results
            notes: last function argument is page(s) with data table(s), e.g., 1 or 1,2,3
            function: dframe = call_parse_pdf_weekly_report(pdf_name, txt, 7)
    """

    def __init__(self, params=None, params_file=None):

        # params is user supplied dictionary: url and file type (e.g., csv, text, html-stream)
        # params_file = list: location of yaml & header to grab

        self.file_list = [
            "csv",
            "html-stream",
            "findlink",
            "findlinks",
            "csv-git-scan",
            "json",
        ]  # update with allowed file types as add capability

        self.file_desc = {
            "csv":"A standard csv file. See 'csv-git-scan'.\n\
            Example: https://www.site.com/myfile.csv\n",
            "html-stream":"Largely used with DataWrapper where octet-stream;charset=utf-8\n\
            Example: https://datawrapper.dwcdn.net/awNod/4/\n",
            "findlink":"For searching html for link to file to download - can retrieve csv, xlsx, or pdf files\n\
            Example: https://www.example.com/data/index.html\n",
            "findlinks":"Same as findlink for multiple files on same page\n",
            "csv-git-scan":"For scanning list of csv files on GitHub and downloading the most recent one. See 'csv'.\n\
            Example: https://github.com/data/tree/master/ListOfFiles\n",
            "json":"Save json to DataFrame.\n\
            Example: https://api.data.uni.edu/epidata/api.php?source=datacast\n",
        } # update when add to file_list

        # call mixin InitializeCheck class from _initialize.py to make sure user inputs are valid
        # if invalid, returns message letting user know error
        # if all okay, prints url and file type to screen as confirmation
        self.init_check(params, params_file)

        # print to screen confirmation that initialization worked
        if self.url:
            print(f"\n\turl set to '{self.url}'")
        if self.file_type:
            print(f"\tfile type to download is '{self.file_type}'")
        if self.key_phrase:
            print(f"\tkey_phrase is '{self.key_phrase}'")

        return

    def get_description(self):
        """Print user supplied description from yaml.

        In the params_file yaml, user supplies a description of the dataset.
        This method returns the user's description.

        Parameters
        ----------
        None

        Returns
        -------
        None
            User-provided description prints to screen.
        """

        if self.desc:
            print(f"data description: {self.desc}")
        else:
            print("No description provided by user")

        return

    def get_webref(self):
        """Print user supplied parent url from yaml.

        In the params_file yaml, user supplies a parent url if available.
        This method returns that reference.

        Parameters
        ----------
        None

        Returns
        -------
        None
            User-provided parent url prints to screen.

        """

        if self.webref:
            print(f"reference site url: {self.webref}")
        else:
            print("No reference site provided by user")

        return

    def fetch(self):
        """Master method to retrieve data.

        Based on `file_type` provided to :ref:`FileFetch() <FileFetch-label>`
        in `params_file` or `params`,
        will call the correct :ref:`fetch sub-method <subfetch-label>`
        to process the fetch request.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.

        .. _ff-filelist-cmd:

        More information on file_list
        options can be found using the command:

        .. code-block:: python

            > python FileFetch.py file_list

        Parameters
        -----------
        None

        Returns
        --------
        pd.DataFrame
            Data retrieved from file.

        Examples
        --------
        .. code-block:: python

            > file = FileFetch(params_file=your_yaml_list)
            > df = file.fetch()


        .. _subfetch-label:

        """

        # if you need to add a file_type add it to if clause below
        # and then create a new "fetch" method to download the data
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
                    if self.file_ext == "xlsx":
                        df = pd.read_excel(doc_url)
                    if self.file_ext == "pdf":
                        front = re.findall(r"(?<=\/\/).*?(?=\/)", doc_url)[0]
                        front = front.replace("www.","")
                        front = front.replace(".","-")
                        back = re.findall(r"([^\/]+$)", doc_url)[0]
                        curdir = os.getcwd()
                        pdf_name = f"{curdir}/{front}_{back}"
                        self.download_pdf(doc_url, pdf_name)
                        df = parse_pdf(self.url, txt, pdf_name)

                else:
                    print("Error: findlink did not return a document link\n")
                    df = pd.DataFrame()

            if self.file_type == "findlinks":
                doc_urls, txts = self.fetch_links()
                df_list = []
                if doc_urls:
                    print("\tSearched for multiple links and found the following:")
                    for doc_url in doc_urls:
                        if self.file_ext == "csv":
                            df = self.fetch_csv_stream(doc_url)
                            df_list.append(df)
                            print(f"\t{doc_url}")
                    print("")
                    df = df_list
                    df_list = []

                else:
                    print("\tError: findlinks did not return any document links\n")
                    df = pd.DataFrame()

            if self.file_type == "csv-git-scan":
                df = self.fetch_csv_git_scan()

            if self.file_type == "json":
                data = self.fetch_json()

                # If no json retrieved, return empty DataFrame
                if not data:
                    df = pd.DataFrame()
                # Otherwise convert json to DF
                else:
                    # get validator name supplied by user in params
                    validator = self.key_phrase.get("validator")
                    checkdata_key, results_key = self.key_phrase.get("keys")

                    # convert json data to DataFrame using
                    # (1) validator or (2) direct conversion (no data validation)
                    if validator:
                        df = self.choose_validator(data)    # validate than covnert
                    else:
                        df = self.json2df(data, results_key) # direct conversion

        else:
            # pp = pprint.PrettyPrinter(indent=1)
            if self.file_type:
                print(
                    f"\nError: currently no capability to download file type: {self.file_type}"
                )
            else:
                print("\nError: no file type was provided.")
            print(f"Allowable file types are:  ")
            pprint(self.file_list, width=5)
            print("Exiting....")
            exit()

        print("\tData fetched! Saved to DataFrame.\n")

        return df

    def fetch_csv(self):
        """Sub-method to retrieve data.

        An auxiliary function called by  :ref:`fetch() <fetch-label>`.
        Specifically processes fetch requests for `file_type` of csv.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.  More information on file_list
        options can be found using :ref:`this command <ff-filelist-cmd>`.

        Parameters
        ------------
        None

        Returns
        ----------
        pd.DataFrame
            Data retrieved from file.
        """

        if self.file_type != "csv":
            print(
                f"\nError: called function to fetch csv but your file type is: {self.file_type}"
            )
            print("Exiting....")
            exit()

        print("\tFetching file...\n")

        time.sleep(1)

        try:
            req = requests.get(self.url)
            if req.ok:
                rawdata = req.content
                data = unicodify(rawdata)
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

    def fetch_csv_stream(self, doc_url):
        """Sub-method to retrieve data.

        An auxiliary function called by  :ref:`fetch() <fetch-label>`.
        Specifically processes fetch requests for `file_type` of finklink(s).

        The findlink option can process various file types (e.g., csv,
        xlsx, pdf). This function processes csv file types.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.  More information on file_list
        options can be found using :ref:`this command <ff-filelist-cmd>`.

        Parameters
        ------------
        None

        Returns
        ----------
        pd.DataFrame
            Data retrieved from file.
        """

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

    def fetch_csv_git_scan(self):
        """Sub-method to retrieve data.

        An auxiliary function called by  :ref:`fetch() <fetch-label>`.
        Specifically processes fetch requests for `file_type` of csv_git_scan.

        Use this option to scan a list of csv files on GitHub and
        only download the most recent one. If you previously downloaded the
        most recent file, a message telling you so will be returned instead of
        a DataFrame.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.  More information on file_list
        options can be found using :ref:`this command <ff-filelist-cmd>`.

        Parameters
        ------------
        None

        Returns
        ----------
        pd.DataFrame
            Data retrieved from file.
        """

        if self.file_type != "csv-git-scan":
            print(
                f"\nError: called function to fetch csv-git-scan but your file type is: {self.file_type}"
            )
            print("Exiting....")
            exit()

        print("\tFetching file...\n")

        self.url = check_last_load(self.url, self.key_phrase)

        if self.url:
            print(f"\n\t*** UPDATED URL FOUND for {self.desc}")
            urlx = self.url.split('/')[self.url.count('/')]
            print(f"\t    {urlx} ***\n")
            self.file_type = "csv"
            df = self.fetch_csv()
            return df

        last_date = self.key_phrase["last_date"]
        return f"\tYou have the most recent version of data: {last_date}"

    async def fetch_html_stream(self):
        """Sub-method to retrieve data.

        An auxiliary function called by  :ref:`fetch() <fetch-label>`.
        Specifically processes fetch requests for `file_type` of html_stream.

        Use this option when the data is streamed as `octet-stream;charset=utf-8`.
        Largely used with DataWrapper data downloads. This method provides the rendered
        HTML. A call to `link_to_df()` is required afterwards
        to convert the HTML to a DataFrame.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.  More information on file_list
        options can be found using :ref:`this command <ff-filelist-cmd>`.

        Parameters
        ------------
        None

        Returns
        ----------
        str
            Rendered HTML from url.

        See Also
        ----------
        FileFetch.link_to_df
        """

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

        print("\tFetching file...\n")
        # TODO modify call to this method so requires input: key_phrase

        r = await self.session.get(self.url)
        await r.html.arender(wait=3.0, timeout=5.0)

        return r

    def fetch_link(self):
        """Sub-method to retrieve data.

        An auxiliary function called by  :ref:`fetch() <fetch-label>`.
        Specifically processes fetch requests for `file_type` of finklink.

        The findlink option searches the url's html to find a downloadable
        file's link.  The link can point to various file types (e.g., csv,
        xlsx, pdf). The returned link will be used to retrieve the data.
        The subsquent retrieval method will depend on the file type.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.  More information on file_list
        options can be found using :ref:`this command <ff-filelist-cmd>`.

        Parameters
        ------------
        None

        Returns
        ----------
        str
            Document link.
        str
            Any associated text describing the link contents.

        See Also
        ----------
        FileFetch.fetch_links
        """

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

        print("\tFetching link...\n")

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
                            doc = get_absolute_path(self.url, doc)
                        return doc, txt
        else:
            for self.tag in whole_section:
                doc = self.tag.get("href")
                txt = str(self.tag.text)
                if doc.lower().endswith(self.file_ext):
                    if not doc.startswith("http"):
                        doc = get_absolute_path(self.url, doc)
                    return doc, txt

        return None, None


    def fetch_json(self):
        """Sub-method to retireve data.

        An auxiliary function called by  :ref:`fetch() <fetch-label>`.
        Specifically processes fetch requests for `file_type` of json.

        Parameters
        ------------
        None

        Returns
        ----------
        pd.DataFrame
            Data retrieved from file.
        """

        if self.file_type != "json":
            print(
                f"\nError: called function to fetch json but your file type is: {self.file_type}"
            )
            print("Exiting....")
            exit()

        # checkdata_key: (1) used to verify successfully got data and
        # results_key: (2) key in json used to identify lists of results for df
        checkdata_key, results_key = self.key_phrase.get("keys")

        # how many retries if first fetch fails
        attempts = self.key_phrase.get("attempts")

        print("\tFetching file...\n")

        time.sleep(1)

        # handle certificate verification and SSL warnings
        http = urllib3.PoolManager(
           cert_reqs='CERT_REQUIRED',
           ca_certs=certifi.where())

        # get data from the API
        success = False
        try:
            r = http.request('GET', self.url, retries=attempts)
            success = True

        except urllib3.exceptions.HTTPError as e:
            print(f"\n\t ***Warning: Call failed.")
            print(f"\t Error code: {e.reason}")
        except urllib3.exceptions.TimeoutError as e:
            print(f"\n\t ***Warning: Call failed.")
            print(f"\t Error code: {e.reason}")
        except urllib3.exceptions.RequestError as e:
            print(f"\n\t ***Warning: Call failed.")
            print(f"\t Error code: {e.reason}")
        except urllib3.exceptions.NewConnectionError as e:
            print(f"\n\t ***Warning: Call failed.")
            print(f"\t Error code: {e.reason}")

        if not success:
            print("\n\t ***Error: Call failed. Empty data returned.\n")
            return None

        if checkdata_key in r.data.decode("utf-8"):
            data = json.loads(r.data.decode("utf-8"))
        else:
            print("\n\t ***Error: Wrong data format found. Check URL. Empty data returned.\n")
            return None

        return data


    def fetch_links(self):
        """Sub-method to retrieve data.

        An auxiliary function called by  :ref:`fetch() <fetch-label>`.
        Specifically processes fetch requests for `file_type` of finklinks.

        The findlinks option searches the url's html to find two or more downloadable
        file links.  The links can point to various file types (e.g., csv,
        xlsx, pdf). The returned links will be used to retrieve the data.
        The subsquent retrieval method will depend on the file types.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.  More information on file_list
        options can be found using :ref:`this command <ff-filelist-cmd>`.

        Parameters
        ------------
        None

        Returns
        ----------
        list
            Document links.
        list
            Any associated text describing the contents of the links.

        See Also
        ----------
        FileFetch.fetch_link
        """

        if self.file_type != "findlinks":
            print(
                f"\nError: called function to fetch findlinks but your file type is: {self.file_type}"
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

        print("\tFetching links...\n")

        req = requests.get(self.url)
        soup = BeautifulSoup(req.content, 'html.parser')

        whole_section = soup.find_all(self.tag, self.search)

        docs = []
        txts = []

        if self.tag2:
            for section in whole_section:
                nested_tag = section.find_all("a")
                for link in nested_tag:
                    doc = link.get("href")
                    txt = str(link.text)
                    if doc.lower().endswith(self.file_ext):
                        if not doc.startswith("http"):
                            doc = get_absolute_path(url, doc)
                        docs.append(doc)
                        txts.append(txt)
                return docs, txts
        else:
            for self.tag in whole_section:
                doc = self.tag.find("a").get("href")
                txt = str(self.tag.find("a").text)
                if doc.lower().endswith(self.file_ext):
                    if not doc.startswith("http"):
                        doc = get_absolute_path(self.url, doc)
                    docs.append(doc)
                    txts.append(txt)
                return docs, txts

        return None, None


    def json2df(self, data, key):
        """Convert JSON to pd.DataFrame.

        Given a json data and the data results key, will convert
        JSON to a DataFrame.

        Parameters
        -----------
        data : dict
            JSON data.
        key: str
            Dictionary key for results list in json

        Returns
        --------
        pd.DataFrame
            Data retrieved from JSON.
        """

        try:
            df = pd.json_normalize(data, key)
        except:
            print("\n\t***Error: JSON to DataFrame conversion failed.\n")
            df = pd.DataFrame()

        return df


    def link_to_df(self, results):
        """Sub-method called after fetch_html_stream.

        An auxiliary function called by fetch(). Specifically processes fetch
        requests for file_type of html_stream.

        Must be called after
        `fetch_html_stream` to process the rendered HTML into a DataFrame.
        Available `file_type` keyword options are listed in
        :ref:`file_list <ff-attribute-label>`.  More information on file_list
        options can be found using :ref:`this command <ff-filelist-cmd>`.

        Parameters
        ------------
        None

        Returns
        ----------
        pd.DataFrame
            Data retrieved from file.


        See Also
        ----------
        FileFetch.fetch_html_stream()

        """

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
        """Download and save a pdf locally.

        An auxiliary function called by :ref:`fetch() <fetch-label>`.

        Parameters
        -----------
        pdf_url : str
            url pointing to a downloadable pdf.
        pdf_name : str
            file name under which to save pdf.

        Returns
        --------
        None
            Confirmation message with file name printed to screen.


        .. _fetch-label:

        """

        response = requests.get(pdf_url)

        with open(pdf_name, "wb") as p:
            p.write(response.content)

        return print(f"\tpdf saved as {pdf_name}\n")

    def save(self, df, fname, ftype="csv", fpath="./", index=False):
        """Save pd.DataFrame to csv.

        Parameters
        -----------
        df : pd.DataFrame
            DataFrame to be saved to csv.
        fname : str
            File name to save DataFrame to.
        ftype : str, optional
            File type to save DataFrame to. Default is csv. Options: ('csv', 'excel')
        fpath : str, optional
            File path to save DataFrame to. Default is run directory.
        index : bool, optional
            Whether to include index in saved file. Default is False.

        Returns
        -----------
        bool
            True if file successfully saved, False otherwise.
        """

        if isinstance(df, pd.DataFrame):
            if df.size == 0:
                print("\n\t*** WARNING *** DataFrame is empty. Trying again.\n")
                return False
        else:
            print(f"\tNot a DataFrame for {fname}. Skipping save.")
            print(df) # print message providing latest version date
            return True

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

        print(f"\tFile saved to:\t{full_path}\n")

        return True


if __name__ == "__main__":
    # execute only if run as a script

    if len(sys.argv) == 1:
        print("\n    No agruments given.  For help or information try:")
        file = FileFetch(params={"url":"","file_type":"","key_phrase":""})
        file.help_opts()
    elif len(sys.argv) > 2:
        print("\n    Too many arguments. For help or information try:")
        file = FileFetch(params={"url":"","file_type":"","key_phrase":""})
        file.help_opts()
    else:
        if sys.argv[1] == "file_list":
            file = FileFetch(params={"url":"","file_type":"","key_phrase":""})
            file.file_info()
        elif sys.argv[1] == "doc":
            print(FileFetch.__doc__)
        elif sys.argv[1] == "help":
            print("\n\tHit Ctrl+Z to EXIT Help on class FileFectch...\n\
        Processing, please wait...\n")
            time.sleep(3)
            print(help(FileFetch))
        else:
            print("\n    Unrecognized argument. For help or information try:")
            file = FileFetch(params={"url":"","file_type":"","key_phrase":""})
            file.help_opts()

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
    # yaml_file = ["../../url_filefetch.yml", "minnesota"] # Uncomment
    #
    # file = FileFetch(params_file=yaml_file) # Uncomment
    # file = FileFetch(params)

    # file.get_description()
    # file.get_webref()

    # df = file.fetch() # Uncomment
    # print(df.head())

    # i = 0
    # fnames=["hhs_table1", "hhs_table2", "hhs_table3"]
    # fpaths=["./hhs_icu", "./hhs_icu", "./hhs_icu"]
    # if isinstance(df, list):
    #     for table in df:
    #         verify = file.save(table, fname=fnames[i], fpath=fpaths[i])
    #         i += 1
    #         # print(verify)
    #
    # print("DONE")
    # # print(df.dtypes)

    # file.save(df, fname="testrun", fpath="./") # Uncomment

    # # MINNESOTA TESTING
    # url = "https://www.health.state.mn.us/diseases/coronavirus/stats/index.html"
    # txt = "Weekly COVID-19 Report: 9/10/2020 (PDF)"
    # pdf_name = "/home/jennifp3/Documents/Python_scripts/filefetch/health-state-mn-us_covidweekly37.pdf"
    #
    # df = parse_pdf(url, txt, pdf_name)
    # print(df.head())

    # TODO throw specified error (code) if url connection has a problem
    # TODO merge, drop columns, calculate 7-day moving average positivity,
    # TODO 7-day moving average for new cases, 14-day % change
    # TODO post-processor to clean up files (e.g., change dtypes, header names, merges/joins)
    # TODO Load to database - combine with supercharge package

    # TODO move methods external to class to util.py

    # TODO: add csv-googledocs for covid tracking project
    # TODO: add ability to append a date for reading github JHU
