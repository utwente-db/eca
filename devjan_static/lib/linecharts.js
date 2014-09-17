(function($, block) {

// a simple linechart example
block.fn.linechart = function(config) {
    var options = $.extend({
        line_series : ["default"],
        line_options : {
		series: {	
			lines: {
                		show: true
        		}
    		}
    }}, config);

    // create empty linechart with parameter options
    var plot = $.plot(this.$element, [],options.line_options);

    // dict containing the labels and values
    var linedata_series = {};

    var initline = function(series) {
	for(var k in series) {
	   linedata_series[series[k]] = {order:k,data:[]};
	}
    }

    initline(options.line_series);

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
	initline(options.line_series);
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

})(jQuery, block);
