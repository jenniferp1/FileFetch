# import os, sys, inspect, site

# currentdir = os.path.dirname(
#     os.path.abspath(inspect.getfile(inspect.currentframe()))
# )
# parentdir = os.path.dirname(currentdir)
# # reqenv = "C:\\Users\\PALGUTAJ\\AppData\\Roaming\\Python\\envs\\req\\Lib\\site-packages"
# # sys.path.insert(0, parentdir)
# # print(site.getsitepackages())

import pyppdf.patch_pyppeteer
from requests_html import HTMLSession
import pandas as pd
from io import StringIO
import requests
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup

import pandas as pd
import io


class FileFetch:
    def __init__(self, url):

        # Internal links are URLs that links to other pages of the same website.
        self.internal_urls = set()
        # External links are URLs that links to other websites.
        self.external_urls = set()

        self.url = url

    def is_valid(self, link):
        """
        Checks whether url link is a valid URL.
        """
        netloc = bool(urlparse(link).netloc)
        scheme = bool(urlparse(link).scheme)

        return (netloc, scheme)

    def get_all_website_links(self):
        """
        Returns all URLs that is found on `url` in which it belongs to the same website
        """
        print(f"\n\tGetting urls from {self.url}\n")  # update user

        # all URLs of `url`
        urls = set()
        # domain name of the URL without the protocol
        self.domain_name = urlparse(self.url).netloc
        soup = BeautifulSoup(requests.get(self.url).content, "html.parser")

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            else:
                # join the URL if it's relative (not absolute link)
                href = urljoin(self.url, href)
                parsed_href = urlparse(href)
                print(href)
                href = (
                    parsed_href.scheme
                    + "://"
                    + parsed_href.netloc
                    + parsed_href.path
                )
                print(href, "\n")


# ff = FileFetch("https://scrapethissite.com")
# ff.get_all_website_links()

# session = requests.session()
# data = session.get ("https://scrapethissite.com").content

# import wget

# print('Beginning file download with wget module')

# url = 'http://i3.ytimg.com/vi/J---aiyznGQ/mqdefault.jpg'
# wget.download(url, '/Users/scott/Downloads/cat4.jpg')


# url = "https://datawrapper.dwcdn.net/owNad/3/#toggle"
# url = "https://datawrapper.dwcdn.net/jxldP/124/"
# url = "https://covidtracking.com/race/dashboard"

# ####
# # covid tracking project testing
# ########
# url = "https://covidtracking.com/data/longtermcare"

# session = HTMLSession()
# r = session.get(url)
# # r.html.render()
# links = r.html.links

# csvs = []
# for link in links:
#     if link.endswith("output=csv"):
#         csvs.append(link)
# print(*csvs, sep="\n")
# # if len(link) > 200:
# #     stream = unquote(link)
# #     data = StringIO(stream)
# #     df = pd.read_csv(data, sep=",")
# #     print(df)

# url = "https://covidactnow.org/us/fl/?s=891176"
url = "https://www.covidexitstrategy.org/"
# https://www.jcchouinard.com/web-scraping-with-python-and-requests-html/
session = HTMLSession()
r = session.get(url)
r.html.render()
# print(r.html.html)

# links = r.html.links


with open("OutputTest.txt", "w", encoding="utf-8") as text_file:
    print(r.html.html, file=text_file)

# print(r.html.full_text)

# container = r.html.find("div.sc-fzoYkl span", first=True)

# print(len(container))

# for link in links:
#     print(f"\n{link}\n")

#####################
# working script
#####################
# link = """data:application/octet-stream;charset=utf-8,State%2CTotal%20Grade%2C%25%20of%20Tests%20Are%20Positive%20(7-Day%20Avg)%2CContact%20Tracers%20%2F%20Daily%20Positive%20Tests%20(7-Day%20Avg)%2C%23%20of%20Contact%20Tracers%2CDaily%20Tests%20(7-Day%20Avg)%2CContact%20Tracers%20%2F%20100k%20Population%2CPlanned%20Number%20of%20Tracers%3F%2C%23%20Contact%20Tracers%20Needed%2CHave%20Enough%20Contact%20Tracers%3F%2CSource%20for%20Contact%20Tracer%20Count%2CSource%20Confidence%0AMassachusetts%2C4.5%2C2.719808751%2C5.358429395%2C2125%2C14580.85714%2C35.14906512%2C2500%2C1982.857143%2C142.1428571%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AMaine%2C4.5%2C0.6766403874%2C5.52293578%2C86%2C2301.285714%2C6.397800347%2C125%2C77.85714286%2C8.142857143%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ANew%20York%2C4.5%2C0.9526855155%2C14.77402369%2C9620%2C68348.14286%2C49.4511005%2C17000%2C3255.714286%2C6364.285714%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AConnecticut%2C4.5%2C0.7336991196%2C10.46956522%2C860%2C11195.71429%2C24.12148026%2C900%2C410.7142857%2C449.2857143%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AVermont%2C4.5%2C0.561465721%2C9.763157895%2C53%2C966.8571429%2C8.493739473%2C53%2C27.14285714%2C25.85714286%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ANew%20Hampshire%2C3.5%2C2.057942058%2C4.247572816%2C125%2C1430%2C9.193130011%2C125%2C147.1428571%2C-22.14285714%2CNews%20Reports%20%2CMedium%0ANew%20Jersey%2C3.5%2C1.600060932%2C2.819480044%2C1100%2C24383%2C12.38433314%2C4000%2C1950.714286%2C-850.7142857%2CNews%20Reports%20%2CMedium%0ADistrict%20of%20Columbia%2C3.5%2C2.004958031%2C4.555314534%2C300%2C3284.714286%2C42.50803048%2C300%2C329.2857143%2C-29.28571429%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AMinnesota%2C2.5%2C-4.56449143%2C1.45432498%2C1028%2C-15486%2C18.22813971%2C1400%2C3534.285714%2C-2506.285714%2CNews%20Reports%20%2CHigh%0AAlaska%2C2.5%2C1.818430782%2C1.813253012%2C172%2C5216.428571%2C23.51188239%2C500%2C474.2857143%2C-302.2857143%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ANew%20Mexico%2C2.5%2C2.708487225%2C1.223776224%2C250%2C7542.428571%2C11.92276528%2C350%2C1021.428571%2C-771.4285714%2CState%2CHigh%0AMichigan%2C2.5%2C2.520682523%2C1.507692308%2C1050%2C27628.57143%2C10.51381831%2C1050%2C3482.142857%2C-2432.142857%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CMedium%0AWest%20Virginia%2C2.5%2C2.856856455%2C1.842105263%2C225%2C4275.428571%2C12.55477369%2C270%2C610.7142857%2C-385.7142857%2CNews%20Reports%20%2CMedium%0ANorth%20Dakota%2C2.5%2C7.387417777%2C2.812785388%2C352%2C1694%2C46.19046744%2C500%2C625.7142857%2C-273.7142857%2CNews%20Reports%20%2CHigh%0ANebraska%2C2%2C8.875815871%2C3.217223029%2C950%2C3326.857143%2C49.1106323%2C1000%2C1476.428571%2C-526.4285714%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ACalifornia%2C2%2C5.132335514%2C1.668240478%2C10600%2C123803.2857%2C26.82714157%2C10600%2C31770%2C-21170%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ASouth%20Dakota%2C2%2C8.133905104%2C4.166666667%2C350%2C1032.714286%2C39.56326675%2C350%2C420%2C-70%2CNews%20Reports%20%2CHigh%0AUtah%2C2%2C10.37583806%2C2.609506058%2C1200%2C4432%2C37.43030944%2C1200%2C2299.285714%2C-1099.285714%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AWashington%2C2%2C9.827692545%2C2.91312022%2C2122%2C7412%2C27.8664454%2C2122%2C3642.142857%2C-1520.142857%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ADelaware%2C2%2C4.884393064%2C1.791420118%2C173%2C1977.142857%2C17.76611171%2C300%2C482.8571429%2C-309.8571429%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AMontana%2C2%2C4.581661725%2C1.421319797%2C160%2C2457%2C14.97036803%2C160%2C562.8571429%2C-402.8571429%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AMaryland%2C1.5%2C5.936277705%2C1.621482498%2C1350%2C14025.14286%2C19.58649855%2C1400%2C4162.857143%2C-2812.857143%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ARhode%20Island%2C1.5%2C5.899678686%2C2.118003026%2C200%2C1600.571429%2C18.87930554%2C200%2C472.1428571%2C-272.1428571%2CNews%20Reports%20%2CHigh%0AVirginia%2C1.5%2C6.966204454%2C1.555220451%2C1547%2C14279.14286%2C18.12426403%2C1770%2C4973.571429%2C-3426.571429%2CNews%20Reports%20%2CHigh%0AOregon%2C1.5%2C6.227879725%2C2.005730659%2C600%2C4803.285714%2C14.22563806%2C800%2C1495.714286%2C-895.7142857%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AKentucky%2C1.5%2C7.279159923%2C1.447776629%2C800%2C7591.142857%2C17.90641347%2C800%2C2762.857143%2C-1962.857143%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHIgh%0AWyoming%2C1.5%2C7.845399481%2C1.286764706%2C50%2C495.2857143%2C8.63917451%2C50%2C194.2857143%2C-144.2857143%2CNews%20Reports%20%2CMedium%0AColorado%2C1.5%2C6.992792516%2C1.151315789%2C525%2C6521%2C9.116583917%2C800%2C2280%2C-1755%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0APennsylvania%2C1%2C5.425962478%2C0.8346500092%2C649%2C14330.57143%2C5.069524743%2C649%2C3887.857143%2C-3238.857143%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AIllinois%2C1%2C4.016291554%2C0.9682718077%2C1600%2C41143.14286%2C12.62644098%2C3898%2C8262.142857%2C-6662.142857%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CMedium%0AOhio%2C1%2C5.175928797%2C0.5621414914%2C630%2C21652.42857%2C5.389636499%2C2000%2C5603.571429%2C-4973.571429%2CNews%20Reports%20%2CHigh%0AWisconsin%2C0.5%2C5.896859867%2C0.7111412123%2C600%2C14307.85714%2C10.30496868%2C1000%2C4218.571429%2C-3618.571429%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AHawaii%2C0.5%2C5.720838377%2C0.6236080178%2C80%2C2242.428571%2C5.650228269%2C320%2C641.4285714%2C-561.4285714%2CNews%20Reports%20%2CHigh%0ALouisiana%2C0.5%2C7.617166521%2C0.2193497846%2C400%2C23940.28571%2C8.604382126%2C631%2C9117.857143%2C-8717.857143%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ANorth%20Carolina%2C0.5%2C6.157619032%2C0.9482525061%2C1500%2C25689.42857%2C14.30194495%2C1500%2C7909.285714%2C-6409.285714%2CNews%20Reports%20%2CHigh%0AIowa%2C0%2C9.767209453%2C0.4213060488%2C200%2C4860.285714%2C6.339003572%2C350%2C2373.571429%2C-2173.571429%2CNews%20Reports%20%2CMedium%0AGeorgia%2C0%2C12.32951416%2C0.3792737405%2C1225%2C26196.14286%2C11.53763959%2C1300%2C16149.28571%2C-14924.28571%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AArkansas%2C0%2C14.19488672%2C0.496868476%2C374%2C5302.714286%2C12.39311764%2C700%2C3763.571429%2C-3389.571429%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AOklahoma%2C0%2C9.492429197%2C0.8655714538%2C700%2C8519.571429%2C17.69029897%2C1000%2C4043.571429%2C-3343.571429%2CNews%20Reports%20%2CHigh%0AArizona%2C0%2C15.55606673%2C0.2157366332%2C396%2C11799.71429%2C5.440519256%2C500%2C9177.857143%2C-8781.857143%2CNews%20Reports%20%2CMedium%20%0ASouth%20Carolina%2C0%2C14.24622417%2C0.5501355014%2C725%2C9250.571429%2C14.0811861%2C1800%2C6589.285714%2C-5864.285714%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0ATexas%2C0%2C16.5304502%2C0.353931164%2C2800%2C47858%2C9.656543976%2C4000%2C39555.71429%2C-36755.71429%2CNews%20Reports%20%2CHigh%0AIdaho%2C0%2C15.87501311%2C0.5779392338%2C250%2C2724.857143%2C13.9894184%2C500%2C2162.857143%2C-1912.857143%2CNews%20Reports%20%2CHigh%0AAlabama%2C0%2C18.1479992%2C0.09695290859%2C150%2C8525.142857%2C3.059235986%2C200%2C7735.714286%2C-7585.714286%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AMissouri%2C0%2C11.23730983%2C0.08716386276%2C94%2C9596.857143%2C1.531586195%2C94%2C5392.142857%2C-5298.142857%2CCompiled%20Local%20Health%20Department%20Numbers%20(No%20Definitive%20State%20Report)%2CLow%0AMississippi%2C0%2C20.88487446%2C0.2052484973%2C200%2C4665.714286%2C6.720093651%2C250%2C4872.142857%2C-4672.142857%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AIndiana%2C0%2C8.412047243%2C0.6074279764%2C500%2C9785.285714%2C7.426971701%2C500%2C4115.714286%2C-3615.714286%2CDirect%20Contact%20With%20State%20or%20State%20Press%20Release%2CHigh%0AFlorida%2C0%2C17.61390999%2C0.2285247909%2C1600%2C39749.42857%2C7.449574413%2C1600%2C35007.14286%2C-33407.14286%2CWTSP-TV%20news%20story%2CMedium%0ATennessee%2C0%2C8.731109801%2C0.382743527%2C737%2C22054.14286%2C10.79193472%2C1300%2C9627.857143%2C-8890.857143%2CNews%20Reports%20%2CHigh%0AKansas%2C0%2C11.97778619%2C0.8826835265%2C359%2C3395.571429%2C12.32273624%2C495%2C2033.571429%2C-1674.571429%2CCompiled%20Local%20Health%20Department%20Numbers%20(No%20Definitive%20State%20Report)%2CMedium%0ANevada%2C0%2C18.42134063%2C0.4158621714%2C400%2C5221.428571%2C12.98635524%2C400%2C4809.285714%2C-4409.285714%2CNews%20Reports%20%2CMedium"""
# key_phrase = "data:application/octet-stream;charset=utf-8,"
# if link.startswith(key_phrase):
#     link = link.lstrip(key_phrase)
#     stream = unquote(link)
#     data = StringIO(stream)
#     df = pd.read_csv(data, sep=",")
#     df.to_csv("testandtrace.csv", index=False)


#################################################################
# url = "https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv"

# # s = requests.get(url).content
# # c = pd.read_csv(s)
# # print(c)

# req = requests.get(url)
# if req.ok:
#     data = req.content.decode("utf8")
#     df = pd.read_csv(io.StringIO(data))
#     df.rename(columns={"region": "state_abbr"}, inplace=True)

#     # print(df.groupby("region").get_group("VA"))

# url2 = "https://raw.githubusercontent.com/kjhealy/fips-codes/master/state_fips_master.csv"
# df2 = pd.read_csv(url2)


# result = pd.merge(
#     df,
#     df2[
#         ["state_name", "state_abbr", "fips", "region_name", "division_name"]
#     ],
#     on="state_abbr",
#     how="left",
# )

# # result.to_csv("rt_test.csv")
# print(result.tail())

