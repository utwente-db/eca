(function($, block) {

// a simple rolling chart with memory
block.fn.rolling_chart = function(config) {
    // combine default configuration with user configuration
    var options = $.extend({
        memory: 100,
        data: []
    }, config);

    // maintain state for this block
    var data = options.data.slice();

    // function to project our state to something the library understands
    var prepare_data = function() {
        var result = [];

        for(var i in data) {
            result.push([i, data[i]]);
        }

        return [result];
    };

    // initial setup of library state (also builds necessary HTML)
    var plot = $.plot(this.$element, prepare_data(), options.chart);


    // register actions for this block
    this.actions({
        'add': function(e, message) {
            // roll memory
            if(data.length > options.memory) {
                data = data.slice(1);
            }

            // update block state
            data.push(message.value);

            // update HTML
            plot.setData(prepare_data());
            plot.setupGrid();
            plot.draw();
        }
    });

    // return element to allow further work
    return this.$element;
}

})(jQuery, block);
