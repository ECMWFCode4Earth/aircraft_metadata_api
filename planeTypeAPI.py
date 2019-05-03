import os
# import random
import math
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from db import session_factory
import requests
from lxml.html import fromstring
from itertools import cycle


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                             i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


def diffdistance(long1, lat1, long2, lat2):
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    r = 6371e3
    latdiff = math.radians(lat1-lat2)
    longdiff = math.radians(long1-long2)
    a = math.sin(latdiff/2) * math.sin(latdiff/2) + math.cos(lat1) * math.cos(lat2) *  \
        math.sin(longdiff / 2) * math.sin(longdiff/2)
    c = math.atan2(math.sqrt(a), math.sqrt(1-a))
    return r * c


def execute_sql(sql):
    session = session_factory()
    session.execute(sql)
    try:
        session.commit()
    except:
        session.rollback()
        session.flush()


def toepoch(_date):   # input format 20190501173500
    year = _date[:4]
    month = _date[4:6]
    day = _date[6:8]
    hour = _date[8:10]
    minute = _date[10:12]
    seconds = _date[12:]
    return (datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(seconds)) - datetime.datetime(1970, 1, 1)).total_seconds()


class planeTypeAPI():

    def __init__(self, proxy=True):
        chrome_options = Options()
        chrome_driver = os.getcwd() +"/chromedriver/chromedriver"
        if proxy:
            proxies = get_proxies()
            self.proxy_pool = cycle(proxies)
            chrome_options.add_argument('--proxy-server=http://'+ next(self.proxy_pool))
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument('user-agent='+user_agent)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
        self.wait = WebDriverWait(self.driver, 5)

    def reinit(self):
        self.driver.quit()
        chrome_options = webdriver.ChromeOptions()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument('user-agent='+ user_agent)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--proxy-server='+ next(self.proxy_pool))
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)


    # def getPlaneType():
    #     time.sleep(random.uniform(0.1, 0.5))
    #     if flightID == None and dport == None or aPort == None:
    #         raise Exception('x should not exceed 5. The value of x was: {}'.format(x))

    def _getTypeByID(self, flightID, departure=None):
        # first try flightradar24
        self.driver.get("https://www.flightradar24.com/data/flights/"+flightID)
        while self.driver.current_url != "https://www.flightradar24.com/data/flights/":
            self.reinit()
        datarow = self.driver.find_elements_by_css_selector('tr[class=" data-row"]')
        res = None
        if len(datarow) > 0:
            if departure:
                mini = 9999999999999999999  # maximum value
                for i in range(len(datarow)):
                    tmp = abs(int(datarow[i].get_attribute("data-timestamp")) - departure)
                    if tmp < mini:
                        res = i
                        mini = tmp
            else:
                res = 0
            print(res)
            print(datarow)
            return datarow[res].find_elements_by_css_selector('td[class="hidden-xs hidden-sm"]')[1].text
        return None

    def get_airport(self, lat1, long1):
        session = session_factory()
        arange = [int(long1-30), int(long1+30), int(lat1-30), int(lat1+30)]
        cur = session.execute("select icao, latitude, longitude from Airport where longitude  between %d and %d and latitude between %d and %d"
                              % (arange[0], arange[1], arange[2], arange[3]))
        mini = 9999999999999999
        res = None
        for row in cur:
            tmp = diffdistance(long1, lat1, row[2], row[1])
            if tmp < mini:
                mini = tmp
                res = row[0]
        return res

    def getTypeByPort(self, dep, arr, year, month, day, hour):  # for hour 0 - 0-6, 6 - 6-12, 12 -12-18, 18 - 0
        #  flightstats
        _path = "https://www.flightstats.com/v2/flight-tracker/route/%s/%s/?year=%s&month=%s&date=%s&hour=%s" % (dep, arr, year, month, day, hour)
        self.driver.get(_path)
        while self.driver.current_url != _path:
            self.reinit()
            self.driver.get(_path)
        datarow = self.driver.find_element_by_css_selector('div[class="table__Table-s1x7nv9w-6 iiiADv"]')
        datarow = datarow.find_elements_by_css_selector('div[class="table__TableRowWrapper-s1x7nv9w-9 ggDItd"]')
        departure = datarow[0].find_element_by_css_selector('div[class="table__Cell-s1x7nv9w-13 cPfMpR"]')
        departure = departure.find_element_by_tag_name("h2").text


class routedb():
    def loaddata(self):
        with open('./rawdata/routes.tsv') as fp:
            next(fp)
            for line in fp:
                tmp = line.split('\t')
                self.insert(tmp[0], tmp[2], tmp[4])

    def insert(self, id, dep, arr):
        execute_sql("insert into Route (flightid, dep,arr) \
                    VALUES( '%s', '%s', '%s' )" 
                    % (id, dep, arr))


class airportdb():
    def loaddata(self):
        with open('./rawdata/airports.txt') as fp:
            for line in fp:
                tmp = line.split(',')
                if tmp[4] != "\\N":
                    self.insert(tmp[4].replace('"', ''),
                                float(tmp[6]), float(tmp[7]))

    def insert(self, icao, lat, longti):
        execute_sql("insert into Airport (icao, latitude,longitude)\
                    VALUES( '%s' , %f , %f )"
                    % (icao, lat, longti))


class planetypedb():
    def loaddata(self):
        for file in os.listdir('./rawdata/amdw'):
            with open('./rawdata/amdw/'+file) as fp:
                for line in fp:
                    tmp = line.split()
                    if tmp[7] != '???' and tmp[8] != '???':
                        # if dep and arr is present call getTypeByPort
                        pass

    def insert(self, amdarid, deptime, arrtime,
               deplat, deplong, arrlat, arrlong):
        execute_sql("insert into Planetype (amdarid, deptime, \
                    arrtime,deplat, deplong,arrlat,arrlong) \
                    VALUES( '%s' , %d , %d, %f , %f , %f, %f )"
                    % (amdarid, deptime, arrtime, deplat,
                       deplong, arrlat, arrlong))
