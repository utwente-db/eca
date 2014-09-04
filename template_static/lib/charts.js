(function($, block) {

// a simple rolling chart with memory
block.fn.rolling_chart = function(config) {
    var options = $.extend({
        memory: 100,
        data: []
    }, config);

    var data = options.data.slice();

    var prepare_data = function() {
        var result = [];

        for(var i in data) {
            result.push([i, data[i]]);
        }

        return [result];
    };

    var plot = $.plot(this.$element, prepare_data(), options.chart);

    this.actions({
        'add': function(e, message) {
            // roll memory
            if(data.length > options.memory) {
                data = data.slice(1);
            }

            data.push(message.value);

            plot.setData(prepare_data());
            plot.setupGrid();
            plot.draw();
        }
    });

    // return element to allow further work
    return this.$element;
}

})(jQuery, block);
