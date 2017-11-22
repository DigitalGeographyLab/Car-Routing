# Install

Clone `git@github.com:DigitalGeographyLab/Car-Routing.git`

## Libraries required

* OWSLib

  Also require: Microsoft Visual C++ 9.0 is required. Get it from [here][microsoft-vistual-c++].
  
  
# Run

```{r, engine='sh', count_lines}
../Car-Routing/src$ python -m digiroad -c <../testPoints.geojson> -s <../outputFolder/> -i <IMPEDANCE/COST ATTRIBUTE>
```

Input testPoints.geojson is in the format:

```json
{
  "type": "geojson",
  "data": {
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
}
```

Impedance/Cost attribute values accepted:
* DISTANCE
* SPEED_LIMIT_TIME
* DAY_AVG_DELAY_TIME
* MIDDAY_DELAY_TIME
* RUSH_HOUR_DELAY

[microsoft-vistual-c++]: https://www.microsoft.com/en-us/download/details.aspx?id=44266