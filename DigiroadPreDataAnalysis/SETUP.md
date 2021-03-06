# Installation

```
    $ git clone git@github.com:DigitalGeographyLab/Car-Routing.git
    $ cd DigiroadPreDataAnalysis
```

## Libraries required

* OWSLib
```
    $ cd /opt/anaconda3/bin/
    $ ./conda install -c conda-forge owslib
    $ source ./activate
    $ pip install --upgrade owslib
```

  For windows, also required: Microsoft Visual C++ 9.0 is required. Get it from [here][microsoft-vistual-c++].
* nvector (not available in conda repositories)

```
    $ pip install nvector
```
* pyproj
```
    $ conda install -c conda-forge pyproj
```
* psycopg2
```
    $ conda install -c conda-forge psycopg2
```

* geopandas
```
    $ conda install -c conda-forge geopandas
```
* joblib
```
    $ conda install -c anaconda joblib
```
* psutil
```
    $ conda install -c anaconda psutil
```

# Run

```{r, engine='sh', count_lines}
    $ ../Car-Routing/DigiroadPreDataAnalysis$ /opt/anaconda3/bin/./python -m digiroad -s <../startPoints.geojson> -e <../endPoints.geojson> -o <../outputFolder/> -c <IMPEDANCE/COST ATTRIBUTE>
```

Input testPoints.geojson is in the format:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "MultiPoint",
        "coordinates": [
          [8443150.541380882, 2770625.5047027366],
          [8436436.62334174, 2776131.3593964037]
        ]
      },
      "properties": {
        "title": "Pair 1",
        "icon": "monument"
      }
    },
    .
    .
    .
    {
      "type": "Feature",
      "geometry": {
        "type": "MultiPoint",
        "coordinates": [
          [8452765.483509162, 2783396.1614870545],
          [8445529.046721973, 2778867.5661432995]
        ]
      },
      "properties": {
        "title": "Pair 2",
        "icon": "monument"
      }
    }
  ]
}
```

Impedance/Cost attribute values accepted:
* DISTANCE
* SPEED_LIMIT_TIME
* DAY_AVG_DELAY_TIME
* MIDDAY_DELAY_TIME
* RUSH_HOUR_DELAY

# Additonal Layers 

You are allowed to add new attributes coming from a polygon layer and attach them to the selected points (start and end point to calculate the shortpath).

See: [Additional Layers Operations][additional-layers]



[microsoft-vistual-c++]: https://www.microsoft.com/en-us/download/details.aspx?id=44266
[additional-layers]: digiroad/additionalOperations/ADDITIONAL_LAYERS.md