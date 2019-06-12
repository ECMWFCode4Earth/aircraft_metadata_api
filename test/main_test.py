import sys
import os
import subprocess
from planeTypeAPI import api,convertTimeZone
from db import session_factory
from datetime import datetime
import time
chrome_path = os.path.abspath(os.path.join(os.getcwd(), '.'))+ "/chromedriver/chromedriver"  
a = api(chrome_path =chrome_path)

def test_getRouteAware():
    sys.stdout.write(chrome_path)
    # g_version = str(subprocess.check_output(['google-chrome', '--version']))
    # assert g_version[2:len(g_version)-3] == "Google Chrome 74.0.3729.6 dev"
    routes = a.getRoutebyAware('LHR','JFK')
    assert 'BAW173' in routes
    sys.stdout.write(routes[0])

def test_getTypeByID():
    planeType = a._getTypeByID('CX712',option=1)
    assert planeType == 'A333' or planeType == 'A359'

def test_getRoutebyStat():
    today = datetime.today().strftime('%Y%m%d')
    today += '18'
    route = a.getRoutebyStat('LHR','JFK',today)
    assert 'BA 1593' in route

def test_db():
    session = session_factory()
    cur = session.execute("select icao, latitude, longitude, iata from Airport where iata = 'GKA'")
    cur = cur.fetchone()
    assert cur[0] == 'AYGA'

def test_converttz():
    assert convertTimeZone('10-Jun-2019','04:10PM','+07') == '20190610231000'




