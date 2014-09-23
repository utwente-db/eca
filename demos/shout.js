/*
 * This file is the demo for a block definition. For more information
 * see:
 * https://github.com/utwente-db/eca/wiki/Extending:-Creating-Your-Own-Blocks
 *
 */

(function($, block) {

block.fn.shout = function(config) {
    // handle configuration
    var options = $.extend({
        size: '64pt',
        text: 'RED',
        color: 'red'
    }, config);

    // create HTML representation
    var $el = $('<span></span>').appendTo(this.$element);
    $el.css('font-size', options.size);

    // create HTML element for display
    var data = {
        text: options.text,
        color: options.color
    }

    // update function to update element
    var update = function() {
        $el.text(data.text+'!').css('color', data.color);
    }

    // invoke update to initialise the display
    update();

    // register actions
    this.actions({
        word: function(e, message) {
            data.text = message.text;
            update();
        },
        color: function(e, message) {
            data.color = message.color;
            update();
        }
    });

    // return the element for further work
    return this.$element;
}

})(jQuery, block);
