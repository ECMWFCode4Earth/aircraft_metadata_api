import os
import random
import math
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from db import session_factory
import requests
from lxml.html import fromstring
from itertools import cycle


def get_proxies():
    url = ['https://www.us-proxy.org/','https://free-proxy-list.net/']
    response = requests.get(url[1])
    parser = fromstring(response.text)
    proxies = []
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]')[:10]:
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                             i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
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


def toepoch(_date):   # input format 20190501173500
    year = _date[:4]
    month = _date[4:6]
    day = _date[6:8]
    hour = _date[8:10]
    minute = _date[10:12]
    seconds = _date[12:]
    return (datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(seconds)) - datetime.datetime(1970, 1, 1)).total_seconds()


class planeTypeAPI():

    def __init__(self, proxy=False):
        chrome_options = Options()
        chrome_driver = os.getcwd() +"/chromedriver/chromedriver"
        self.useproxy = proxy
        if self.useproxy:
            self.proxies = get_proxies()
            self.proxy_pool = cycle(self.proxies)
            self.proxy = next(self.proxy_pool)
            chrome_options.add_argument('--proxy-server=http://'+ self.proxy)       
            print('connecting on '+ self.proxy)
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument('user-agent='+user_agent)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
        self.wait = WebDriverWait(self.driver, 10)
        self.rotate = random.randint(4,10)

    def checkconn(self,path):
        if self.rotate == 0:
            self.reinit()
            self.rotate = random.randint(4,10)
        self.driver.get(path)
        while 1:
            try:
                _ = requests.get('https://printatestpage.com/', timeout=10)
                break
            except requests.ConnectionError:
                print("proxy error")
                self.reinit()        
        self.driver.get(path)
        while self.driver.current_url != path:
            self.reinit()
        self.rotate -= 1
        return

    def reinit(self):
        self.driver.quit()
        self.proxies.remove(self.proxy)
        if len(self.proxies) == 0:
            self.proxies = get_proxies()
            self.proxy_pool = cycle(self.proxies)
        self.proxy = next(self.proxy_pool)
        print('reconnecting on '+ self.proxy)
        chrome_options = webdriver.ChromeOptions()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument('user-agent='+user_agent)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--proxy-server='+ self.proxy)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=self.chrome_driver)

    def _getTypeByID(self, flightID, _time):
       # first try flightradar24
        s = random.uniform(1.0,5.0)
        print('sleeping for %f seconds'%s)
        time.sleep(s)
        epochtime = toepoch(_time)
        if self.useproxy:
            self.checkconn("https://www.flightradar24.com/data/flights/"+flightID)
        else:
            self.driver.get("https://www.flightradar24.com/data/flights/"+flightID)
        try:
            self.wait.until(lambda driver: self.driver.find_element_by_css_selector('tr[class=" data-row"]').is_displayed())
        except:
            return None
        datarow = self.driver.find_elements_by_css_selector('tr[class=" data-row"]')
        for i in range(len(datarow)):
            try:
                sta = int(datarow[i].find_elements_by_css_selector('td[class="hidden-xs hidden-sm"]')[5].get_attribute("data-timestamp"))
                std = int(datarow[i].get_attribute("data-timestamp"))
            except:
                continue
            if epochtime >= std and epochtime <= sta:
                planeType = datarow[i].find_elements_by_css_selector('td[class="hidden-xs hidden-sm"]')[1].text
                return planeType
        return None

    def get_airport(self, lat1, long1):
        session = session_factory()
        arange = [ int(long1-30), int(long1+30), int(lat1 - 30) , int(lat1+30) ]
        cur = session.execute("select icao, latitude, longitude from Airport where longitude  between %d and %d and latitude between %d and %d"% (arange[0],arange[1],arange[2],arange[3]))
        mini = 9999999999999999
        res = None
        for row in cur:
            tmp = diffdistance(long1,lat1,row[2],row[1])
            if  tmp < mini:
                mini = tmp
                res = row[0]
        return res
    
    def getRoutebyPort(self,arr,dep):
        session = session_factory()
        res = session.execute("select flightid from route where arr='%s' and dep = '%s'"% (arr,dep))
        return [i[0] for i in res]

class routedb():
    def loaddata(self):
        count = 0
        session = session_factory()
        with open('./rawdata/routes.tsv') as fp:
            next(fp)
            for line in fp:
                tmp = line.split('\t')
                if len(tmp[2]) > 2 and len(tmp[4]) > 2:
                    session.execute("insert into Route (flightid, dep,arr) VALUES( '%s' , '%s' , '%s' )" % (tmp[0],tmp[2].replace("'",''),tmp[4].replace("'",'')))
                    count += 1
                    if count % 1000 == 0:
                        try:
                            session.commit()
                            print('successfully inserted 1000 row, total inserted: %d'% count)
                        except:
                            print('error')
                            session.rollback()
                            session.flush()
            session.commit()


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
        a = planeTypeAPI()
        #res = []
        totaline = 0
        testline = 0
        matchline = 0
        for file in os.listdir('./rawdata/amdw'):
            with open('./rawdata/amdw/'+file) as fp:
                for line in fp:
                    tmp = line.split()
                    if tmp[7] != '???' and tmp[8] != '???':
                        testline += 1
                        id = a.getRoutebyPort(tmp[7],tmp[8])
                        tmp1 = None
                        if len(id) != 0:
                            for x in id:
                                print("testing on flightID %s"%x)
                                tmp1 = a._getTypeByID(x,tmp[1]+tmp[2])
                                if tmp1 != None:
                                    id = x
                                    print('match successful %s with %s' %(x,tmp1))
                                    break
                            if tmp1 != None:
                                matchline += 1
                                f = open("text.txt", "a")
                                f.write("%s, %s, %s, %s, %s \n"%(tmp[0], id, tmp1, tmp[7], tmp[8]))
                                f.close()
                    else:
                        print('no matching route')
                    totaline += 1
                    if testline%10 == 0:
                        print('total record: %d, record tested: %d , record matched: %d'%(totaline,testline,matchline))
