//myNHS Dashboard
//===============
//
//Simple set of graphs for the Operations view.
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
//:version: 0.4
//:date: 25-Jul-2016


queue()
    .defer(d3.json, "/myNHS/operationsData")
    //.defer(d3.csv, "./static/data/operations.csv")
    .await(makeGraphs);


function makeGraphs(error, projectsJson) {
	//Set Data Formatters
	var dateFormat = d3.time.format("%Y-%m-%d");

	//Get projectsJson data
	var data = projectsJson;

	//Modify
    data.forEach(function(d) {
        d.date = dateFormat.parse(d.IsCurrentLastModified);
    });

    //Create a Crossfilter instance
	var ndx = crossfilter(data);

	// Define Dimensions
	var allDim = ndx.dimension(function(d) {return d;});
	var OrganisationNameDim = ndx.dimension(function(d) { return d.OrganisationName; });
	var OrganisationTypeIDDim = ndx.dimension(function(d) { return d.OrganisationTypeID; });
	var DateDim = ndx.dimension(function(d) { return d.date; });
	var TreatmentNameDim  = ndx.dimension(function(d) {return d.TreatmentName;})

    // Set up Groups
	var OrganisationNameGroup = OrganisationNameDim.group();
	var OrganisationTypeIDGroup = OrganisationTypeIDDim.group();
	var TreatmentNameGroup = TreatmentNameDim.group();
	var DateGroup = DateDim.group();

    // Compute sums and counts
	var Total = OrganisationNameGroup.reduceSum(function(d) {return d.Value;});
	var TypeCount = OrganisationTypeIDGroup.reduceCount();
	var countPerDate = DateGroup.reduceSum(function(d) {return d.Value;});

    //Charts
	var Chart = dc.rowChart("#row-chart");
    var typeChart = dc.pieChart('#chart-type');
    var yearChart = dc.bubbleChart('#chart-year');
    // Table
	var dataTable = dc.dataTable("#data-table");

    // A dropdown widget
    var selectField = dc.selectMenu('#menuselect');
    selectField
        .dimension(TreatmentNameDim)
        .group(TreatmentNameGroup.reduceCount());

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

//    // Add info
//    var info = L.control();
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

    typeChart
        .width(160)
        .height(160)
        .dimension(OrganisationTypeIDDim)
        .group(TypeCount)
        .transitionDuration(1500)
        .colors(d3.scale.category10())
        .innerRadius(30);

    yearChart
        .width(540)
        .height(200)
        .margins({ top: 5, right: 10, bottom: 30, left: 80 })
        .dimension(DateDim)
        .group(countPerDate)
        .x(d3.time.scale().domain(d3.extent(data, function(d) { return d.date; })).nice())
        .y(d3.scale.linear().domain([0, d3.max(countPerDate, function(d) { return d.Value; })+10]))
        .r(d3.scale.linear())
        .radiusValueAccessor(function (p) {
                        return 1;
                    })
        .elasticX(true)
        .elasticY(true)
        .elasticRadius(true)
        .renderLabel(false)
        .renderHorizontalGridLines(true)
        .renderVerticalGridLines(true)
        .transitionDuration(1500)
        .yAxisPadding(5000)
        .renderlet(function(chart) {chart.svg().selectAll('.chart-body').attr('clip-path', null)})
        .xAxisPadding(2)
        .xUnits(d3.time.days)
        .maxBubbleRelativeSize(2)
        .xAxis().ticks(5);

	Chart
        .width(580)
        .height(530)
        .gap(2)
        .dimension(OrganisationNameDim)
        .group(Total)
        .elasticX(true)
        .ordering(function(d) { return -d.value })
        .label(function (d) { return d.key })
        .title(function (d) { return d.value })
        .renderTitleLabel(true)
        .rowsCap(30);

    dataTable
    .dimension(allDim)
    .group(function (d) { return 'dc.js insists on putting a row here so I remove it using JS'; })
    .columns([
      function (d) { return d.OrganisationName; },
      function (d) { return d.OrganisationTypeID; },
      function (d) { return d.date; },
      function (d) { return d.Value; },
      function (d) { return d.TreatmentID; },
      function (d) { return d.TreatmentName; }
    ])
    .sortBy(dc.pluck('Value'))
    .order(d3.descending)
    .size(30)
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
        marker.setRadius(Math.max(2, Math.min(d.Value / 50, 20)));

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