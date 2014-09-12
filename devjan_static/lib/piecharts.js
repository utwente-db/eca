(function($, block) {

// a simple piechart example
block.fn.piechart = function(config) {
    var options = $.extend({
    	// see: http://www.flotcharts.org/flot/examples/series-pie/
        pie_options : {
		series: {	
			pie: {
                		show: true
        		}
    		}
    }}, config);

    // create empty piechart with parameter options
    var plot = $.plot(this.$element, [],options.pie_options);

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
