// Hip Replacement Graphs


queue()
    .defer(d3.json, "/myNHS/hipReplacements")
    .await(makeGraphs);


function makeGraphs(error, projectsJson) {
	//Set Data Formatters
	var dateFormat = d3.time.format("%Y-%m-%d");
	var yearFormat = d3.time.format('%Y');
//	var dateFormat = d3.timeFormat("%Y-%m-%d");
//	var yearFormat = d3.timeFormat('%Y');


	//Get projectsJson data
	var hipReplacements = projectsJson;
	console.log(hipReplacements)

	//Modify
    hipReplacements.forEach(function(d) {
        d.date = dateFormat.parse(d.IsCurrentLastModified);
        d.Views = +d.Views;
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
    var viewsDim = ndx.dimension(function(d) { return d.Views; });
    var probabilityDim = ndx.dimension(function(d) { return d.Probability; });

    // Set up Groups
	var OrganisationNameGroup = OrganisationNameDim.group();
	var OrganisationTypeIDGroup = OrganisationTypeIDDim.group();
	var isPimsManagedGroup = isPimsManagedDim.group();

    // Compute sums and counts
	var TotalHips = OrganisationNameGroup.reduceSum(function(d) {return d.Value;});
	var TypeCount = OrganisationTypeIDGroup.reduceCount();
	var PimsCount = isPimsManagedGroup.reduceCount();
	var countPerYear = yearDim.group().reduceCount();
    var viewCount = viewsDim.group().reduceSum(function(d) {return d.Views;});
    var probabilityCount = probabilityDim.group().reduceCount();

    //Charts
	var Chart = dc.rowChart("#row-chart");
	var number = dc.numberDisplay("#number");
    var dataCount = dc.dataCount('#data-count');
    var typeChart = dc.pieChart('#chart-type');
    var pimsChart = dc.pieChart('#chart-pims');
    var yearChart = dc.pieChart('#chart-year');
    var viewChart = dc.barChart('#chart-views');
    var probabilityChart = dc.pieChart('#chart-prob');
    // Table
	var dataTable = dc.dataTable("#data-table");

    /* instantiate and configure map */
    L.mapbox.accessToken = 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg';
    var map = L.map('map', 'mapbox.streets').setView([53.4, -1.2], 6);
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
        .innerRadius(25);
//        .colors(d3.scale.ordinal().range([ '#1f78b4', '#b2df8a', '#cab2d6', '#bc80bd']));

    probabilityChart
        .width(150)
        .height(150)
        .dimension(probabilityDim)
        .group(probabilityCount)
        .innerRadius(25);

    yearChart
        .width(150)
        .height(150)
        .dimension(yearDim)
        .group(countPerYear)
        .innerRadius(25)
        .renderLabel(true);

    pimsChart
        .width(150)
        .height(150)
        .dimension(isPimsManagedDim)
        .group(PimsCount)
        .innerRadius(25);

    viewChart
        .width(400)
        .height(180)
        .dimension(viewsDim)
        .group(viewCount)
        .x(d3.scale.linear().domain([-0.0, d3.max(viewCount, function (d) { return d.Views; }) + 1]))
//        .x(d3.scaleLinear().domain([-0.0, d3.max(viewCount, function (d) { return d.Views; }) + 1]))
        .elasticY(true)
        .elasticX(true)
        .barPadding(1)
        .yAxisLabel('Number of Views')
        .margins({top: 5, right: 20, bottom: 40, left: 80})
        .xAxis().tickFormat(function(v) { return ""; });

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
      function (d) { return d.IsPimsManaged; },
      function (d) { return d.year; },
      function (d) { return d.Views; },
      function (d) { return d.Value; },
      function (d) { return d.MetricName; }
    ])
    .sortBy(dc.pluck('Value'))
    .order(d3.descending)
    .on('renderlet', function (table) {
      // each time table is rendered remove nasty extra row dc.js insists on adding
      table.select('tr.dc-table-group').remove();

      // update map to match filtered data
      Markers.clearLayers();
      _.each(allDim.top(Infinity), function (d) {
        var name = d.OrganisationName;
        var a1 = d.Address1;
        var a2 = d.Address2;
        var a3 = d.Address3;
        var postcode = d.Postcode;

        var marker = L.circleMarker([d.Latitude, d.Longitude]);
        marker.bindPopup("<p>" + name +  "<br>" + a1 + "<br>" + a2 + "<br>" + a3 + "<br>" + postcode + "</p>");
        marker.setRadius(d.Value / 50)

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

  d3.selectAll('a#page').on('click', function () {
        viewChart.filterAll();
        dc.redrawAll();
  });

  d3.selectAll('a#prob').on('click', function () {
        probabilityChart.filterAll();
        dc.redrawAll();
  });

    dc.renderAll();

};