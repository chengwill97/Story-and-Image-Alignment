$(function() {
    $('#inputImages').change(function(){

        if (this.files.length == 0) {
            $('.imageNameScroll').hide();
        } else {
            $('.imageNameScroll').show();
        }

        $('#imageNames').html('');

        $('#imageNames').append('<li class="list-group-item active d-flex justify-content-between align-items-center"> Images Uploaded <span class="badge badge-secondary badge-pill">'
        + this.files.length
        + '</span></li>');

        for(var i = 0 ; i <= this.files.length ; i++){
            if(typeof this.files[i] !== 'undefined') {
                var filename = this.files[i].name;
                $('#imageNames').append('<li class="list-group-item">' + filename + '</li>');
            }
        }

    });
});

$(function() {
    $('#inputText').change(function(){

        if (this.files.length == 0) {
            $('.textNameScroll').hide();
        } else {
            $('.textNameScroll').show();
        }

        $('#textNames').html('');

        $('#textNames').append('<li class="list-group-item active d-flex justify-content-between align-items-center"> Text Files Uploaded <span class="badge badge-secondary badge-pill">'
        + this.files.length
        + '</span></li>');

        for(var i = 0 ; i <= this.files.length ; i++){
            if(typeof this.files[i] !== 'undefined') {
                var filename = this.files[i].name;
                $('#textNames').append('<li class="list-group-item">' + filename + '</li>');
            }
        }

    });
});
