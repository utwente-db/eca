(function($, block) {
block.fn.form = function(config) {
    var options = $.extend({
        target: null,
        callback: function() {}
    }, config);

    // check for sane config
    if(options.target === null) {
        console.log("The 'form' block requires a target option to know where to send the request.");
        return this.$element;
    }

    // set up submit handler
    var $block = this.$element;
    $block.find("input[type='submit']").click(function() {
        var payload = {};

        // handle simple fields
        $block.find("textarea[name], select[name]").each(function() {
            payload[this.name] = this.value;
        });

        // handle the more complex fields
        $block.find("input[name]").each(function() {
            switch($(this).attr('type')) {
                // radio buttons usually have a single selected option per name
                case 'radio':
                    if($(this).prop('checked')) {
                        payload[this.name] = this.value;
                    }
                    break;

                // checkboxes are akin to a bitfield
                case 'checkbox':
                    // build a map of checked values for this name
                    if(typeof payload[this.name] === 'undefined') {
                        payload[this.name] = [];
                    }
                    if($(this).prop('checked')) {
                        payload[this.name].push(this.value);
                    }
                    break;

                // default to storing the value
                default:
                    payload[this.name] = this.value;
                    break;
            }
        });

        // fire and forget the datablob
        $.ajax(options.target,{
            method: 'POST',
            data: JSON.stringify(payload)
        }).then(options.callback);
    });

    return this.$element;
}

})(jQuery, block);
