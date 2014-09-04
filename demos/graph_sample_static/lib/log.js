(function($, block) {
block.fn.log = function(config) {
    this.$element.addClass('block log').append('<ul>');

    this.actions(function(e, message){
        $ul = $('ul:first-child', this);
        $ul.append('<li>');
        $ul.find("> li:last-child").text(message.text);
        $(this).scrollTop(1000000);
    });

    return this.$element;
};
})(jQuery, block);
