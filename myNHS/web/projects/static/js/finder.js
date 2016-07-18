// Finder Graphs

queue()
    .defer(d3.json, "/myNHS/finderData")
    .await(makeGraphs);


function makeGraphs(error, projectsJson) {
	//Get projectsJson data
	var data = projectsJson;

    //Create a Crossfilter instance
	var ndx = crossfilter(data);
	//var all = ndx.groupAll();

	// Define Dimensions
	var allDim = ndx.dimension(function(d) {return d;});
	//var OrganisationNameDim = ndx.dimension(function(d) { return d.OrganisationName; });
    //var OrganisationTypeIDDim = ndx.dimension(dc.pluck('OrganisationTypeID'));
    var DisplayNameDim = ndx.dimension(function(d) { return d.DisplayName; });

    // Set up Groups
	//var OrganisationNameGroup = OrganisationNameDim.group();
	var DisplayNameGroup = DisplayNameDim.group().reduceCount();

    // Compute sums and counts
	//var TypeCount = OrganisationTypeIDDim.group().reduceCount();

    //Charts
    //var typeChart = dc.pieChart('#chart-type');
    // Table
	var dataTable = dc.dataTable("#data-table");

    // A dropdown widget
    selectField = dc.selectMenu('#menuselect')
        .dimension(DisplayNameDim)
        .group(DisplayNameGroup);

    /* instantiate and configure map */
    L.mapbox.accessToken = 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg';
    var map = L.map('map', 'mapbox.streets').setView([53.4, -1.2], 6);
    var Markers = new L.FeatureGroup();

    map.invalidateSize();

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
      id: 'mapbox.streets',
      accessToken: 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg',
    } ).addTo(map);


//    typeChart
//        .width(150)
//        .height(150)
//        .dimension(OrganisationTypeIDDim)
//        .group(TypeCount)
//        .innerRadius(25);

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
//    .sortBy(dc.pluck('OrganisationName'))
//    .order(d3.ascending)
    .on('renderlet', function (table) {
      // each time table is rendered remove nasty extra row dc.js insists on adding
      table.select('tr.dc-table-group').remove();

      var array = [];

      // update map to match filtered data
      Markers.clearLayers();
      _.each(allDim.top(Infinity), function (d) {
        var name = d.OrganisationName;
        var a1 = d.Address1;
        var a2 = d.Address2;
        var a3 = d.Address3;
        var postcode = d.Postcode;
        var organisationContactValue = d.OrganisationContactValue;

//        var marker = L.circleMarker([d.Latitude, d.Longitude]);
        var marker = L.marker([d.Latitude, d.Longitude]);
        marker.bindPopup("<p><strong>Name:</strong><br>" + name +  "<br><strong>Address:</strong><br>" + a1 +
                         "<br>" + a2 + "<br>" + a3 + "<br>" + postcode +
                         "<br><strong>Phone Number:</strong><br>" + organisationContactValue + "</p>");
//        marker.setRadius(3)

        array.push(marker);

      });
      map.addLayers(array);
      map.addLayer(Markers);
      map.fitBounds(Markers.getBounds());
    });

  // register handlers
  d3.selectAll('a#type').on('click', function () {
        typeChart.filterAll();
        dc.redrawAll();
  });


    dc.renderAll();

};