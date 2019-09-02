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
    planeType = a._getTypeByID('BA1419',[y1,y2],option=1)[0]
    assert planeType in ['A320','32N','A319']
    y3 = yesterday + '184000' 
    planeType = a._getTypeByID('BAW1419',[y2,y3],option=0)
    assert planeType[:4]  in ['A319','A320','A20N'] or planeType[:3] == '32N'

def test_get_airline_fleet():
    assert ['B-206L', 'Boeing 737 MAX 8', 'B38M'] in a.get_airline_fleet('aq-jyh')

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

def test_distance_diff_airport():
    assert int(a.distance_diff_airport('HKG','LHR',code1='iata',code2='iata')) == 9630
    assert int(a.distance_diff_airport('EDDM','MUC',code1='icao',code2='iata')) < 10




