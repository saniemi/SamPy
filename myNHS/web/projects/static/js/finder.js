//myNHS Dashboard
//===============
//
//Simple set of graphs for the Organisation Finder
//
//
//Author
//------
//
//:author: Sami Niemi (sami.niemi@valtech.co.uk)
//
//
//Version
//-------
//
//:version: 0.3
//:date: 25-Jul-2016


queue()
    .defer(d3.json, "/myNHS/finderData")
    //.defer(d3.csv, "./static/data/finder.csv")
    .defer(d3.json, "/myNHS/latestImages")
    .await(makeGraphs);

function initmap() {
    var maxBounds = [[48,-12], [61,5]];
    var imageBounds = [[48,-12], [61,5]];
    var map = L.map('map',{center:new L.LatLng(54, -2),zoom:6,maxBounds:maxBounds});
    var osmAttrib='Map data &copy; <a href="http://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors<\/a>';
    var osm = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution: osmAttrib});

    var lastRainTime = "2016-08-03T13:00:00"; //"<?php echo $lastRainTime?>";
    console.log(lastRainTime);
    //you will need to replace {key}  with your actual API key
    var RainImageUrl = 'http://datapoint.metoffice.gov.uk/public/data/layer/wxobs/RADAR_UK_Composite_Highres/png?TIME='+lastRainTime+'Z&key=7e2ecd8b-e840-4d06-8eba-5b48ff725\
cb0';
    console.log(RainImageUrl);
    var rainLayer = L.imageOverlay(RainImageUrl, imageBounds);

    var lastLightningTime = "2016-08-03T13:00:00";//"<?php echo $lastLightningTime?>";
    //you will need to replace {key}  with your actual API key
    var LightningImageUrl = 'http://datapoint.metoffice.gov.uk/public/data/layer/wxobs/ATDNET_Sferics/png?TIME='+lastLightningTime+'Z&key=7e2ecd8b-e840-4d06-8eba-5b48ff725cb\
0';
    var lightningLayer = L.imageOverlay(LightningImageUrl, imageBounds);

    var overlays = {
        "Rain": rainLayer,
        "Lightning":lightningLayer
    };

    map.addLayer(osm);
    map.addLayer(rainLayer);
    L.control.layers('',overlays,{collapsed:false}).addTo(map);

}


function makeGraphs(error, projectsJson, timingJson) {
	//Get projectsJson data
	var data = projectsJson;
	var timing = timingJson;

    //Get the latest timestamps for weather data
    var lastLightningTime = timing.Lightning;
    var lastRainTime = timing.Rainfall;

    //Create a Crossfilter instance
	var ndx = crossfilter(data);

	// Define Dimensions
	var allDim = ndx.dimension(function(d) {return d;});
    var DisplayNameDim = ndx.dimension(function(d) { return d.DisplayName; });

    // Set up Groups
	var DisplayNameGroup = DisplayNameDim.group().reduceCount();

    // Table
	var dataTable = dc.dataTable("#data-table");

    // A dropdown widget
    var selectField = dc.selectMenu('#menuselect');
    selectField
        .dimension(DisplayNameDim)
        .group(DisplayNameGroup);

    /* instantiate and configure map */
    L.mapbox.accessToken = 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg';
    var maxBounds = [[48,-12], [61,5]];
    var imageBounds = [[48,-12], [61,5]];

    // street Layers
    var streets = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
      id: 'mapbox.streets',
      accessToken: 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg'});
    // CCG areas
    custom = L.geoJson(null, {style: style, onEachFeature: onEachFeature});
    var CCG = omnivore.kml('./static/data/augmented.KML', null, custom);
    // Rainfall
    var RainImageUrl = 'http://datapoint.metoffice.gov.uk/public/data/layer/wxobs/RADAR_UK_Composite_Highres/png?TIME='+lastRainTime+'Z&key=7e2ecd8b-e840-4d06-8eba-5b48ff725cb0';
    var rainLayer = L.imageOverlay(RainImageUrl, imageBounds);
    // Lightning
    var LightningImageUrl = 'http://datapoint.metoffice.gov.uk/public/data/layer/wxobs/ATDNET_Sferics/png?TIME='+lastLightningTime+'Z&key=7e2ecd8b-e840-4d06-8eba-5b48ff725cb0';
    var lightningLayer = L.imageOverlay(LightningImageUrl, imageBounds);

    // Set up the map
    var map = L.map('map', {center: new L.LatLng(54, -2), zoom:6, maxBounds:maxBounds, layers:[streets, CCG, rainLayer, lightningLayer]});

    // Key value mapping of the layers
    var baseMaps = {"Streets": streets};
    var overlayMaps = {"CCG": CCG, "Rain": rainLayer, "Lightning":lightningLayer};

    // Add the control
    L.control.layers(baseMaps, overlayMaps).addTo(map);

    // Markers feature group
    var Markers = new L.FeatureGroup().bringToFront();

    // Add info
    var info = L.control();
    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    info.update = function (props) {
        this._div.innerHTML = '<h4>Population</h4>' +  (props ?
            '<b>' + props.population + '</b><br />'
            : '');
    };
    info.addTo(map);

    function getColor(d) {
        return d > 300000 ? '#800026' :
               d > 250000  ? '#BD0026' :
               d > 200000  ? '#E31A1C' :
               d > 180000  ? '#FC4E2A' :
               d > 140000   ? '#FD8D3C' :
               d > 120000   ? '#FEB24C' :
               d > 100000   ? '#FED976' :
                             '#FFEDA0';
    }

    function style(feature) {
        //console.log(feature)
        //console.log(feature.properties.population)
        return {
            fillColor: getColor(+feature.properties.population),
            weight: 2,
            opacity: 1,
            color: 'black',
            dashArray: '3',
            fillOpacity: 0.2
        };
    }

    function highlightFeature(e) {
        var layer = e.target;

        layer.setStyle({
            weight: 4,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.5
        });

        if (!L.Browser.ie && !L.Browser.opera) {
            layer.bringToFront();
        }

        info.update(layer.feature.properties);

    }

    function resetHighlight(e) {
        custom.resetStyle(e.target);
        info.update();
    }


    function zoomToFeature(e) {
        map.fitBounds(e.target.getBounds());
    }

    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: zoomToFeature
        });
    }

    // Add legend
    var legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend'),
            grades = [0, 100000, 120000, 140000, 180000, 200000, 250000, 300000],
            labels = [];

        // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = 0; i < grades.length; i++) {
            div.innerHTML +=
                '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
                grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
        }

        return div;
    };
    legend.addTo(map);

    dataTable
    .dimension(allDim)
    .group(function (d) { return 'dc.js insists on putting a row here so I remove it using JS'; })
    .size(20)
    .columns([
      function (d) { return d.OrganisationName; },
      function (d) { return d.DisplayName; },
      function (d) { return d.Address1 + d.Address2 + d.Address3; },
      function (d) { return d.Postcode; },
      function (d) { return d.OrganisationContactValue; }
    ])
    .on('renderlet', function (table) {
      // each time table is rendered remove nasty extra row dc.js insists on adding
      table.select('tr.dc-table-group').remove();


      var array = [];

      // update map to match filtered data
      Markers.clearLayers();

      _.each(allDim.top(5000), function (d) {
        var name = d.OrganisationName;
        var a1 = d.Address1;
        var a2 = d.Address2;
        var a3 = d.Address3;
        var postcode = d.Postcode;
        var organisationContactValue = d.OrganisationContactValue;

        var marker = L.circleMarker([d.Latitude, d.Longitude], {color: 'magenta', fillColor: 'magenta', fillOpacity: 0.5});
        //var marker = L.marker([d.Latitude, d.Longitude]);
        marker.bindPopup("<p><strong>Name:</strong><br>" + name +  "<br><strong>Address:</strong><br>" + a1 +
                         "<br>" + a2 + "<br>" + a3 + "<br>" + postcode +
                         "<br><strong>Phone Number:</strong><br>" + organisationContactValue + "</p>");
        marker.setRadius(4)

        Markers.addLayer(marker);

        //array.push(marker);

      });
      //Markers.addLayer(array);
      //var Markers = L.featureGroup(array).addTo(map);

      map.addLayer(Markers);
      map.fitBounds(Markers.getBounds());
    });

    dc.renderAll();

};