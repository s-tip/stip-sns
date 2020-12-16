$(function(){
    function getCookie(name){
        var cookieValue = null;
        if (document.cookie && document.cookie != ''){
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++){
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')){
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    Dropzone.options.uploadFormOtherTypes = {
        paramName: 'input_files',
        parallelUploads: 1024,
        autoProcessQueue: false,
        uploadMultiple: true,
        timeout: 60 * 60 * 1000,
        accept: function(file, done) {
            file.status = Dropzone.QUEUED;
        },
        params: function(files, xhr, chunk) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            var stix_title = $('#stix-title-text').val();
            return {
                'is_merged_single_stix': $('#checkbox-is-single').prop('checked'),
                'stix_title': $('#stix-title-text').val(),
                'stix_description': $('#stix-description-text').val(),
                'stix_tlp': $('input[name=TLP]:checked').val().toLowerCase(),
                'publication': $("input[name='publication']:checked").val(),
                'people': _get_people(),
                'group': _get_group()
            };
        },
        success: function(file) {
            this.removeFile(file);
            alert('Success!!');
        },
        error: function(file, errorMessage, xhr) {
            console.log(errorMessage)
            console.log(xhr)
            var msg = 'An error occured in S-TIP ('  + xhr.statusText + '/' + xhr.status + ')';
            alert(msg);
        },
    };

    $('#upload-button').click(function(){
        if ($('#checkbox-is-confirm-cee').prop('checked')) {
    		alert('Under Construction');
    		return false;
        }

        var publication = $("input[name='publication']:checked").val();
        if (publication == 'people') {
           var people = _get_people();
            if (people.length == 0) {
              alert('Select Sharing Accoutns')
              return;
            }
        }
        else if (publication == 'group') {
           var group = _get_group();
            if (group.length == 0) {
                  alert('Select Sharing Group')
              return;
            }
        }
        Dropzone.forElement("#upload-form-other-types").processQueue();
    });

    function _get_group(){
        return $("input[name='group']").val();
    }

    function _get_people(){
        var people = [];
        jQuery.each($('#account-select-box option:selected'), function () {
            people.push(this.value)
        });
        return people;
    };

});
