import sys
import os
import subprocess
from planeTypeAPI import api,convertTimeZone, toepoch, diffdistance
from db import session_factory
from datetime import datetime, date, timedelta
import time
chrome_path = os.path.abspath(os.path.join(os.getcwd(), '.'))+ "/chromedriver/chromedriver"  
a = api(chrome_path =chrome_path)

def test_getRouteAware():
    sys.stdout.write(chrome_path)
    routes = a.getRoutebyAware('LHR','JFK')
    assert 'BAW173' in routes
    sys.stdout.write(routes[0])

def test_getRoutebyStat():
    today = datetime.today().strftime('%Y%m%d')
    today += '18'
    route = a.getRoutebyStat('LHR','JFK',today)
    assert 'BA1593' in route

def test_getTypeByID():
    yesterday = date.today() - timedelta(days=1)
    yesterday = str(yesterday).replace('-','')
    twodaybefore = date.today() - timedelta(days=2)
    twodaybefore = str(twodaybefore).replace('-','')
    y1 = yesterday + '190000'
    y2 = twodaybefore + '190000'
    planeType = a._getTypeByID('BA1419',[y1,y2],option=1)
    assert planeType == 'A320' or planeType == '32N' or planeType == 'A319'
    y3 = yesterday + '184000' 
    planeType = a._getTypeByID('BA1419',[y2,y3])
    assert planeType in ['A320 (G-EUYH)','A320 (G-EUYC)','A320 (G-EUYP)', 'A320 (G-EUYB)', 'A20N (G-TTND)'] 

def test_db():
    session = session_factory()
    cur = session.execute("select icao, latitude, longitude, iata from Airport where iata = 'GKA'")
    cur = cur.fetchone()
    assert cur[0] == 'AYGA'

def test_converttz():
    assert  '20190610091000' in convertTimeZone('10-Jun-2019','04:10PM','+07')
    assert '20190610031000' in convertTimeZone('10-Jun-2019','04:10AM','BST') 

def test_toepochtime():
    assert toepoch('20190614104100') == 1560508860

def test_diffdistance():
    a = diffdistance(23.723789,56.652241,24.105186 ,56.949650)
    b = diffdistance(23.723789,56.652241,23.797649 ,56.972309)
    print(a,b)
    assert a > b





