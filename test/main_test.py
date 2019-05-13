import sys
import os
import subprocess
sys.path.append("..")
import planeTypeAPI as api


chrome_path = os.path.abspath(os.path.join(os.getcwd(), '.'))+ "/chromedriver/chromedriver"  


def test_getRouteAware():
    sys.stdout.write(chrome_path)
    # g_version = str(subprocess.check_output(['google-chrome', '--version']))
    # assert g_version[2:len(g_version)-3] == "Google Chrome 74.0.3729.6 dev"
    a = api.api(chrome_path =chrome_path)
    routes = a.getRoutebyAware('SEA','PDX')
    assert len(routes) > 5
    sys.stdout.write(routes[0])

def test_getTypeByID():
    a = api.api(chrome_path =chrome_path)
    planeType = a._getTypeByID('CX712',option=1)
    assert planeType == 'A333' or planeType == 'A359'


