// Wait Time Graphs

queue()
    .defer(d3.json, "/myNHS/waitTimeData")
    .await(makeGraphs);


function reduceAddAvg(attr) {
  return function(p,v) {
    ++p.count
    p.sum += v[attr];

    if (p.count > 0){
        p.avg = p.sum/p.count;
    } else {
        p.avg = 0;
    }

    return p;
  };
};

function reduceRemoveAvg(attr) {
  return function(p,v) {
    --p.count
    p.sum -= v[attr];

    if (p.count > 0){
        p.avg = p.sum/p.count;
    } else {
        p.avg = 0;
    }

    return p;
  };
};

function reduceInitAvg() {
  return {count:0, sum:0, avg:0};
};


function reduceAdd(p, v) {
    p.total += v.Value;
    ++p.count;
    if (p.count > 0){
        p.average = d3.round((p.total / p.count), 1);
    }else {
        p.average = 0;
    }
    return p;
}

function reduceRemove(p, v) {
    p.total -= v.Value;
    --p.count;
    if (p.count > 0){
        p.average = d3.round((p.total / p.count), 1);
    }else {
        p.average = 0;
    }
    return p;
}

function reduceInitial() {
    return {
        total: 0,
        count: 0,
        average: 0,
    };
}


function makeGraphs(error, projectsJson) {
	//Set Data Formatters
	var dateFormat = d3.time.format("%Y-%m-%d");
	var monthFormat = d3.time.format("%m")

	//Get projectsJson data
	var data = projectsJson;

	//Modify
    data.forEach(function(d) {
        d.date = dateFormat.parse(d.IsCurrentLastModified);
        d.month = +monthFormat(d.date);
    });

    //Create a Crossfilter instance
	var ndx = crossfilter(data);
	var all = ndx.groupAll();

	// Define Dimensions
	var allDim = ndx.dimension(function(d) {return d;});
	var OrganisationNameDim = ndx.dimension(function(d) { return d.OrganisationName; });
	var OrganisationTypeIDDim = ndx.dimension(function(d) { return d.OrganisationTypeID; });
	var isPimsManagedDim = ndx.dimension(function(d) { return d.IsPimsManaged; });
	var serviceNameDim = ndx.dimension(function(d) {return d.ServiceName;})

        // dimension by month
        var monthDim = ndx.dimension(function(d) {
            var month = d.month;
        //    var name = ["January","February","March","April","May","June","July","August","September","October","November","December"]
            var name = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            return name[month-1];
        });

    // Set up Groups
	var OrganisationNameGroup = OrganisationNameDim.group();
	var OrganisationTypeIDGroup = OrganisationTypeIDDim.group();
	var isPimsManagedGroup = isPimsManagedDim.group();
	var serviceNameGroup = serviceNameDim.group();

    // Compute sums and counts
	var TypeCount = OrganisationTypeIDGroup.reduceCount();
	var PimsCount = isPimsManagedGroup.reduceCount();
	var countPerMonth = monthDim.group().reduceCount();
	var serviceNameCount = serviceNameGroup.reduceCount();
	//var average = OrganisationNameGroup.reduce(reduceAddAvg('Value'), reduceRemoveAvg('Value'), reduceInitAvg);
	var average = OrganisationNameGroup.reduceSum(function(d) {return d.Value});
	//var average = OrganisationNameGroup.reduce(reduceAdd, reduceRemove, reduceInitial);;
	//var average = reductio().avg(function(d) { return +d.Value; })(OrganisationNameGroup);
	//var average = reductio().min(function(d) { return +d.Value; })(OrganisationNameGroup);
    console.log(average.top(4));


    //Charts
	var Chart = dc.rowChart("#row-chart");
    var typeChart = dc.pieChart('#chart-type');
    var pimsChart = dc.pieChart('#chart-pims');
    var yearChart = dc.pieChart('#chart-year');
    var ServiceChart = dc.rowChart('#chart-service');
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

    typeChart
        .width(200)
        .height(200)
        .dimension(OrganisationTypeIDDim)
        .group(TypeCount)
        .innerRadius(50);

    ServiceChart
        .width(600)
        .height(310)
        .gap(2)
        .dimension(serviceNameDim)
        .group(serviceNameCount)
        .elasticX(true)
        .ordering(function(d) { return -d.value })
        .label(function (d) { return d.key })
        .title(function (d) { return d.value })
        .renderTitleLabel(true);

    yearChart
        .width(200)
        .height(200)
        .dimension(monthDim)
        .group(countPerMonth)
        .innerRadius(50)
        .renderLabel(true);

    pimsChart
        .width(200)
        .height(200)
        .dimension(isPimsManagedDim)
        .group(PimsCount)
        .innerRadius(50);

	Chart
        .width(700)
        .height(530)
        .gap(2)
        .dimension(OrganisationNameDim)
        .group(average)
        .elasticX(true)
        .label(function (d) { return d.key })
        //.valueAccessor(function (p) {return p.value.avg;})
        //.ordering(function(p) { return -p.value.min })
        .ordering(function(d) { return -d.value })
        //.title(function (d) { return +d.value.min.toFixed(1)  })
        .title(function (d) { return d.value})
        .renderTitleLabel(true)
        .rowsCap(30);

    dataTable
    .dimension(allDim)
    .group(function (d) { return 'dc.js insists on putting a row here so I remove it using JS'; })
    .size(50)
    .columns([
      function (d) { return d.OrganisationName; },
      function (d) { return d.OrganisationTypeID; },
      function (d) { return d.IsPimsManaged; },
      function (d) { return d.month; },
      function (d) { return d.ServiceName; },
      function (d) { return d.Value; }
    ])
    .sortBy(dc.pluck('Value'))
    .order(d3.ascending)
    .on('renderlet', function (table) {
      // each time table is rendered remove nasty extra row dc.js insists on adding
      table.select('tr.dc-table-group').remove();

      // update map to match filtered data
      Markers.clearLayers();
      _.each(allDim.top(5000), function (d) {
        var name = d.OrganisationName;
        var a1 = d.Address1;
        var a2 = d.Address2;
        var a3 = d.Address3;
        var postcode = d.Postcode;

        var marker = L.circleMarker([d.Latitude, d.Longitude]);
        marker.bindPopup("<p><strong>Name:</strong><br>" + name +  "<br><strong>Address:</strong><br>" + a1 +
                         "<br>" + a2 + "<br>" + a3 + "<br>" + postcode + "</p>");
        marker.setRadius(d.Value)

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

  d3.selectAll('a#service').on('click', function () {
        ServiceChart.filterAll();
        dc.redrawAll();
  });

    dc.renderAll();

};