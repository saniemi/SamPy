// Finder Graphs

queue()
    .defer(d3.json, "/myNHS/finderData")
    .await(makeGraphs);


function makeGraphs(error, projectsJson) {
	//Get projectsJson data
	var data = projectsJson;

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

    // street Layers
    var streets = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
      id: 'mapbox.streets',
      accessToken: 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg'});
    // contours
    custom = L.geoJson(null, {style: {"color": "black", "weight": 3, "opacity": 0.15}});
    var CCG = omnivore.kml('./static/data/CCG_BSC_Apr2015.KML', null, custom);

    // Set up the map
    var map = L.map('map', {center: [53.4, -1.2], zoom:6, layers:[streets, CCG]});

    // Key value mapping of the layers
    var baseMaps = {"Streets": streets, "CCG": CCG};
    var overlayMaps = {"CCG": CCG};

    // Add the control
    L.control.layers(baseMaps, overlayMaps).addTo(map);

    // Markers feature group
    var Markers = new L.FeatureGroup().bringToFront();


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

        var marker = L.circleMarker([d.Latitude, d.Longitude], {color: 'blue', fillColor: 'blue', fillOpacity: 0.5});
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