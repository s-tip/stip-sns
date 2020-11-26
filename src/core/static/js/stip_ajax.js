const empty_gif = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';
const re = /^[0-9]{6}$/;
const suggest_limit = 5
const suggest_min_length = 2


$(document)
  .ajaxError(function (e, xhr, opts, error) {
    console.log('AjaxError: ' + error);
    if (error == 'Unauthorized') {
      alert('Session Timeout!!. Back to the Login Page.')
      window.location.href = '/login'
    } else {
      alert(error);
    }
  });

function enable_2fa_submit() {
  var auth_code = $('#authentication_code').val();
  if (!re.test(auth_code)) {
    $('.err_msg').text("Please enter a 6 digits integer.");
    return false;
  }

  $('.err_msg').text('');

  $.ajax({
    url: '/settings/enable_2fa/',
    type: 'POST',
    data: $('#enable_2fa_form').serialize(),
    dataType: 'json',
    timespan: 1000 * 10,
  })
    .done(function (data, textStatus, jqXHR) {
      if (data.status == 'OK') {
        $('#enable_2fa_modal').modal('hide');
      } else {
        $('.err_msg').text(data.error_msg);
      }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      $('.err_msg').text(jqXHR.statusText);
    });
}

function enable_2fa() {
  $('.err_msg').text('');
  $('#qrcode_img').attr('src', empty_gif);
  $('#secret').text('');
  $('#authentication_code').val('');
  $('#enable_2fa_modal').modal();

  $.ajax({
    url: '/settings/get_2fa_secret/',
    type: 'GET',
    data: null,
    dataType: 'json',
    timespan: 1000 * 10,
  })
    .done(function (data, textStatus, jqXHR) {
      var secret = data.secret;
      var qrcode_base64 = 'data:image/png;base64,' + data.qrcode;
      $('#qrcode_img').attr('src', qrcode_base64);
      $('#secret').text(secret);
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      $('.err_msg').text(jqXHR.statusText);
    });
}

function disable_2fa() {
  $('.err_msg').text('');
  $('#disable_2fa_modal').modal();
}

function disable_2fa_submit() {
  $('.err_msg').text('');
  $.ajax({
    url: '/settings/disable_2fa/',
    type: 'POST',
    data: $('#disable_2fa_form').serialize(),
    dataType: 'json',
    timespan: 1000 * 10,
  })
    .done(function (data, textStatus, jqXHR) {
      if (data.status == 'OK') {
        $('#disable_2fa_modal').modal('hide');
      } else {
        $('.err_msg').text(data.error_msg);
      }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      $('.err_msg').text(jqXHR.statusText);
    });
}

$('#id_enable_2fa').change(function () {
  if ($(this).prop('checked')) {
    enable_2fa();
  } else {
    disable_2fa();
  }
});

$('#enable_2fa_modal').on('shown.bs.modal', function () {
  $('#authentication_code').focus();
})

$('#enable_2fa_form').submit(function (event) {
  event.preventDefault();
  enable_2fa_submit();
});

$('#enable_cancel_btn').click(function () {
  $('#enable_2fa_modal').modal('hide');
  $('#id_enable_2fa').prop('checked', false);
});

$('#enable_close_btn').click(function () {
  $('#enable_2fa_modal').modal('hide');
  $('#id_enable_2fa').prop('checked', false);
});

$('#disable_2fa_modal').on('shown.bs.modal', function () {
  $('#disable_no_btn').focus();
})

$('#disable_2fa_form').submit(function (event) {
  event.preventDefault();
  disable_2fa_submit();
});

$('#disable_no_btn').click(function () {
  $('#disable_2fa_modal').modal('hide');
  $('#id_enable_2fa').prop('checked', true);
});

$('#disable_close_btn').click(function () {
  $('#disable_2fa_modal').modal('hide');
  $('#id_enable_2fa').prop('checked', true);
});

function start_suggest(sg, inputid, suggestid) {
  sg = new Suggest.LocalMulti(
    inputid,
    suggestid,
    [],
    {
      interval: 500,
      dispMax: 5,
      listTagName: "div",
      prefix: true,
      ignoreCase: true,
      highlight: false,
      display: false,
      classMouseOver: "over",
      classSelect: "select",
      delim: " "
    });
  sg._search = function (text) { return []; };
  sg.hookBeforeSearch = function (text) {
    if (sg == null) { return []; }
    if (text.length < 2) { return []; }
    if (text[0] != "#") { return []; }
    var inputElement = $("#" + inputid);
    var suggestElement = $("#" + suggestid);
    var caretPosition = Measurement.caretPos(inputElement);
    var scroll = $(window).scrollTop();
    suggestElement.css({ "top": (caretPosition.top - scroll + 25) });
    suggestElement.css({ "left": caretPosition.left });
    sg.candidateList = [];
    url = "/feeds/tags/?word=" + encodeURIComponent(text);
    $.ajax({
      url: url,
      type: "GET",
      datatype: "json",
      timespan: 5000
    }).done(function (data, textStatus, jqXHR) {
      sg.candidateList = data;
      var list_count = sg.candidateList.length;
      sg.suggestIndexList = [];
      if (list_count > 0) {
        for (i = 0; i < list_count; i++) {
          sg.suggestIndexList.push(i);
        }
        sg.createSuggestArea(sg.candidateList);
      }
    }).fail(function (jqXHR, textStatus, errorThrown) {
      return []
    })
  };
};

var search_sg = null;
window.addEventListener ?
  window.addEventListener('load', start_suggest(search_sg, "search-text", "search-suggest"), false) :
  window.attachEvent('onload', start_suggest(search_sg, "search-text", "search-suggest"));

var title_sg = null;
window.addEventListener ?
  window.addEventListener('load', start_suggest(title_sg, "compose-title", "title-suggest"), false) :
  window.attachEvent('onload', start_suggest(title_sg, "compose-title", "title-suggest"));

var content_sg = null;
window.addEventListener ?
  window.addEventListener('load', start_suggest(content_sg, "compose-content", "content-suggest"), false) :
  window.attachEvent('onload', start_suggest(content_sg, "compose-content", "content-suggest"));
