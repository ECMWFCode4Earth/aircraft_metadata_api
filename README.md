Master:
[![Build Status](https://travis-ci.org/esowc/aircraft_metadata_api.svg?branch=master)](https://travis-ci.org/esowc/aircraft_metadata_api/)
Develop branch:
[![Build Status](https://travis-ci.org/esowc/aircraft_metadata_api.svg?branch=develop)](https://travis-ci.org/esowc/aircraft_metadata_api/)

# aircraft_metadata_api

# ESoWC 2019 - Obtaining online aircraft metadata. 

__Team:__ [@michiboo](https://github.com/michiboo)

__Mentor:__ [@BruceIngleby](https://github.com/BruceIngleby), [@MohamedDahoui](https://github.com/MohamedDahoui)

### Summary
The aim of this project is to obtain aircraft metadata for AMDAR data.

### To do
- [x] Create API for flightaware
- [x] Create API for flightradar24
- [ ] Create API for 1+ more site
- [x] Create table for airport (number of records: 5958)
- [x] Create table for flight routes (number of records: 1022545)
- [ ] Finish Readme
- [ ] Optimize 
- [ ] Documentation
- [ ] Clean code
- [ ] Use official API of flightaware?

### manual installation

To install the api manually please follow the steps in .travis.yml

### quick start

It have to use a specific version of chrome, in this case it use version 75, if your chrome version is differnt.
Visit http://chromedriver.chromium.org/downloads to download corresponding chromedriver and put it in chromedriver folder.

To use the script in other directory, run the command below:
```
export PYTHONPATH=${PYTHONPATH}:${pwd}
```
To add it permanently to python path:

run:
``` 
echo 'export PYTHONPATH=$PYTHONPATH:'$PWD >>  ~/.bashrc
source ~/.bashrc
 ```

To retrieve routes and plane type:
```
from planeTypeAPI import api
a = api()
flightID =  a._getTypeByID('CX19',option=1) # option 1 - flightaware , 0 - flightradar24
routes = a.getRoutebyAware('PDX','SEA') # get routes from flightaware
routestat = a.getRouteByStat('PDX','SEA', 20190510192005) # get routes from flightstats

```

To get plane type for AMDAR or AIREP data:
```
1. Place extracted txt files in rawdata/amdw folder

2. Initiate planetypedb()

from planeTypeAPI import planetypedb
a = planetypedb()

3. remove first line of AIREP file (a line with statistic) if exists

a.remove_firstline_arep()

4. filter the data with altitude (default=3000)

a.filterDataByaltitude()

5. get plane type and insert into sqlite database

a.loaddata() 

```

### more quicker start with docker
In the directory run 
```
sudo docker build -t [tag name] .
sudo docker run -it [tag name]

```

### Acknowledgments
Thank you [@jwagemann](https://github.com/jwagemann) for organize ESOWC event!
