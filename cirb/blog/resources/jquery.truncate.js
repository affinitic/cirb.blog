(function($) {
  $.fn.truncate = function(length, options) {
    options = jQuery.extend( {
      more: 'more',
      elipsis: '...'
    }, options);

    function moreLink() {
      return '<p><a class="morelink" href="#">' + options.more + '</a></p>';
    }

    function stripEmptyTags(str) {
      var emptyTagRegex = /<(\w+)[^>]*>\s*[<br>|<br/>|<br />]{0,}<\/\1>/g;
      str = str.replace(emptyTagRegex, '');
      if(emptyTagRegex.test(str))
        return stripEmptyTags(str);
      return str;
    }

    function stripTrailingBreakSpaces(str) {
      console.log(str);
      var regex = /[<br>|<br/>|<br />]{1,}(<\/\w+>)?$/;
      console.log(regex.test(str));
      return str.replace(regex, '');
    }

    return this.each(function(i, el) {
      el = $(el);
      var htmlRegex = /<\/?[^<>]*\/?>/gi,
          origStr = $.trim(el.html()),
          str = origStr.split(htmlRegex).join('');
      if(str.length < length)
        return;
      var truncateAt = length, tags = {}, match = null, end = origStr.length, classes = el.attr('class') || 'truncate';
      //$(el).wrap('<div></div>').attr('class', '').parent().attr('class', classes);
      if(str.charCodeAt(truncateAt) != 32) {
        var nextSpaceIndex = str.substring(truncateAt).indexOf(' ');
        if(nextSpaceIndex < 0)
          return;
        truncateAt = truncateAt + str.substring(truncateAt).indexOf(' ');
      }
      var truncated = str.substring(0, truncateAt);
      while ((match = htmlRegex.exec(origStr)) !== null){
        tags[match.index] = match[0];
      }

      for(var tag in tags) {
        truncated = [truncated.substring(0, tag), tags[tag], truncated.substring(tag)].join('');
      }

      truncated = stripEmptyTags(truncated)
      truncated = stripTrailingBreakSpaces(truncated).replace(/(<\/\w+>)?$/, options.elipsis + '$1');

      el.parent().append(moreLink());
      el.addClass('less').html(truncated);
      var articleurl = el.parent().find('h1').find('a').attr('href');
      el.parent().find('.morelink').attr('href', articleurl);
    });
  };
})(jQuery);

