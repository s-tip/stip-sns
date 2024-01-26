$(function () {
    var now_processing_file = null
    var merged_confirm_data = null
    var merged_files = []
    const CONFIRM_KEYS = ['indicators', 'tas', 'ttps']

    function getCookie(name){
        var cookieValue = null
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';')
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i])
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                    break
                }
            }
        }
        return cookieValue;
    }

    Dropzone.options.bulkUploadPost = {
        paramName: 'attach_',
        autoProcessQueue: false,
        uploadMultiple: false,
        timeout: 60 * 60 * 1000,
        init: function() {
            this.on('processing', function(file) {
                display_processing_animation()
                if (_is_confirm()) {
                    this.options.url = '/feeds/confirm_indicator/'
                }else{
                    this.options.url = '/bulk_upload/post/'
                }
           });
        },
        accept: function(file, done) {
            file.status = Dropzone.QUEUED
        },
        params: function(files, xhr, chunk) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'))
            return _get_params()
        },
        success: function(file, data) {
            remove_processing_animation()
            if(_is_confirm()){
                ret = display_confirm_dialog(data)
                if(_is_merged()){
                    merged_files.push(file)
                    if (ret == false){
                        alert(gettext('No CTI Elements exist'))
                        _merged_post()
                    }
                }else{
                    if (ret == false){
                        alert(gettext('No CTI Elements exist'))
                        _post(null ,[file])
                        _process_queue()
                    }else{
                        now_processing_file = file
                    }
                }
            }else{
                _process_queue()
            }
            this.removeFile(file)
        },
        error: function(file, errorMessage, xhr) {
            remove_processing_animation()
            this.removeFile(file)
            var msg = 'An error occured in S-TIP ('  + xhr.statusText + '/' + xhr.status + ')'
            alert(msg)
        }
    }

    $('#upload-button').click(function(){
        var publication = $("input[name='publication']:checked").val()
        if (publication == 'people') {
           var people = _get_people()
            if (people.length == 0) {
              alert('Select Sharing Accoutns')
              return
            }
        }
        else if (publication == 'group') {
           var group = _get_group()
            if (group.length == 0) {
              alert('Select Sharing Group')
              return
            }
        }

        var dz = _get_dropzone()
        dz.options.parallelUploads = 1
        dz.options.uploadMultiple = false
        if (_is_confirm()) {
             if (_is_merged()){
                merged_confirm_data = {}
                for (const elem of CONFIRM_KEYS){
                    merged_confirm_data[elem] = []
                }
                merged_files = []
            }
        }else{
             if (_is_merged()){
                dz.options.parallelUploads = 10240
                dz.options.uploadMultiple = true
             }
        }
        _init_upload_count()
        _process_queue()
        return
    })

    $('#confirm-compose').click(function () {
        $('#confirm_indicators_modal_dialog').modal('hide')
        var confirm_data = get_confirm_data()
        if(_is_merged()){
            for (const elem of CONFIRM_KEYS){
                merged_confirm_data[elem] = merged_confirm_data[elem].concat(confirm_data[elem])
            }
            _merged_post()
       }else{
            if (now_processing_file != null){
                _post(confirm_data, [now_processing_file])
                _process_queue()
            }
        }
   })

    function _merged_post () {
        if(_is_queued()){
            _process_queue()
        }else{
            _post(merged_confirm_data, merged_files)
        }
        return
    }

    function _get_dropzone () {
        return Dropzone.forElement('#bulk-upload-post')
    }

    function _init_upload_count () {
        var dz = _get_dropzone()
        dz.options.stip_upload_count = 0
        return
    }

    function _increase_upload_count () {
        var dz = _get_dropzone()
        dz.options.stip_upload_count++
        return
    }

    function _get_upload_count () {
        var dz = _get_dropzone()
        return dz.options.stip_upload_count
    }

    function _process_queue () {
        var dz = _get_dropzone()
        dz.processQueue()
        return
    }

    function _is_queued () {
        return _get_queued_files() != 0
    }

    function _get_queued_files () {
        var dz = _get_dropzone()
        return dz.getQueuedFiles()
    }

    function get_csrf_token() {
        return  $('input[name="csrfmiddlewaretoken"]').val()
    }

    function _post (confirm_data, files) {
        var fd = new FormData()
        var post_data = _get_params()
        if (confirm_data != null) {
            post_data['confirm_data'] = JSON.stringify(confirm_data)
        }
        for(var key in post_data){
            var value = post_data[key]
            if(!_is_merged() && _is_confirm()){
                if (key == 'stix_title'){
                    var count = _get_upload_count()
                    value = `${value} ${count}`
                    _increase_upload_count()
                }
            }
            fd.append(key, value)
        }

       var index = 0;
       for (const file_ of files){
           fd.append(`attach_${index}`, file_, file_.name)
           index += 1
       }
        display_processing_animation()

        $.ajax({
            url: '/bulk_upload/post/',
            method: 'post',
            data: fd,
            cache: false,
            async: false,
            processData: false,
            contentType: false,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('X-CSRFToken', get_csrf_token())
            }
        }).done(function (data) {
        }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
            var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
            alert(msg);
        }).always(function () {
            remove_processing_animation()
        })
    }

    function _notify_success () {
        alert('Success!!')
    }

    function _is_confirm () {
        return $('#checkbox-is-confirm-cee').prop('checked')
    }

    function _is_merged () {
        return $('#checkbox-is-single').prop('checked')
    }

    function _get_group () {
        return $("input[name='group']").val()
    }

    function _get_people () {
        var people = []
        jQuery.each($('#account-select-box option:selected'), function () {
            people.push(this.value)
        })
        return people
    }

    function _get_params () {
        var r =  {
            'stix_title': $('#stix-title-text').val(),
            'stix_description': $('#stix-description-text').val(),
            'stix_tlp': $('input[name=TLP]:checked').val().toLowerCase(),
            'publication': $("input[name='publication']:checked").val(),
            'people': _get_people(),
            'group': _get_group(),
            'confirm_data': null
        }
        if (!_is_merged() && !_is_confirm()){
            var count = _get_upload_count()
            r['stix_title'] = `${$('#stix-title-text').val()} ${count}`
            _increase_upload_count()
        }
        return r
    }
})
