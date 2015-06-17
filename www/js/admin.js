var $imageCanvas;
var $userModal;
var $userButtons;
var $userNotice;
var $buttonWrappers;
var $qualityButtons;
var $alternateUserForm;

var setButtonWrapperHeight = function() {
    var height = $imageCanvas.height();
    $buttonWrappers.height(height);
    $buttonWrappers.show();
}

var onLoadImage = function(data) {
    if (data.image_url) {
        var $newImg = $('<img class="img-responsive">');
        $newImg.attr('src', data.image_url);
        $imageCanvas.html($newImg);
        imagesLoaded($newImg, function() {
            setButtonWrapperHeight();
        });
    } else {
        $imageCanvas.html('<h1>No moar images. Awesome!</h1>');
        setButtonWrapperHeight();
    }
}

var loadImage = function(e) {
    $.ajax({
        url: 'get-image/',
        success: onLoadImage,
    });
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

var evaluateImage = function(e) {
    var quality = $(this).data('quality');
    var image_url = $imageCanvas.find('img').attr('src');
    $.ajax({
        url: 'save-image/',
        method: 'POST',
        data: {
            quality: quality,
            image_url: image_url,
            evaluator: $.cookie('graeae_user')
        },
        success: loadImage
    });
}

var onDocumentLoad = function(e) {
    $imageCanvas = $('#image-canvas');
    $userModal = $('#user-modal');
    $userButtons = $('.select-user');
    $userNotice = $('#user-notice');
    $buttonWrappers = $('.button-wrapper');
    $qualityButtons = $('.quality-button');
    $alternateUserForm = $('#alternate-user');

    $userButtons.on('click', selectUser);
    $alternateUserForm.on('submit', selectAlternateUser);
    $qualityButtons.on('click', evaluateImage);

    loadSelectUser();
    drawUserNotice();
    loadImage();
}

$(onDocumentLoad);
