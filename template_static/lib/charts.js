(function($, block) {

// a simple rolling chart with memory
block.fn.rolling_chart = function(config) {
    var options = $.extend({
        memory: 100,
        series: { serie : {label:"serie", color:'black'} }
    }, config);

    var handle_data = function(values) {
        var result = [];

        for(var i in values) {
            result.push([i, values[i]]);
        }
        return result;
    };

    var xo = { series: {
            lines: { show: true },
            points: {
                radius: 3,
                show: true,
                fill: true
            }
        }};

    var plot = $.plot(this.$element, [] , {});

    var reset = function() {
        var result = options.series;
	for(var k in result) {
	    if (result.hasOwnProperty(k)) {
	        result[k].databuffer = [];
	    }
	}
	return result;
    }

    var plot_series = reset();

    var add_to_serie = function(skey,value) {
	var databuffer = plot_series[skey].databuffer;
        if(databuffer.length > options.memory) {
            plot_series[skey].databuffer = databuffer.slice(1);
        }
	databuffer.push(value);
    }

    var redraw = function(serie_value) {
    	    var plot_current = [];
	    var mykeys = Object.keys(plot_series);
	    for(var mykey in mykeys) {
		var skey = mykeys[mykey];
		var serie = plot_series[skey];
		// serie['databuffer'].push(serie_value[skey]);
		add_to_serie(skey,serie_value[skey]);
		serie['data'] = handle_data(serie['databuffer']);
		plot_current.push(serie);
	    }
            plot.setData(plot_current);
            plot.setupGrid();
            plot.draw();
        }

    this.actions({
        'add': function(e, message) {
	    redraw(message.value);
        },
        'reset': function(e, message) {
	    plot_series = reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

//
//
//

// a simple linechart example
block.fn.linechart = function(config) {
    var options = $.extend({
        series_names : ["default"],
        options : {
		series: {	
			lines: {
                		show: true
        		}
    		}
    }}, config);

    // create empty linechart with parameter options
    var plot = $.plot(this.$element, [],options.options);

    // dict containing the labels and values
    var linedata_series = {};

    var initline = function(series) {
	for(var k in series) {
	   linedata_series[series[k]] = {order:k,data:[]};
	}
    }

    initline(options.series_names);

    var addline = function(label, values) {
    	var data;

	if (linedata_series.hasOwnProperty(label))
		data = linedata_series[label].data;
	else
		data = linedata_series['default'].data;
	for(var v in values) {
		data.push(values[v]);
	}
	redraw();
    }

    var setline = function(label, values) {
	if (linedata_series.hasOwnProperty(label))
		linedata_series[label].data = values;
	else
		linedata_series['default'].data = values;
	redraw();
    }

    var redraw = function() {
        var result = [];
    	for(var k in linedata_series) {
	    if (linedata_series.hasOwnProperty(k)) {
	    	var line_serie = linedata_series[k];

 		result.push({label:k,data:line_serie.data});
	    }
	}
        plot.setData(result);
	plot.setupGrid();
        plot.draw();
    }

    var reset = function() {
	initline(options.series_names);
    }

    this.actions({
        'set': function(e, message) {
	    addline(message.series, message.value);
        },
        'add': function(e, message) {
	    addline(message.series, message.value);
        },
        'reset': function(e, message) {
	    reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

//
//
//

// a simple barchart example
block.fn.barchart = function(config) {
    var options = $.extend({
    	series : { "serie1":{
        	data: {"January": 10, "February": 8, "March": 4, "April": 13, "May": 20, "June": 9},
        	label: "serie 1",
        	bars: {
                	show: true,
                	barWidth: 0.2,
                	align: "left"
            	}
       	 
    	},  "serie2":{
        	data: {"January": 10, "February": 8, "March": 4, "April": 13, "May": 20, "June": 9},
        	label: "series 2",
        	bars: {
                	show: true,
                	barWidth: 0.2,
                	align: "center"
            	}
    	},  "serie3":{
        	data: {"January": 10, "February": 8, "March": 4, "April": 13, "May": 20, "June": 9},
        	label: "series 3",
        	bars: {
                	show: true,
                	barWidth: 0.2,
                	align: "right"
            	}
    	}}
    }, config);

    var bar_init = {
            xaxis: {
                mode: "categories",
                tickLength: 0
            }
	}

    var bardata_series = options.series;

    var translate_bar = function() {
        var result = [];
	for(var k in bardata_series) {
	    if (bardata_series.hasOwnProperty(k)) {
		var newserie = jQuery.extend({}, bardata_series[k]);
        	var newdata = [];
		var data = newserie.data;
		for(var l in data) {
	    	    if (data.hasOwnProperty(l)) {
			newdata.push([l,data[l]]);
		    }
		}
		newserie.data = newdata;
		result.push(newserie);
	    }
	}
	return result;
    }

    var plot = $.plot(this.$element, translate_bar(), bar_init);

    var addbar = function(serie_label, category, value) {
	var data = bardata_series[serie_label].data;
	if (data.hasOwnProperty(category))
		data[category] = (data[category] + value);
	else
		data[category] = value;
	redraw();
    }

    var setbar = function(serie_label, category, value) {
	var data = bardata_series[serie_label].data;
	data[category] = value;
	redraw();
    }

    var redraw = function() {
        plot.setData(translate_bar());
	plot.setupGrid();
        plot.draw();
    }

    var reset = function() {
	for(var k in bardata_series) {
	    if (bardata_series.hasOwnProperty(k)) {
		bardata_series[k].data = {};
	    }
	}
    }

    this.actions({
        'set': function(e, message) {
		setbar(message.series,message.value[0],message.value[1]);
        },
        'add': function(e, message) {
		addbar(message.series,message.value[0],message.value[1]);
        },
        'reset': function(e, message) {
		reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

//
//
//

// a simple piechart example
block.fn.piechart = function(config) {
    var options = $.extend({
    	// see: http://www.flotcharts.org/flot/examples/series-pie/
        options : {
		series: {	
			pie: {
                		show: true
        		}
    		}
    }}, config);

    // create empty piechart with parameter options
    var plot = $.plot(this.$element, [],options.options);

    // dict containing the labels and values
    var piedata_dict = {};

    var addpie = function(label, value) {
	if (piedata_dict.hasOwnProperty(label))
		piedata_dict[label] = (piedata_dict[label] + value);
	else
		piedata_dict[label] = value;
	redraw();
    }

    var setpie = function(label, value) {
	piedata_dict[label] = value;
	redraw();
    }

    var redraw = function() {
        var result = [];
	for(var k in piedata_dict) {
	    if (piedata_dict.hasOwnProperty(k)) {
 		result.push({label:k,data:piedata_dict[k]});
	    }
	}
        plot.setData(result);
        plot.draw();
    }

    var reset = function() {
	piedata_dict = {};
    }

    this.actions({
        'set': function(e, message) {
	    setpie(message.value[0],message.value[1]);
        },
        'add': function(e, message) {
	    addpie(message.value[0],message.value[1]);
        },
        'reset': function(e, message) {
	    reset();
	}
    });
    // return element to allow further work
    return this.$element;
}

})(jQuery, block);
