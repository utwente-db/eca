/*
Event stream handling.

See https://developer.mozilla.org/en-US/docs/Web/API/EventSource for a more
comprehensive explanation.
*/

events = {};

(function($, exports) {
    var e = new EventSource('/events');

    exports.connect = function(name, elements) {
        // wrap to allow selector, jQuery object and DOM nodes
        var $elements = $(elements);

        // add listener that triggers events in DOM
        this.listen(name, function(message) {
            $elements.trigger('server-event', [message]);
        });
    };

    exports.listen = function(name, callback) {
        // add event listener to event stream
        e.addEventListener(name, function(m) {
            try {
                var message = JSON.parse(m.data);
            } catch(err) {
                console.exception("Received malformed message: ",err);
                return;
            }

            callback(message);
        });
    };
})(jQuery, events);


