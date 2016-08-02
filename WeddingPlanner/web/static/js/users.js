//WeddingPlanner  Dashboard
//==========================
//
//Simple set of graphs.
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
//:version: 0.1
//:date: 02-Aug-2016


queue()
    .defer(d3.json, "/WeddingPlanner/users")
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
	var dateFormat = d3.time.format("%Y%m%d");

	//Get projectsJson data
	var data = projectsJson;

	//Modify
    data.forEach(function(d) {
        d.bounceRate = +d3.round(d.bounceRate, 1);
        d.goalCompletionsAll = +d.goalCompletionsAll;
        d.goal10Starts = +d.goal10Starts;
        d.sessions = +d.sessions;
        d.bounces = +d.bounces;
        d.avgSessionDuration = d3.round(+d.avgSessionDuration, 1);
        d.goalStartsAll = +d.goalStartsAll;
        d.goalValueAll = +d.goalValueAll;
        d.goalValuePerSession = +d.goalValuePerSession;
        d.goalAbandonRateAll = +d.goalAbandonRateAll;
        d.date = dateFormat.parse(d.date);
    });

    //Create a Crossfilter instance
	var ndx = crossfilter(data);
	var all = ndx.groupAll();

	// Define Dimensions
	var allDim = ndx.dimension(function(d) {return d;});
	var userTypeDim = ndx.dimension(function(d) { return d.userType; });
	var sourceDim = ndx.dimension(function(d) { return d.source; });
	var userAgeBracketDim = ndx.dimension(function(d) { return d.userAgeBracket; });
	var userGenderDim = ndx.dimension(function(d) { return d.userGender; });
	var deviceCategoryDim = ndx.dimension(function(d) { return d.deviceCategory; });
	var timeDim = ndx.dimension(function(d) {return d.date;})
	var goalStartsAllDim = ndx.dimension(function(d) {return d.goalStartsAll;})
	var goal10StartsDim = ndx.dimension(function(d) {return d.goal10Starts;})
	var goalCompletionsAllDim = ndx.dimension(function(d) {return d.goalCompletionsAll;})
	var goalAbandonRateAllDim = ndx.dimension(function(d) {return d.goalAbandonRateAll;})
	var avgSessionDurationDim = ndx.dimension(function(d) {return d.avgSessionDuration;})

    // Compute sums and counts
	var userTypeCount = userTypeDim.group().reduceCount();
	var sourceCount = sourceDim.group().reduceCount();
	var userAgeBracketCount = userAgeBracketDim.group().reduceCount();
	var userGenderCount = userGenderDim.group().reduceCount();
	var deviceCategoryCount = deviceCategoryDim.group().reduceCount();
	var sessions = timeDim.group().reduceSum(function(d) {return +d.sessions});
	var goalStartsAllSum = goalStartsAllDim.group().reduceSum(function(d) {return +d.goalStartsAll});
	var goal10StartsSum = goal10StartsDim.group().reduceSum(function(d) {return +d.goal10Starts});
	var goalCompletionsAllSum = goalCompletionsAllDim.group().reduceSum(function(d) {return +d.goalCompletionsAll});
    var averagebounceRate = timeDim.group().reduce(reduceAddAvg('bounceRate'), reduceRemoveAvg('bounceRate'), reduceInitAvg);
    var goalAbandonRateAll = goalAbandonRateAllDim.group().reduce(reduceAddAvg('goalAbandonRateAll'), reduceRemoveAvg('goalAbandonRateAll'), reduceInitAvg).order(function(d) {return +d.avg});
    var avgSessionDuration = avgSessionDurationDim.group().reduce(reduceAddAvg('avgSessionDuration'), reduceRemoveAvg('avgSessionDuration'), reduceInitAvg).order(function(d) {return +d.avg});
    //console.log(averagebounceRate.top(5));

    //Charts
    var typeChart = dc.pieChart('#chart-type');
    var sourceChart = dc.pieChart('#chart-source');
    var userAgeBracketChart = dc.pieChart('#chart-age');
    var genderChart = dc.pieChart('#chart-gender');
    var deviceChart = dc.pieChart('#chart-device');
    var timeChart = dc.compositeChart('#time-chart');
	var goalStartsAllChart = dc.rowChart("#start-chart");
	var goal10StartsChart = dc.rowChart("#start10-chart");
	var goalCompletionsAllChart = dc.rowChart("#completion-chart");
	var goalAbandonRateAllChart = dc.rowChart("#abandon-chart");
	var avgSessionDurationChart = dc.rowChart("#duration-chart");
    // Table
	var dataTable = dc.dataTable("#data-table");

    typeChart
        .width(170)
        .height(170)
        .dimension(userTypeDim)
        .group(userTypeCount)
        .transitionDuration(500)
        .innerRadius(30);

    sourceChart
        .width(170)
        .height(170)
        .dimension(sourceDim)
        .group(sourceCount)
        .transitionDuration(500)
        .innerRadius(30);

    userAgeBracketChart
        .width(170)
        .height(170)
        .dimension(userAgeBracketDim)
        .group(userAgeBracketCount)
        .transitionDuration(500)
        .innerRadius(30);

    genderChart
        .width(170)
        .height(170)
        .dimension(userGenderDim)
        .group(userGenderCount)
        .transitionDuration(500)
        .innerRadius(30);

    deviceChart
        .width(170)
        .height(170)
        .dimension(deviceCategoryDim)
        .group(deviceCategoryCount)
        .transitionDuration(500)
        .innerRadius(30);

    timeChart
        .width(1300)
        .height(300)
        .margins({top: 10, right: 10, bottom: 20, left: 40})
        .dimension(timeDim)
        .group(sessions)
        .transitionDuration(500)
        .elasticY(true)
        .elasticX(true)
        .brushOn(false)
        .x(d3.time.scale().domain(d3.extent(data, function(d) { return d.date; })))
        .legend(dc.legend().gap(5).x(100).y(60))
        .renderHorizontalGridLines(true)
        .compose([dc.lineChart(timeChart)
                        .dimension(timeDim)
                        .colors('blue')
                        .group(sessions, "Sessions")
                        .elasticY(true)
                        .elasticX(true),
                  dc.lineChart(timeChart)
                        .dimension(timeDim)
                        .colors('red')
                        .group(averagebounceRate, "Average Bouncerate")
                        .valueAccessor(function (p) {return p.value.avg})
                        .elasticY(true)
                        .elasticX(true)]);

    goalStartsAllChart
        .width(250)
        .height(530)
        .gap(2)
        .dimension(goalStartsAllDim)
        .group(goalStartsAllSum)
        .elasticX(true)
        .label(function(d) { return ''; })
        .ordering(function(p) { return -p.value })
        .title(function(p) { return d3.round(p.value, 1) })
        .renderTitleLabel(true)
        .rowsCap(20);

    goal10StartsChart
        .width(250)
        .height(530)
        .gap(2)
        .dimension(goal10StartsDim)
        .group(goal10StartsSum)
        .elasticX(true)
        .label(function(d) { return ''; })
        .ordering(function(p) { return -p.value })
        .title(function(p) { return d3.round(p.value, 1) })
        .renderTitleLabel(true)
        .rowsCap(20);

    goalCompletionsAllChart
        .width(250)
        .height(530)
        .gap(2)
        .dimension(goalCompletionsAllDim)
        .group(goalCompletionsAllSum)
        .elasticX(true)
        .label(function(d) { return ''; })
        .ordering(function(p) { return -p.value })
        .title(function(p) { return d3.round(p.value, 1) })
        .renderTitleLabel(true)
        .rowsCap(20);

    goalAbandonRateAllChart
        .width(250)
        .height(530)
        .gap(2)
        .dimension(goalAbandonRateAllDim)
        .group(goalAbandonRateAll)
        .elasticX(true)
        .label(function(d) { return ''; })
        .ordering(function(p) { return +p.value.avg })
        .title(function(p) { return d3.round(p.value.avg, 0) })
        .renderTitleLabel(true)
        .rowsCap(20);
        //.x(d3.scale.linear())
        //.xUnits(dc.units.integers);

    avgSessionDurationChart
        .width(250)
        .height(530)
        .gap(2)
        .dimension(avgSessionDurationDim)
        .group(avgSessionDuration)
        .elasticX(true)
        .label(function(d) { return ''; })
        .ordering(function(p) { return -p.value.avg })
        .title(function(p) { return d3.round(p.value.avg, 0) })
        .renderTitleLabel(true)
        .rowsCap(20);

    dataTable
        .dimension(allDim)
        .size(50)
        .columns([function (d) { return d.userType; },
                  function (d) { return d.source; },
                  function (d) { return d.userAgeBracket; },
                  function (d) { return d.userGender; },
                  function (d) { return d.bounceRate; },
                  function (d) { return d.goalCompletionsAll; },
                  function (d) { return d.avgSessionDuration; }])
        .group(function (d) { return 'dc.js insists on putting a row here so I remove it using JS'; })
        .sortBy(dc.pluck('goalCompletionsAll'))
        .order(d3.descending)
        .on('renderlet', function (table) {
            // each time table is rendered remove nasty extra row dc.js insists on adding
            table.select('tr.dc-table-group').remove();});


    // register handlers
    d3.selectAll('a#all').on('click', function () {
        dc.filterAll();
        dc.renderAll();
    });

    d3.selectAll('a#type').on('click', function () {
        typeChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#source').on('click', function () {
        sourceChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#age').on('click', function () {
        userAgeBracketChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#gender').on('click', function () {
        genderChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#device').on('click', function () {
        deviceChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#start').on('click', function () {
        goalStartsAllChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#start10').on('click', function () {
        goal10StartsChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#completion').on('click', function () {
        goalCompletionsAllChart.filterAll();
        dc.redrawAll();
    });

    d3.selectAll('a#abandon').on('click', function () {
        goalAbandonRateAllChart.filterAll();
        dc.redrawAll();
    });


    d3.selectAll('a#duration').on('click', function () {
        avgSessionDurationChart.filterAll();
        dc.redrawAll();
    });

    dc.renderAll();

};