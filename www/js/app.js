// Global jQuery references
var $metricToggleButtons = null;

var onToggleMetricView = function(e) {
    var $el = $(this)
    var targetSelector = $el.parents('.btn-group').data('toggle-target');
    var $target = $(targetSelector);
    var toggleState = $el.find('input').attr('value');
    if (toggleState == 'distribution') {
        $target.find('.value').hide();
        $target.find('.histogram').show();
    } else {
        $target.find('.value').show();
        $target.find('.histogram').hide();
    }
}

var onDocumentLoad = function(e) {
    $metricToggleButtons = $('.metric-toggle .btn');

    $metricToggleButtons.on('click', onToggleMetricView);
}

$(onDocumentLoad);
