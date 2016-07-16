queue()
    .defer(d3.json, "/myNHS/hipReplacements")
    .await(makeGraphs);


function makeGraphs(error, projectsJson) {
	//Set Data Formatters
	var dateFormat = d3.time.format("%Y-%m-%d");
	var yearFormat = d3.time.format('%Y');

	//Get projectsJson data
	var hipReplacements = projectsJson;
	console.log(hipReplacements)

	//Modify
    hipReplacements.forEach(function(d) {
        d.date = dateFormat.parse(d.IsCurrentLastModified);
        d.IsPimsManaged = +d.IsPimsManaged;
        d.year = +yearFormat(d.date);
    });

    //Create a Crossfilter instance
	var ndx = crossfilter(hipReplacements);
	var all = ndx.groupAll();
	//console.log("All Reduced Count:" + all.reduceCount().value())

	// Define Dimensions
	var allDim = ndx.dimension(function(d) {return d;});
	var OrganisationNameDim = ndx.dimension(function(d) { return d.OrganisationName; });
	var OrganisationTypeIDDim = ndx.dimension(function(d) { return d.OrganisationTypeID; });
	var isPimsManagedDim = ndx.dimension(function(d) { return d.IsPimsManaged; });
	var yearDim  = ndx.dimension(function(d) {return d.year;})

    // Set up Groups
	var OrganisationNameGroup = OrganisationNameDim.group();
	var OrganisationTypeIDGroup = OrganisationTypeIDDim.group();
	var isPimsManagedGroup = isPimsManagedDim.group();

    // Compute sums and counts
	var TotalHips = OrganisationNameGroup.reduceSum(function(d) {return d.Value;});
	var TypeCount = OrganisationTypeIDGroup.reduceCount();
	var PimsCount = isPimsManagedGroup.reduceCount();
	var countPerYear = yearDim.group().reduceCount();
	console.log(PimsCount.top(3));

    //Charts
	var Chart = dc.rowChart("#row-chart");
	var number = dc.numberDisplay("#number");
    var dataCount = dc.dataCount('#data-count');
    var typeChart = dc.pieChart('#chart-type');
    var pimsChart = dc.pieChart('#chart-pims');
    var yearChart = dc.pieChart('#chart-year');
    // Table
	var dataTable = dc.dataTable("#data-table");

    /* instantiate and configure map */
    L.mapbox.accessToken = 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg';
    var map = L.map('map', 'mapbox.streets').setView([53.4, -1.2], 7);
    var Markers = new L.FeatureGroup();

    map.invalidateSize();

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
      id: 'mapbox.streets',
      accessToken: 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg',
    } ).addTo(map);

    dataCount
         .dimension(ndx)
         .group(all);

    typeChart
        .width(150)
        .height(150)
        .dimension(OrganisationTypeIDDim)
        .group(TypeCount)
        .innerRadius(20)
        .colors(d3.scale.ordinal().range([ '#1f78b4', '#b2df8a', '#cab2d6', '#bc80bd']));

    yearChart
        .width(150)
        .height(150)
        .dimension(yearDim)
        .group(countPerYear)
        .innerRadius(20)
        .renderLabel(true);

    pimsChart
        .width(150)
        .height(150)
        .dimension(isPimsManagedDim)
        .group(PimsCount)
        .innerRadius(20);

	Chart
        .width(700)
        .height(2400)
        .gap(1)
        .dimension(OrganisationNameDim)
        .group(TotalHips)
        .elasticX(true)
        .ordering(function(d) { return -d.value })
        .label(function (d) { return d.key })
        .title(function (d) { return d.value })
        .renderTitleLabel(true);

	number
        .formatNumber(d3.format("d"))
        .valueAccessor(function(d){return d; })
        .group(all);

    dataTable
    .dimension(allDim)
    .group(function (d) { return 'dc.js insists on putting a row here so I remove it using JS'; })
    .size(100)
    .columns([
      function (d) { return d.OrganisationName; },
      function (d) { return d.OrganisationTypeID; },
      function (d) { return d.isPimsManaged; },
      function (d) { return d.date; },
      function (d) { return d.year; },
      function (d) { return d.Value; },
      function (d) { return d.MetricName; }
    ])
    .sortBy(dc.pluck('Value'))
    .order(d3.descending)
    .on('renderlet', function (table) {
      // each time table is rendered remove nasty extra row dc.js insists on adding
      table.select('tr.dc-table-group').remove();

      // update map with breweries to match filtered data
      Markers.clearLayers();
      _.each(allDim.top(Infinity), function (d) {
        var name = d.OrganisationName;
        var value = d.Value;
        var marker = L.marker([d.Latitude, d.Longitude]);
        marker.bindPopup("<p>" + name +  " " + value + "</p>");
        Markers.addLayer(marker);
      });
      map.addLayer(Markers);
      map.fitBounds(Markers.getBounds());
    });

  // register handlers
  d3.selectAll('a#all').on('click', function () {
        dc.filterAll();
        dc.renderAll();
  });

  d3.selectAll('a#year').on('click', function () {
        yearChart.filterAll();
        dc.redrawAll();
  });

  d3.selectAll('a#pims').on('click', function () {
        pimsChart.filterAll();
        dc.redrawAll();
  });

  d3.selectAll('a#type').on('click', function () {
        typeChart.filterAll();
        dc.redrawAll();
  });

  d3.selectAll('a#bars').on('click', function () {
        Chart.filterAll();
        dc.redrawAll();
  });


    dc.renderAll();

};