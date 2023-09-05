# yaschedule

Lib for getting schedule data from Yandex.Rasp API:
https://yandex.ru/dev/rasp/doc

<a target="new" href="https://pypi.python.org/pypi/yaschedule"><img border=0 src="https://img.shields.io/badge/python-3.9+-blue.svg?style=flat" alt="Python version"></a>
<a target="new" href="https://pypi.python.org/pypi/yaschedule"><img border=0 src="https://img.shields.io/pypi/v/yaschedule.svg?maxAge=60%" alt="PyPi version"></a>

## Quick Start
### Init
```python
from yaschedule.core import YaSchedule

# TO GET TOKEN - https://yandex.ru/dev/rasp/doc/concepts/access.html
TOKEN = 'some string' 


yaschedule = YaSchedule(TOKEN)
```

### [optional] requests caching
See more at [requests_cache](https://requests-cache.readthedocs.io/) docs
```python
print(yaschedule.session.settings.expire_after) # get particular cache setting
yaschedule.session.settings.expire_after = 600 # set particular cache setting

print(yaschedule.session.settings) # get all cache settings as object of <class 'requests_cache.policy.settings.CacheSettings'>
print({ a : getattr(yaschedule.session.settings, a) for a in dir(yaschedule.session.settings) if not a.startswith('_') }) # get all cache settings as dict

```

### Usage
```python

# get all stations in json 
yaschedule.get_all_stations() # !!! The size of the returned data is about 40 MB

# cities and stations codes from yaschedule.get_all_stations()
city_1 = 'c213' # Moscow
city_2 = 'c2' # Saint-Petersburg
station_1 = 's9600366' # Pulkovo
station_2 = 's9600213' # Sheremetevo

# get station schedule
yaschedule.get_station_schedule(station=station_1)

# get schedule between two stations
yaschedule.get_schedule(from_station=station_1, to_station=station_2)

# get schedule between two cities
yaschedule.get_schedule(from_station=city_1, to_station=city_2)

# get schedule between city and station
yaschedule.get_schedule(from_station=city_1, to_station=station_1)

# u can also specify other request params of request
# transport_type by default get all transport types
yaschedule.get_schedule(from_station=city_1, to_station=city_2, transport_types='train')
yaschedule.get_schedule(from_station=city_1, to_station=city_2, transport_types='plane')
# transfers by default: False
yaschedule.get_schedule(from_station=city_1, to_station=city_2, transfers=True)
```
