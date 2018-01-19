(function () {
    'use strict';
    var MainController = function ($scope, $timeout) {
        //require('ol/ol.css');

        $scope.val = "Main controller variable value"
        var geoserverUrl = '/geoserver';
        //var center = ol.proj.transform([-70.26, 43.67], 'EPSG:4326', 'EPSG:3857');

        L.Control.Layers.include({
            getActiveOverlays: function () {

                // Create array for holding active layers
                var active = [];
                var context = this;
                // Iterate all layers in control
                context._layers.forEach(function (obj) {

                    // Check if it's an overlay and added to the map
                    if (obj.overlay && context._map.hasLayer(obj.layer)) {

                        // Push layer to active array
                        active.push(obj);
                    }
                });

                // Return array
                return active;
            }
        });


        var mbAttr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
            '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="http://mapbox.com">Mapbox</a>',
            mbUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibmdhdmlzaCIsImEiOiJjaXFheHJmc2YwMDdoaHNrcWM4Yjhsa2twIn0.8i1Xxwd1XifUU98dGE9nsQ';

        var grayscale = L.tileLayer(mbUrl, {
                id: 'mapbox.light',
                attribution: mbAttr,
                maxZoom: 22,
                maxNativeZoom: 18
            }),
            streets = L.tileLayer(mbUrl, {
                id: 'mapbox.streets',
                attribution: mbAttr,
                maxZoom: 22,
                maxNativeZoom: 18
            }),
            outdoors = L.tileLayer(mbUrl, {
                id: 'mapbox.outdoors',
                attribution: mbAttr,
                maxZoom: 22,
                maxNativeZoom: 18
            }),
            satellite = L.tileLayer(mbUrl, {
                id: 'mapbox.satellite',
                attribution: mbAttr,
                maxZoom: 22,
                maxNativeZoom: 18
            }),
            dark = L.tileLayer(mbUrl, {id: 'mapbox.dark', attribution: mbAttr, maxZoom: 22, maxNativeZoom: 18}),
            light = L.tileLayer(mbUrl, {id: 'mapbox.light', attribution: mbAttr, maxZoom: 22, maxNativeZoom: 18}),
            satellitestreets = L.tileLayer(mbUrl, {
                id: 'mapbox.streets-satellite',
                attribution: mbAttr,
                maxZoom: 22,
                maxNativeZoom: 18
            });

        var baseLayers = {
            "Grayscale": grayscale,
            "Streets": streets,
            //"Outdoors": outdoors,
            //"Satellite": satellite,
            "Satellite Streets": satellitestreets,
            "Dark Map": dark
            //"Light Map": light
        };

        var center = [45.532189, -122.640910]; //Portland
        center = [60.165063, 24.938400]; //Helsinki

        $scope.map = L.map('map', {
            center: center, //Default location
            zoom: 12, //Default Zoom, Higher = Closer)
            layers: [streets], // Default basemaplayer on startrup, can also give another layer here to show by default)
            maxZoom: 22,
            minZoom: 1,
        });

        $scope.ctrl = L.control.layers(baseLayers, $scope.overlays);
        //$scope.ctrl = L.control.activeLayers(baseLayers, $scope.overlays);
        $scope.ctrl.addTo($scope.map);

        /*var map = L.map('map').setView([51.505, -0.09], 13);

        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        L.marker([51.5, -0.09]).addTo(map)
            .bindPopup('A pretty CSS3 popup.<br> Easily customizable.')
            .openPopup();*/

        $scope.changeImpedance = function (event) {
            $scope.impedanceFilter = event.target.value;
        }

        $scope.searchRoute = function () {
            if ($scope.startMarker && $scope.endMarker) {
                if (!$scope.impedanceFilter) {
                    $scope.impedanceFilter = "pituus";// "time";
                }
                var viewParams = [
                    'source:' + $scope.startMarker.options["id"],
                    'target:' + $scope.endMarker.options["id"],
                    'cost:' + $scope.impedanceFilter
                ];

                var url = $scope.geoserverUrl + '/wfs?service=WFS&version=1.0.0&' +
                    'request=GetFeature&typeName=tutorial:shortest_path&' +
                    'outputformat=application/json&' +
                    '&viewparams=' + viewParams.join(';');

                url = $scope.geoserverUrl + '/wfs?service=WFS&version=1.0.0&' +
                    'request=GetFeature&typeName=tutorial:dgl_shortest_path&' +
                    'outputformat=application/json&' +
                    '&viewparams=' + viewParams.join(';');

                $.ajax({
                    url: url,
                    async: false,
                    type: "GET",
                    //dataType: 'json',
                    contentType: 'text/plain',
                    xhrFields: {
                        // The 'xhrFields' property sets additional fields on the XMLHttpRequest.
                        // This can be used to set the 'withCredentials' property.
                        // Set the value to 'true' if you'd like to pass cookies to the server.
                        // If this is enabled, your server must respond with the header
                        // 'Access-Control-Allow-Credentials: true'.
                        withCredentials: false
                    },
                    headers: {
                        // Set any custom headers here.
                        // If you set any non-simple headers, your server must include these
                        // headers in the 'Access-Control-Allow-Headers' response header.
                    },
                    success: function (json) {
                        $scope.loadRoute(json);
                    },
                    error: function () {
                        // Here's where you handle an error response.
                        // Note that if the error was due to a CORS issue,
                        // this function will still fire, but there won't be any additional
                        // information about the error.
                    }
                });
            }
        }

        $scope.impedanceFilter = "pituus";
        var impedance_attributes = {
            "pituus": "Distance",
            "digiroa_aa": "Speed limit time",
            "kokopva_aa": "Day average delay time",
            "keskpva_aa": "Midday delay time",
            "ruuhka_aa": "Rush hour delay time"
        };

        L.Control.SelectionBox = L.Control.extend({
            onAdd: function (map) {
                var div = L.DomUtil.create('div', 'impedance-box leaflet-bar');

                var title = L.DomUtil.create('span', 'impedance-box-title', div);
                title.innerHTML = "Cost Attributes"
                L.DomEvent.addListener(title, '', $scope.changeImpedance);

                var selection = L.DomUtil.create('select', 'impedance-selector', div);
                L.DomEvent.addListener(selection, 'change', $scope.changeImpedance);

                for (var key in impedance_attributes) {
                    var option = L.DomUtil.create('option', 'impedance-option', selection);
                    option.value = key;
                    option.innerHTML = impedance_attributes[key];
                }

                var searchRouteButton = L.DomUtil.create('input', 'search-button', div);
                searchRouteButton.type = "button";
                searchRouteButton.value = "Search Route";

                L.DomEvent.addListener(searchRouteButton, 'click', $scope.searchRoute);

                return div;
            },

            onRemove: function (map) {
                // Nothing to do here
            }
        });

        L.control.selectionBox = function (opts) {
            return new L.Control.SelectionBox(opts);
        }

        L.control.selectionBox({position: 'topleft'}).addTo($scope.map);


        var zoom = 12;
        var pointerDown = false;
        var currentMarker = null;
        var changed = false;
        var routeLayer;
        var routeSource;
        var travelTime;
        var travelDist;

        // elements in HTML document
        var info = document.getElementById('info');
        var popup = document.getElementById('popup');


        // format a single place name
        $scope.formatPlace = function (name) {
            if (name == null || name == '') {
                return 'unnamed street';
            } else {
                return name;
            }
        }

        // format the list of place names, which may be single roads or intersections
        $scope.formatPlaces = function (list) {
            var text;
            if (!list) {
                return $scope.formatPlace(null);
            }
            var names = list.split(',');
            if (names.length == 0) {
                return $scope.formatPlace(null);
            } else if (names.length == 1) {
                return $scope.formatPlace(names[0]);
            } else if (names.length == 2) {
                text = $scope.formatPlace(names[0]) + ' and ' + $scope.formatPlace(names[1]);
            } else {
                text = ' and ' + $scope.formatPlace(names.pop());
                names.forEach(function (name) {
                    text = name + ', ' + text;
                });
            }

            return 'the intersection of ' + text;
        }

        // format times for display
        $scope.formatTime = function (time) {
            var mins = Math.round(time * 60);
            if (mins == 0) {
                return 'less than a minute';
            } else if (mins == 1) {
                return '1 minute';
            } else {
                return mins + ' minutes';
            }
        }

        // format distances for display
        $scope.formatDist = function (dist) {
            var units;
            dist = dist.toPrecision(2);
            if (dist < 1) {
                dist = dist * 1000;
                units = 'm';
            } else {
                units = 'km';
            }

            // make sure distances like 5.0 appear as just 5
            dist = dist.toString().replace(/[.]0$/, '');
            return dist + units;
        }

        $scope.geoserverUrl = "http://localhost:8080/geoserver";

        // load the response to the nearest_vertex layer
        $scope.loadVertex = function (response, isSource) {
            var featureLayer = L.geoJSON(response/*, {
                onEachFeature: onEachFeature
            }*/);

            var featureLayerProj = L.Proj.geoJson(response);

            if (isSource) {
                if (featureLayer.getLayers().length == 0) {
                    $scope.startMarker = null;
                    return;
                }
                // var latlng = proj4('EPSG:4326', 'EPSG:3857').inverse([featureLayer.getLayers()[0].getLatLng().lng, featureLayer.getLayers()[0].getLatLng().lat]); //[lng, lat]
                var latlng = proj4('EPSG:4326', 'EPSG:3857').inverse([featureLayer.getLayers()[0].feature.geometry.coordinates[0][0], featureLayer.getLayers()[0].feature.geometry.coordinates[0][1]]); //[lng, lat]
                latlng = L.latLng(latlng[1], latlng[0]);// [lat, lng]

                $scope.startMarker.options["id"] = featureLayer.getLayers()[0].feature.id.split('.')[1];
                $scope.startMarker.setLatLng(latlng);
            } else {
                if (featureLayer.getLayers().length == 0) {
                    $scope.endMarker = null;
                    return;
                }

                //var latlng = proj4('EPSG:4326', 'EPSG:3857').inverse([featureLayer.getLayers()[0].getLatLng().lng, featureLayer.getLayers()[0].getLatLng().lat]); //[lng, lat]
                var latlng = proj4('EPSG:4326', 'EPSG:3857').inverse([featureLayer.getLayers()[0].feature.geometry.coordinates[0][0], featureLayer.getLayers()[0].feature.geometry.coordinates[0][1]]); //[lng, lat]
                latlng = L.latLng(latlng[1], latlng[0]);// [lat, lng]

                $scope.endMarker.options["id"] = featureLayer.getLayers()[0].feature.id.split('.')[1];
                $scope.endMarker.setLatLng(latlng);
            }
        }

        // WFS to get the closest vertex to a point on the map
        $scope.getNearestVertex = function (marker) {
            var coordinates = proj4('EPSG:4326', 'EPSG:3857').forward([marker.getLatLng().lng, marker.getLatLng().lat]); //[lng, lat]
            coordinates = L.latLng(coordinates[1], coordinates[0]);// [lat, lng]

            var url = $scope.geoserverUrl + '/wfs?service=WFS&version=1.0.0&' +
                'request=GetFeature&typeName=tutorial:nearest_vertex&' +
                'outputformat=application/json&' +
                'viewparams=x:' + coordinates.lng + ';y:' + coordinates.lat;

            url = $scope.geoserverUrl + '/wfs?service=WFS&version=1.0.0&' +
                'request=GetFeature&typeName=tutorial:dgl_nearest_car_routable_vertex&' +
                'outputformat=application/json&' +
                'viewparams=x:' + coordinates.lng + ';y:' + coordinates.lat;

            $.ajax({
                url: url,
                async: false,
                type: "GET",
                //dataType: 'json',
                contentType: 'text/plain',
                xhrFields: {
                    // The 'xhrFields' property sets additional fields on the XMLHttpRequest.
                    // This can be used to set the 'withCredentials' property.
                    // Set the value to 'true' if you'd like to pass cookies to the server.
                    // If this is enabled, your server must respond with the header
                    // 'Access-Control-Allow-Credentials: true'.
                    withCredentials: false
                },
                headers: {
                    // Set any custom headers here.
                    // If you set any non-simple headers, your server must include these
                    // headers in the 'Access-Control-Allow-Headers' response header.
                },
                success: function (json) {
                    $scope.loadVertex(json, marker == $scope.startMarker);
                },
                error: function () {
                    // Here's where you handle an error response.
                    // Note that if the error was due to a CORS issue,
                    // this function will still fire, but there won't be any additional
                    // information about the error.
                }
            });


        }

        function calculateTotalTravelTime(features) {

            var distance = 0;
            var speed_limit_time = 0;
            var day_avg_delay_time = 0;
            var midday_delay_time = 0;
            var rush_hour_delay_time = 0;

            for (var i in features) {
                distance += features[i].properties.distance;
                speed_limit_time += features[i].properties.speed_limit_time;
                day_avg_delay_time += features[i].properties.day_avg_delay_time;
                midday_delay_time += features[i].properties.midday_delay_time;
                rush_hour_delay_time += features[i].properties.rush_hour_delay_time;
            }

            var totals = {
                "distance": distance,
                "speed_limit_time": speed_limit_time,
                "day_avg_delay_time": day_avg_delay_time,
                "midday_delay_time": midday_delay_time,
                "rush_hour_delay_time": rush_hour_delay_time
            }

            return totals;
        }

        $scope.loadRoute = function (jsonRoute) {
            $scope.routeLayer = L.Proj.geoJson(jsonRoute);

            var totalTimes = calculateTotalTravelTime(jsonRoute.features);

            var div = L.DomUtil.create('div', 'route-popup-box');

            var impedance_attributes_english = {
                "distance": "Total Distance",
                "speed_limit_time": "Total speed limit time",
                "day_avg_delay_time": "Total day average delay time",
                "midday_delay_time": "Total Midday delay time",
                "rush_hour_delay_time": "Total rush hour delay time"
            };

            var title = L.DomUtil.create('span', '', div);
            title.innerHTML = "<b>" + impedance_attributes[$scope.impedanceFilter] + ":</b><br/><br/>";

            for (var key in totalTimes) {
                var option = L.DomUtil.create('span', '', div);
                option.innerHTML = impedance_attributes_english[key] + ": " + Math.round(totalTimes[key]);
            }

            $scope.routeLayer.bindPopup(div);

            $scope.routeLayer.on('mouseover', function (e) {
                this.openPopup();
            });
            /*$scope.routeLayer.on('mouseout', function (e) {
                this.closePopup();
            });*/
            $scope.routeLayer.addTo($scope.map);
            $scope.ctrl.addOverlay($scope.routeLayer, impedance_attributes[$scope.impedanceFilter]);
        }

        $scope.startMarker = undefined;
        $scope.endMarker = undefined;

        $scope.pointSelection = function (event) {
            if ($scope.startMarker && $scope.endMarker) {
                return;
            }

            var marker = L.marker(event.latlng);
            var message = "";
            if (!$scope.startMarker) {
                $scope.startMarker = marker;

                var startIcon = L.icon({
                    iconUrl: 'app\\img\\start-pin-green.png',
                    shadowUrl: 'bower_components\\leaflet\\dist\\images\\marker-shadow.png',


                    iconSize: [48, 48], // size of the icon
                    iconAnchor: [24, 48], // point of the icon which will correspond to marker's location
                    shadowSize: [38, 30], // size of the shadow
                    shadowAnchor: [10, 30],  // the same for the shadow
                    popupAnchor: [0, -48] // point from which the popup should open relative to the iconAnchor
                });

                $scope.startMarker.setIcon(startIcon);
                $scope.getNearestVertex($scope.startMarker);
                message = 'Start point';
            } else {
                $scope.endMarker = marker;

                var endIcon = L.icon({
                    iconUrl: 'app\\img\\end-pin-red.png',
                    shadowUrl: 'bower_components\\leaflet\\dist\\images\\marker-shadow.png',

                    iconSize: [48, 48], // size of the icon
                    iconAnchor: [24, 48], // point of the icon which will correspond to marker's location
                    shadowSize: [38, 30], // size of the shadow
                    shadowAnchor: [10, 30],  // the same for the shadow
                    popupAnchor: [0, -48] // point from which the popup should open relative to the iconAnchor

                    //iconSize: [48, 48], // size of the icon
                    //shadowSize: [50, 64], // size of the shadow
                    //iconAnchor: [22, 94], // point of the icon which will correspond to marker's location
                    //shadowAnchor: [4, 62],  // the same for the shadow
                    //popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
                });

                $scope.endMarker.setIcon(endIcon);
                $scope.getNearestVertex($scope.endMarker);
                message = 'End point';
            }

            marker.addTo($scope.map)
                .bindPopup(message)
                .openPopup();

            $scope.searchRoute();
        }

        //$scope.map.fitWorld();
        $scope.map.on('click', $scope.pointSelection);

        /*setTimeout(function () {
           $scope.map.invalidateSize();
        }, 0);*/
        $timeout(function () {
                window.dispatchEvent(new Event('resize'));
            },
            100);
    }
    // Declare app level module which depends on views, and components
    var myApp = angular.module('myApp', []);
    /*.
        config(['$locationProvider', '$routeProvider', function($locationProvider, $routeProvider) {
            //$locationProvider.hashPrefix('!');

            //$routeProvider.otherwise({redirectTo: '/view1'});
        }])*/
    myApp.run(function ($rootScope, $window) {
        console.log("app started.");
        $rootScope.animating = false;

        $rootScope.height = $window.innerHeight - 52;

        angular.element($window).bind('resize', function () {
            $rootScope.$apply(function () {
                $rootScope.width = $window.innerWidth;
                $rootScope.height = $window.innerHeight - 52;
            });
        });

    });

    myApp.controller('MainController', MainController);
})();
