# DGL Routing Analytics

This web application is intended to understand how pgRouting works and create a simple interface to interact with it using Geoserver as an mediator to create a feature layer with the optimal route.

Based on [this tutorial][pgRouting-tutorial]

## Installation

Clone the repository:

    $ git clone git@github.com:DigitalGeographyLab/Car-Routing.git

Install dependencies:

    $ npm install

* if you got an error, you probably have not node or a recent version of npm installed. Follow the steps at ```https://docs.npmjs.com/getting-started/installing-node``` to install Node.js. After installing, test it using ```$ node -v```. It should say a version number. Then, make sure npm is installed by using ```$ npm install npm@latest -g```. After install process, test your npm version with ```$ npm -v``` It should again say a version number. Now retry installing the node dependencies with ```$ npm install```.

Install bower components:

    $ npm install -g bower
    $ bower install

## Run it:

Run the development web-server via gulp:

    $ gulp

You can now have a look on the Webapp via your webbrowser at
```localhost:4014``` or ```127.0.0.1:4014```

### Changing the port:
* for gulp:
4014 is the default port for this project, if you want or have to change it,
open the project's ```/gulpfile.js``` and change the port in line
19 to your desire.

* for node:
if you want or have to change port when hosting via nodeJS,
open the project's ```/all.js``` and change the port in line
7 to your desire.



[pgRouting-tutorial]: http://workshops.boundlessgeo.com/tutorial-routing/
