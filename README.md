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
- [ ] Create API for flightaware
- [x] Create API for flightradar24
- [ ] Create API for 1+ more site
- [x] Create table for airport (number of records: 5958)
- [x] Create table for flight routes (number of records: 1022545)
- [ ] Finish Readme
- [ ] Mapping out flight path? (maybe)
- [ ] Optimize 
- [ ] Documentation
- [ ] Clean code
- [ ] Use official API of flightaware?


### quick start

To use the script in other directory, run the command below:
```
export PYTHONPATH=${PYTHONPATH}:${pwd}
```
To retrieve routes and plane type:
```
from planeTypeAPI import api
a = api()
flightID =  a._getTypeByID('CX19',option=1) # option 1 - flightaware , 0 - flightradar24
routes = a.getRoutebyAware('PDX','SEA') # get routes from flightaware
routestat = a.getRouteByStat('PDX','SEA', 20190510192005) # get routes from flightstats

```

### Acknowledgments
Thank you [@jwagemann](https://github.com/jwagemann) for organize ESOWC event!
