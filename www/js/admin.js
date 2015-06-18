var $imageCanvas;
var $imageWrapper;
var $userModal;
var $userButtons;
var $userNotice;
var $buttonWrappers;
var $qualityButtons;
var $alternateUserForm;
var $window;
var $footer;
var $navbar;
var $spinner;
var $love;
var $hate;

var buttonsEnabled;

var onLoadImage = function(data) {
    if (data.image_url) {
        var $newImg = $('<img class="img-responsive">');
        var maxHeight = $window.height() - $footer.outerHeight() - $header.height() - parseInt($imageWrapper.css('margin-top'));
        $newImg
          .attr('src', data.thumb_url)
          .attr('data-image-url', data.image_url)
          .css('max-height', maxHeight);
        $imageCanvas.html($newImg).hide();
        imagesLoaded($newImg, function() {
            enableButtons();
            $imageCanvas.fadeIn();
        });
        loadImage(1);
    } else {
        $imageCanvas.html('<h1 class="text-center">No moar images. Awesome!</h1>').fadeIn();
        $spinner.hide();
    }
}

var cacheImage = function(data) {
    var image = new Image();
    image.src = data.thumb_url;
}

var disableButtons = function() {
    buttonsEnabled = false;
    $qualityButtons.attr('disabled', 'disabled');
}

var enableButtons = function() {
    buttonsEnabled = true;
    $qualityButtons.attr('disabled', false);
}

var loadImage = function(offset) {
    var offset = offset || 0;
    var params = {
        url: 'get-image/' + offset
    }
    if (!offset) {
        params.success = onLoadImage;
    } else {
        params.success = cacheImage;
    }
    $.ajax(params);
}

var loadSelectUser = function(e) {
    var user = $.cookie('graeae_user');
    if (!user) {
        $userModal.modal('show');
    }
}

var selectUser = function(e) {
    var user = $(this).text();
    $.cookie('graeae_user', user);
    drawUserNotice();
    $userModal.modal('hide');
    loadImage();
}

var selectAlternateUser = function(e) {
    $.cookie('graeae_user', $(this).find('input').val());
    drawUserNotice();
    $userModal.modal('hide');
    loadImage();
    e.preventDefault();
}

var drawUserNotice = function(e) {
    var user = $.cookie('graeae_user');
    if (user) {
        var html = JST.user_notice({
            user: user
        });
        $userNotice.html(html);
    }
}

var evaluateImage = function(e, quality) {
    var quality = quality||$(this).data('quality');
    var image_url = $imageCanvas.find('img').data('image-url');

    $imageCanvas.fadeOut();
    if (quality == 'love') {
        $love.css('visibility', 'visible')
    } else {
        $hate.css('visibility', 'visible')
    }
    setTimeout(function() {
        saveImage(quality, image_url)
    }, 300);
}

var saveImage = function(quality, image_url) {
    $hate.css('visibility', 'hidden');
    $love.css('visibility', 'hidden');

    $.ajax({
        url: 'save-image/',
        method: 'POST',
        data: {
            quality: quality,
            image_url: image_url,
            evaluator: $.cookie('graeae_user')
        },
        success: function(data) {
            loadImage();
        },
    });
}

var onDocumentLoad = function(e) {
    $window = $(window);
    $imageCanvas = $('#image-canvas');
    $imageWrapper = $('.image-wrapper');
    $userModal = $('#user-modal');
    $userButtons = $('.select-user');
    $userNotice = $('#user-notice');
    $qualityButtons = $('.quality-button');
    $alternateUserForm = $('#alternate-user');
    $footer = $('.footer');
    $header = $('.header');
    $spinner = $('.spinner');
    $love = $('#love');
    $hate = $('#hate');

    $userButtons.on('click', selectUser);
    $alternateUserForm.on('submit', selectAlternateUser);
    $qualityButtons.on('click', evaluateImage);

    // Bind keyboard shortcuts
    $(document).keydown(function(e) {
        if (e.keyCode == 76) {
            evaluateImage(e, 'love');
        }

        if (e.keyCode == 72) {
            evaluateImage(e, 'hate');
        }
    });

    loadSelectUser();
    drawUserNotice();
    loadImage();
}

$(onDocumentLoad);
