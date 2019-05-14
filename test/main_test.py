import sys
import os
import subprocess
from planeTypeAPI import api
from db import session_factory
chrome_path = os.path.abspath(os.path.join(os.getcwd(), '.'))+ "/chromedriver/chromedriver"  


def test_getRouteAware():
    sys.stdout.write(chrome_path)
    # g_version = str(subprocess.check_output(['google-chrome', '--version']))
    # assert g_version[2:len(g_version)-3] == "Google Chrome 74.0.3729.6 dev"
    a = api(chrome_path =chrome_path)
    routes = a.getRoutebyAware('SEA','PDX')
    assert len(routes) > 5
    sys.stdout.write(routes[0])

def test_getTypeByID():
    a = api(chrome_path =chrome_path)
    planeType = a._getTypeByID('CX712',option=1)
    assert planeType == 'A333' or planeType == 'A359'


def test_db():
    session = session_factory()
    cur = session.execute("select icao, latitude, longitude, iata from Airport where iata = 'GKA'")
    cur = cur.fetchone()
    assert cur[0] == 'AYGA'



