//myNHS Dashboard
//===============
//
//Simple set of graphs for the Average Waiting Time view.
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
//:version: 0.8
//:date: 25-Jul-2016


queue()
    .defer(d3.json, "/myNHS/waitTimeData")
    //.defer(d3.csv, "./static/data/waittime.csv")
    .await(makeGraphs);


function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

// create functions to generate averages for any attribute
function reduceAddAvg(attr) {
  return function(p,v) {
    if (isNumber(v[attr])) {
      ++p.count
      p.sums += v[attr];
      p.avg = (p.count === 0) ? 0 : p.sums/p.count; // guard against dividing by zero
    }
    return p;
  };
}

function reduceRemoveAvg(attr) {
  return function(p,v) {
    if (isNumber(v[attr]))  {
      --p.count
      p.sums -= v[attr];
      p.avg = (p.count === 0) ? 0 : p.sums/p.count;
    }
    return p;
  };
}

function reduceInitAvg() {
  return {count:0, sums:0, avg:0};
}


function makeGraphs(error, projectsJson) {
	//Set Data Formatters
	var dateFormat = d3.time.format("%Y-%m-%d");
	var monthFormat = d3.time.format("%m")

	//Get projectsJson data
	var data = projectsJson;

	//Modify
    data.forEach(function(d) {
        d.Value = +d.Value;
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

    // Compute sums and counts
	var TypeCount = OrganisationTypeIDGroup.reduceCount();
	var PimsCount = isPimsManagedGroup.reduceCount();
	var countPerMonth = monthDim.group().reduceCount();
	var serviceNameCount = serviceNameDim.group().reduceCount();
	var average = OrganisationNameGroup.reduce(reduceAddAvg('Value'), reduceRemoveAvg('Value'), reduceInitAvg).order(function(d) {return +d.avg});
    console.log(average.top(5));

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

    // street Layers
    var streets = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
      id: 'mapbox.streets',
      accessToken: 'pk.eyJ1Ijoic25pZW1pIiwiYSI6ImNpcW85ejZwbjAwNWNpMm5rejJuMzN1Z2cifQ.8FblzFWMjmRLfwrW5ZyvUg'});
    // CCG areas
    custom = L.geoJson(null, {style: style});
    var CCG = omnivore.kml('./static/data/augmented.KML', null, custom);

    // Set up the map
    var map = L.map('map', {center: [53.4, -1.2], zoom:6, layers:[streets, CCG]});

    // Key value mapping of the layers
    var baseMaps = {"Streets": streets, "CCG": CCG};
    var overlayMaps = {"CCG": CCG};

    // Add the control
    L.control.layers(baseMaps, overlayMaps).addTo(map);

    // Markers feature group
    var Markers = new L.FeatureGroup().bringToFront();

     // Add info
//    var info = L.control()
//    info.onAdd = function (map) {
//        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
//        this.update();
//        return this._div;
//    };
//
//    // method that we will use to update the control based on feature properties passed
//    info.update = function (props) {
//        this._div.innerHTML = '<h4>Population</h4>' +  (props ?
//            '<b>' + props.population + '</b><br />'
//            : 'Hover over a CCG');
//    };
//    info.addTo(map);

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
        .label(function(d) { return d.key; })
        .ordering(function(p) { return -p.value.avg })
        .title(function(p) { return d3.round(p.value.avg, 1) })
        .valueAccessor(function (p) {return p.value.avg})
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
//        var a1 = d.Address1;
//        var a2 = d.Address2;
//        var a3 = d.Address3;
//        var postcode = d.Postcode;

        var marker = L.circleMarker([d.Latitude, d.Longitude]);
//        marker.bindPopup("<p><strong>Name:</strong><br>" + name +  "<br><strong>Address:</strong><br>" + a1 +
//                         "<br>" + a2 + "<br>" + a3 + "<br>" + postcode + "</p>");
        marker.bindPopup("<p><strong>Name:</strong><br>" + name + "</p>");

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