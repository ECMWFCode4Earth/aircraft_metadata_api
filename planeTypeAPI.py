import os
import random
import math
from datetime import datetime
import time
import db
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from db import session_factory
import requests

dirpath = os.getcwd()


def reinit():
    db.reinit()
    a = routedb()
    a.loaddata()
    a = airportdb()
    a.loaddata()
    a = planetypedb()
    a.loaddata()

def convertTimeZone(datestr,_time,timezone):
    datestr = [i for i in datestr.split('-')]
    _time = _time.split(':')
    if timezone[0] != '+' and timezone[0] != '-':
        # To do get UTC diff from db
        pass
    else:
        # add or substract hours to UTC 
        if timezone[0] == '+':
            _time[0] = int(_time[0]) + int(timezone[1:])
        elif timezone[0] == '-':
            _time[0] = int(_time[0]) - int(timezone[1:])
        tmptime = str(_time[0])+ ':' +_time[1]
        local_tz = datetime.strptime(tmptime, "%I:%M%p") 
        local_tz = datetime.strftime(local_tz, "%H:%M")
    month = time.strptime(datestr[1],'%b').tm_mon
    if len(str(month)) == 1:
        month = '0'+ str(month)
    date = datestr[2] + month + datestr[0]   + local_tz.replace(':','') 
    if len(date) == 12:
        date += '00'
    return date

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


class flightawareAPI():
    
    def __init__(self,username,apiKey):
        self.username = username
        self.apiKey = apiKey
        self.fxmlUrl = "https://flightxml.flightaware.com/json/FlightXML2/DecodeFlightRoute"

    def enroute(self,flight):
        payload = {'airport':'KSFO', 'howMany':'10'}
        response = requests.get(self.fxmlUrl + "Enroute",
        params=payload, auth=(self.username, self.apiKey))

        if response.status_code == 200:
            print(response.json())
        else:
            print("Error executing request")

class api():
    def __init__(self, chrome_path=os.getcwd() +"/chromedriver/chromedriver"):
        chrome_options = Options()
        self.chrome_driver = chrome_path
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument('user-agent='+user_agent)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=self.chrome_driver)
        self.wait = WebDriverWait(self.driver, 10)
        self.rotate = random.randint(4,10)


    def _getTypeByID(self, flightID, _time=None, option=0):
       # first try flightradar24
        s = random.uniform(1.0,2.0)
        print('sleeping for %f seconds'%s)
        time.sleep(s)
        if option == 0:
            epochtime = toepoch(_time)
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
        elif option == 1:
            self.driver.get("https://flightaware.com/live/flight/%s" % flightID)
            table = self.driver.find_element_by_css_selector('div[id="flightPageActivityLog"]')
            table = table.find_elements_by_css_selector('div[class="flightPageDataTable"]')
            
            table = self.driver.find_elements_by_css_selector('div[class="flightPageDataRowTall "]')
            for row in table:
                try:
                    data = row.find_elements_by_css_selector('div[class="flightPageActivityLogData optional"]')
                    return data[0].text
                except:
                    return None  
        return None

    def get_airport(self, lat1, long1, range=5):
        session = session_factory()
        arange = [ int(long1-range), int(long1+range), int(lat1 - range) , int(lat1+range) ]
        cur = session.execute("select icao, latitude, longitude from Airport where longitude  between %d and %d and latitude between %d and %d"% (arange[0],arange[1],arange[2],arange[3]))
        mini = 9999999999999999
        res = None
        for row in cur:
            tmp = diffdistance(long1,lat1,row[2],row[1])
            if  tmp < mini:
                mini = tmp
                res = row[0]
        return res
    
    def getRoutebyPort(self,dep,arr):
        session = session_factory()
        res = session.execute("select flightid from route where arr='%s' and dep = '%s'"% (arr,dep))
        return [i[0] for i in res]

    def getRoutebyAware(self,dep,arr):  #ICAO
        self.driver.get("https://flightaware.com/live/findflight?origin=%s&destination=%s" % (dep,arr))
        datarow = self.driver.find_elements_by_css_selector('td[class="ffinder-results-ident text_align_left"]')
        routes = set()
        for row in datarow:
            flightID = row.find_element_by_css_selector('a').text
            if len(flightID) > 3:
                routes.add(flightID)
        return list(routes)

    def getRoutebyStat(self,dep,arr,_date): # for hour 0 - 0-6, 6 - 6-12, 12 -12-18, 18 - 0 
        if type(_date) != str:
            _date = str(_date)
        year = int(_date[:4])
        month = int(_date[4:6])
        day = int(_date[6:8])
        hour = int(_date[8:10])
        if hour < 6:
            hour = 0
        elif hour < 12:
            hour = 6
        elif hour < 18:
            hour = 12
        else:
            hour = 18
        _path = "https://www.flightstats.com/v2/flight-tracker/route/%s/%s/?year=%s&month=%s&date=%s&hour=%s"% (dep,arr,year,month,day,hour)
        self.driver.get(_path)
        self.driver.get_screenshot_as_file("capture.png")
        self.wait.until(lambda driver: self.driver.find_element_by_css_selector('div[class="table__Table-s1x7nv9w-6 iiiADv"]').is_displayed())
        table = self.driver.find_element_by_css_selector('div[class="table__Table-s1x7nv9w-6 iiiADv"]')
        datarow = table.find_elements_by_css_selector('div[class="table__TableRowWrapper-s1x7nv9w-9 ggDItd"]')
        routes = set()
        for row in datarow:
            route = row.find_element_by_css_selector('h2[class="table__CellText-s1x7nv9w-15 KlAnq"]').text
            routes.add(route)
        return list(routes)


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
        count = 0
        session = session_factory()
        with open('./rawdata/airports.txt') as fp:
            for line in fp:
                tmp = line.split(',')
                if tmp[4] != "\\N":
                    session.execute("insert into Airport ( iata, icao, latitude,longitude, altitude)\
                                    VALUES( '%s' , '%s', %f , %f, %f)"
                                    %(tmp[4].replace('"', ''),tmp[5].replace('"', ''),
                                    float(tmp[6]),float(tmp[7]),float(tmp[8]))) 
                    count += 1
        try:
            session.commit()
            print('successfully inserted %d row'% count)
        except:
            print('error')
            session.rollback()
            session.flush()


class planetypedb():
    def loaddata(self):
        a = api()
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
    
    def loadAREP(self):
        a = api() 
        totaline = 0
        matched = 0
        flightIDs = set()
        for file in os.listdir('./rawdata/arep'):
            start = time.time()
            with open('./rawdata/arep/'+file) as fp:
                f = open("test_arep1.txt", "a")
                f.write("\n for file %s \n"%file)
                for line in fp:
                    tmp = line.split()
                    totaline += 1
                    if tmp[0][:3].isalpha():
                        flightIDs.add(tmp[0]) 
        for i in list(flightIDs):
            ptype = a._getTypeByID(i,option=1)
            if ptype:
                matched += 1
                f.write("%s  matched with type %s \n"%(i, ptype))
            else:
                print('nothing!')
        end = time.time()
        f.write('total tested: %d, record matched: %d,time taken: %f'
                    %(totaline,matched ,end-start))
        f.close()
