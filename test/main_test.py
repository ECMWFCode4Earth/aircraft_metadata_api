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
    assert 'BA 1593' in route

def test_getTypeByID():
    yesterday = date.today() - timedelta(days=1)
    yesterday = str(yesterday).replace('-','')
    y1 = yesterday + '190000'
    y1 = toepoch(y1)
    planeType = a._getTypeByID('BA1419',y1,option=1)
    assert planeType == 'A320' or planeType == '32N' or planeType == 'A319'
    y2 = yesterday + '184000' 
    y2 = toepoch(y2)
    planeType = a._getTypeByID('BA1419',y2)
    assert planeType in ['A320 (G-EUYH)','A320 (G-EUYC)'] 

def test_db():
    session = session_factory()
    cur = session.execute("select icao, latitude, longitude, iata from Airport where iata = 'GKA'")
    cur = cur.fetchone()
    assert cur[0] == 'AYGA'

def test_converttz():
    assert convertTimeZone('10-Jun-2019','04:10PM','+07') == '20190610091000'
    assert convertTimeZone('10-Jun-2019','04:10AM','BST') == '20190610031000'

def test_toepochtime():
    assert toepoch('20190614104100') == 1560508860

def test_diffdistance():
    a = diffdistance(23.723789,56.652241,24.105186 ,56.949650)
    b = diffdistance(23.723789,56.652241,23.797649 ,56.972309)
    print(a,b)
    assert a > b





