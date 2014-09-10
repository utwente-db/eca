(function($, block) {
block.fn.tweets = function(config) {
    this.$element.append('<ol class="tweetlistgadget-contents stream-items js-navigable-stream"></ol>');

    var $list = this.$element.find('ol');

    this.actions(function(e, tweet){
        var newItem = $('<li class="js-stream-item stream-item stream-item expanding-stream-item"></li>');

        var tweetDiv = $('<div class="tweet original-tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable js-original-tweet"></div>');
        var contentDiv = $('<div class="content"></div>');
        var headerDiv = $('<div class="stream-item-header"></div>');

        // Build a tag image and header:
        var aTag1 = $('<a class="account-group js-account-group js-action-profile js-user-profile-link js-nav"></a>');
        aTag1.attr("href", "http://twitter.com/" + tweet.user.screen_name);

        var avatar = $("<img>").addClass("avatar js-action-profile-avatar");
        avatar.attr("src", tweet.user.profile_image_url);
        aTag1.append(avatar);
        aTag1.append($('<strong class="fullname js-action-profile-name show-popup-with-id">' + tweet.user.name + '</strong>'));
        aTag1.append($('<span>&rlm;&nbsp;</span>'));
        aTag1.append($('<span class="username js-action-profile-name"><s>@</s><b>' + tweet.user.screen_name + '</b></span>'));
        headerDiv.append(aTag1);

        // Build timestamp:
        var smallTag = $('<small class="time"></small>');
        var aTag2 = $('<a class="tweet-timestamp js-permalink js-nav"></a>');
        aTag2.attr("href", "http://twitter.com/" + tweet.user.screen_name + "/status/" + tweet.id);
        aTag2.attr("title", tweet.created_at);
        aTag2.append($('<span class="_timestamp js-short-timestamp js-relative-timestamp">' + tweet.created_at + '</span>'));
        smallTag.append(aTag2);
        headerDiv.append(smallTag);
        contentDiv.append(headerDiv);

        // Build contents:
        var pTag = $('<p class="js-tweet-text tweet-text">' + tweet.text + '</p>');
        contentDiv.append(pTag);

        // Build outer structure of containing divs:
        tweetDiv.append(contentDiv);
        newItem.append(tweetDiv);
        
        
        $list.prepend(newItem);

        //FIXME hardcoded backlog
        if ($list.children().size() > 4) {
            $list.children().last().remove();
        }
    });

    return this.$element;
};
})(jQuery, block);
