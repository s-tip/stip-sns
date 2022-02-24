var title_count = 0;
var content_count = 0;

$(function () {
  var page_title = $(document).attr("title");
  var screen_type = $("body").data("screen-type");
  var is_post = false

  //新規投稿とキャンセルを入れ替える
  function toggle_new_cancel_button() {
    $('#button-new').toggle();
    $('#button-cancel').toggle();
  }

  function hide_stream_update() {
    $(".stream-update").hide();
    $(".stream-update .new-posts").text("");
    $(document).attr("title", page_title);
  };

  $("body").keydown(function (evt) {
    var keyCode = evt.which ? evt.which : evt.keyCode;
    //Nで開く
    if (keyCode == 78) {
      var focus = $(':focus')[0];
      //どこにもフォーカスが当たっていない場合はひらく
      if (focus == undefined) {
        $(".btn-compose").click();
        return false;
      }
      //textarea/text field中のNはフックしない
      var focus_type = focus.type;
      if (focus_type == 'textarea') {
        return true;
      }
      if (focus_type == 'text') {
        return true;
      }
      if (focus_type == 'search') {
        return true;
      }
      $(".btn-compose").click();
      return false;
    }
  });

  $("#compose-form textarea[name='post']").keydown(function (evt) {
    var keyCode = evt.which ? evt.which : evt.keyCode;
    //Ctrl + P
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13)) {
      $(".btn-post").click();
    }
  });

  $(".btn-compose").click(function () {
    //New button→Cancel button
    toggle_new_cancel_button();
    if ($(".compose").hasClass("composing")) {
      $(".compose").removeClass("composing");
      $(".compose").slideUp();
    }
    else {
      $(".compose").addClass("composing");

      //compose領域の初期化
      //Multi Language
      $("#compose-multi-language").prop('checked', false);

      // compose-title, compose-content を最初の 1つになるまで削除
      while ($(".compose-title-div").length > 1) {
        $(".compose-title-div:last").remove();
      }
      while ($(".compose-content-div").length > 1) {
        $(".compose-content-div:last").remove();
      }
      // 言語設定、 + - アイコン非表示
      compose_stix2_uncheked();

      //title
      $(".compose-title").val("");
      var screen_name = $(".compose").attr("screen_name");
      set_title_value(screen_name);

      //text
      $(".compose textarea").val("");
      //referred-url
      $("#referred-url").val("");

      //TLP
      //一旦すべてクリアする
      $('.label-tlp').removeClass("active");
      $('.radio-tlp').prop("checked", false);

      var tlp = $(".compose").attr("tlp");
      //TLPに合わせてactiveをつける
      if (tlp == "RED") {
        $('#label-tlp-red').addClass("active");
        $('#radio-tlp-red').prop("checked", true);
      } else if (tlp == "AMBER") {
        $('#label-tlp-amber').addClass("active");
        $('#radio-tlp-amber').prop("checked", true);
      } else if (tlp == "GREEN") {
        $('#label-tlp-green').addClass("active");
        $('#radio-tlp-green').prop("checked", true);
      } else {
        $('#label-tlp-white').addClass("active");
        $('#radio-tlp-white').prop("checked", true);
      }

      //添付ファイル
      var attach_file_div = $('#attach-file-div');
      var append_div = $('<div id="attach-file-div"></div>');
      append_div.append(attach_file_div.html());
      //upload fromを空にした後追加(最初と同じ状態にする)
      $('#attach-file-root').empty()
      $('#attach-file-root').append(append_div);

      //Sharing Rangeは With All
      $('#publication-all').prop("checked", true);

      //peoples詳細設定初期化
      $('#account-select-box').multiSelect('deselect_all');

      //他の2つの詳細設定は閉じる
      $("#publication-people-div").slideUp(slideTime);
      $("#publication-group-div").slideUp(slideTime);

      //Anonymous Post check
      $('#check-annonymous').prop("checked", false);

      $(".compose").slideDown(400, function () {
        //$(".compose textarea").focus();
      });
    }
  });

  $(".btn-cancel-compose").click(function () {
    toggle_new_cancel_button();
    $(".compose").removeClass("composing");
    $(".compose").slideUp();
  });

  //STIX 2.x 投稿の title 情報取得
  function get_stix2_title_information() {
    var stix2_titles = [];
    jQuery.each($('.compose-title'), function () {
      var language = $(this).parents('.compose-title-div').find('.compose-title-language-select').val();
      var title_info = { 'title': this.value, 'language': language };
      stix2_titles.push(title_info);
    });
    return stix2_titles;
  };

  //STIX 2.x 投稿の content 情報取得
  function get_stix2_content_information() {
    var stix2_contents = [];
    jQuery.each($('.compose-content'), function () {
      var language = $(this).parents('.compose-content-div').find('.compose-content-language-select').val();
      var content_info = { 'content': this.value, 'language': language };
      stix2_contents.push(content_info);
    });
    return stix2_contents;
  };

  //Mult Language 投稿か？
  function is_multi_language() {
    return $('#compose-multi-language').prop('checked');
  };

  //STIX 2.x 投稿の language duplicate check
  function is_duplicate_languages(values) {
    var ret = false;
    var languages = [];
    jQuery.each(values, function (index) {
      var value = values[index];
      var language = value['language'];
      if (languages.indexOf(language) >= 0) {
        ret = true;
        return;
      }
      languages.push(language)
    });
    return ret;
  };

  function confirm_indicators() {
    //複数ファイル添付対応
    var counter = 0;
    jQuery.each($('.file-attach'), function () {
      if (this.files.length > 0) {
        var name = 'attach_' + counter;
        this.name = name;
        counter++;
      }
    });

    //フィールドにファイルを追加したのでajax送信方法を追加
    var fd = new FormData($('#compose-form').get(0));

    fd.append('multi_language', is_multi_language());
    //複数ある content が一つでも長さ 0 の場合はエラー
    var is_zero_content = false;
    jQuery.each($('.compose-content'), function () {
      if ($(this).val().length == 0) {
        is_zero_content = true;
        return false;
      }
    });
    if (is_zero_content == true) {
      alert(gettext('Cannot to post it due to 0-length content.'));
      return;
    }

    //複数ある content 情報から言語情報などをまとめる
    var titles = get_stix2_title_information();
    var contents = get_stix2_content_information()
    if (is_duplicate_languages(titles) == true) {
      alert(gettext('Duplicate Same Language Title'));
      return;
    }
    if (is_duplicate_languages(contents) == true) {
      alert(gettext('Duplicate Same Language Content'));
      return;
    }
    fd.append('stix2_titles', JSON.stringify(titles));
    fd.append('stix2_contents', JSON.stringify(contents));

    //publicationsによって変更する
    var publication = $("#compose-form input[name='publication']:checked").val();
    var people = [];
    if (publication == 'people') {
      jQuery.each($('#account-select-box option:selected'), function () {
        people.push(this.value)
      });
      if (people.length == 0) {
        alert('Select Sharing Accoutns')
        return;
      }
      fd.append('people', people);
    }
    else if (publication == 'group') {
      if ($("#compose-form input[name='group']").val().length == 0) {
        alert('Select Sharing Group')
        return;
      }
    }
    var button = $(".btn-post");

    display_processing_animation();
    is_post = true
    $.ajax({
      url: '/feeds/confirm_indicator/',
      method: 'post',
      data: fd,
      processData: false,
      contentType: false,
      cache: false,
    }).done(function (data) {
      //indicators の要素があれば modal dialog 表示
      var table_datas = [];

      // indicators あれば追加する
      if (Object.keys(data['indicators']).length > 0) {
        for (file_name in data['indicators']) {
          if (!(file_name in table_datas)) {
            table_datas[file_name] = []
          }
          table_datas[file_name][TABLE_ID_INDICATORS] = data['indicators'][file_name]
        }
      }
      // ttps あれば追加する
      if (Object.keys(data['ttps']).length > 0) {
        for (file_name in data['ttps']) {
          if (!(file_name in table_datas)) {
            table_datas[file_name] = []
          }
          table_datas[file_name][TABLE_ID_TTPS] = data['ttps'][file_name]
        }
      }
      // tas あれば追加する
      if (Object.keys(data['tas']).length > 0) {
        for (file_name in data['tas']) {
          if (!(file_name in table_datas)) {
            table_datas[file_name] = []
          }
          table_datas[file_name][TABLE_ID_TAS] = data['tas'][file_name]
        }
      }
      if (screen_type == 'search') {
        fd.append('query_string', document.getElementById('query_string').value);
        fd.append('screen_name', document.getElementById('screen_name').value);
      }
      make_extract_tables(table_datas);
      is_post = false
      $('#confirm_indicators_modal_dialog').modal();

    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
    }).always(function () {
      remove_processing_animation();
      is_post = false
    });
  };

  //Multi Language 出力チェックボックスのステータス変更時
  $("#compose-multi-language").click(function () {
    if ($(this).prop('checked') == true) {
      $('.compose-title-language-div').css('display', 'inline-block');
      $('.compose-title-plus-button').css('display', 'inline-block');
      $('.compose-title-remove-button').css('display', 'inline-block');
      $('.compose-content-language-div').css('display', 'inline-block');
      $('.compose-content-plus-button').css('display', 'inline-block');
      $('.compose-content-remove-button').css('display', 'inline-block');

    } else {
      compose_stix2_uncheked();
    }
  });

  function compose_stix2_uncheked() {
    $('.compose-title-language-div').css('display', 'none');
    $('.compose-title-plus-button').css('display', 'none');
    $('.compose-title-remove-button').css('display', 'none');
    $('.compose-content-language-div').css('display', 'none');
    $('.compose-content-plus-button').css('display', 'none');
    $('.compose-content-remove-button').css('display', 'none');
  };

  //title の plus ボタンクリック
  $(document).on("click", ".compose-title-plus-button", function () {
    title_count++;
    var compose_title_div = $('.compose-title-div').clone(true);
    var id_name = "compose-title-" + title_count
    compose_title_div.find("input.compose-title").attr("id", id_name)
    compose_title_div.find("label").attr("for", id_name)
    var append_div = $('<div class="row compose-title-div"><br/></div>');
    append_div.append(compose_title_div.html());
    $('#compose-title-root-div').append(append_div);
    // stip_ajax.js start_suggset()
    start_suggest(id_name, "suggest-block");
  });

  //title の remove ボタンクリック
  $(document).on("click", ".compose-title-remove-button", function () {
    // 1 つは必ず残す
    if ($(".compose-title-div").length < 2) {
      return;
    }
    //対象の compose-title-div を除去する
    $(this).parents(".compose-title-div").remove();
  });

  //content の plus ボタンクリック
  $(document).on("click", ".compose-content-plus-button", function () {
    content_count++;
    var compose_content_div = $('.compose-content-div').clone(true);
    var id_name = "compose-content-" + content_count
    compose_content_div.find("textarea.compose-content").attr("id", id_name)
    compose_content_div.find("label").attr("for", id_name)
    var append_div = $('<div class="row compose-content-div"><br/></div>');
    append_div.append(compose_content_div.html());
    $('#compose-content-root-div').append(append_div);
    // stip_ajax.js start_suggset()
    start_suggest(id_name, "suggest-block");
  });

  //content の remove ボタンクリック
  $(document).on("click", ".compose-content-remove-button", function () {
    // 1 つは必ず残す
    if ($(".compose-content-div").length < 2) {
      return;
    }
    //対象の compose-content-div を除去する
    $(this).parents(".compose-content-div").remove();
  });


  //新規投稿の投稿ボタン押下時
  $(".btn-post").click(function () {
    // indicator 確認後投稿へ
    confirm_indicators();
  });

  //確認画面の投稿ボタン押下時
  $('#confirm-compose').click(function () {
    $('#confirm_indicators_modal_dialog').modal('hide');
    var f = $('#compose-form');
    var button = $(".btn-post");

    //各々の confirm-item-tr ごとに checkbox がついていたら form の引数に追加する
    var confirm_data = get_confirm_data();

    //フィールドにファイルを追加したのでajax送信方法を追加
    var fd = new FormData($('#compose-form').get(0));
    fd.append('confirm_data', JSON.stringify(confirm_data));
    //複数ある content 情報から言語情報などをまとめる
    fd.append('multi_language', is_multi_language());
    fd.append('stix2_titles', JSON.stringify(get_stix2_title_information()));
    fd.append('stix2_contents', JSON.stringify(get_stix2_content_information()));
    if (screen_type == 'search') {
      fd.append('query_string', document.getElementById('query_string').value);
      fd.append('screen_name', document.getElementById('screen_name').value);
    }
    display_processing_animation();
    is_post = true
    $.ajax({
      url: '/feeds/post/',
      method: 'post',
      data: fd,
      processData: false,
      contentType: false,
      cache: false,
    }).done(function (data) {
      $("ul.stream").prepend(data);
      $(".compose").slideUp();
      $(".compose").removeClass("composing");
      hide_stream_update();
      toggle_new_cancel_button();
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
    }).always(function () {
      remove_processing_animation();
      button.prop('disabled', false);
      is_post = false
    });
  });



  function add_file_select() {
    var attach_file_div = $('#attach-file-div');
    var append_div = $('<div id="attach-file-div"></div>');
    append_div.append(attach_file_div.html());
    //upload fromを追加する
    $('#attach-file-root').append(append_div);
  };

  //ゴミ箱ボタンclick
  $(document).on("click", ".btn-remove", function () {
    //upload_formとtextを削除する
    var attach_file_div = $(this).parent().parent().parent()
    var file_attach_text = attach_file_div.find('#file-attach-text');
    var file_attach = attach_file_div.find('#file-attach')
    //value削除する
    file_attach_text.val('');
    file_attach.val('');
    //フォーム要素を削除する(2個以上の場合)
    if ($('#attach-file-root').children('#attach-file-div').length > 1) {
      attach_file_div.remove();
    }
  });


  //ファイルが選択されたら
  $(document).on('change', '#file-attach', function () {
    var file_attach_text = $(this).parent().parent().parent().find('#file-attach-text');
    file_attach_text.val($(this).val().replace(/C:\\fakepath\\/g, ''));
    //ファイルフィールド追加
    add_file_select();
  });

  //Anonymous Post がチェックされたら
  $('#check-annonymous').change(function () {
    r = confirm('Keep the current title? (Cancel to change it to deafult)');
    if (r == false) {
      //cancel押下 -> タイトル変更
      if ($(this).is(':checked') == true) {
        //Anonymousを設定する
        set_title_value('Anonymous');
      } else {
        //ログインユーザー名を設定する
        set_title_value($(this).attr('user_name'));
      }
    }
    //Author変更
    if ($(this).is(':checked') == true) {
      set_author_value('Anonymous@Anonymous');
    } else {
      set_author_value($(this).attr('author_name'));
    }
    $('#compose-title').focus();
  });

  //Author の値を変更する
  function set_author_value(author) {
    $('#span-author').text(author);
  }

  //指定されたユーザ名をもとにタイトルフィールドに文字列を設定する
  function set_title_value(user_name) {
    var title = user_name;
    var now = new Date();
    //"Wed Jul 19 2017 09:15:40 GMT+0900 (東京(標準時))" から +0900を抽出
    var tz_str = now.toString().split(' ')[5].split('+')[1];
    var title = now.getFullYear() + '-' +
      ('0' + (now.getMonth() + 1)).slice(-2) + '-' +
      ('0' + (now.getDate())).slice(-2) + 'T' +
      ('0' + (now.getHours())).slice(-2) + ':' +
      ('0' + (now.getMinutes())).slice(-2) + ':' +
      ('0' + (now.getSeconds())).slice(-2) + '+' + tz_str +
      ' by ' + user_name;
    $('#compose-title').val(title);
    return;
  }

  //CTIM-GV クリック
  $(document).on("click", ".share-ctim-gv", function () {
    $.ajax({
      url: '/feeds/get_ctim_gv_url/',
      data: {
        'package_id': $(this).data('package-id'),
      },
      type: 'get',
      cache: false,
      async: false,
    }).done(function (url) {
      //別ウインドウでurlを開く
      var childWindow = window.open('about:blank');
      childWindow.location.href = url;
      childWindow = null;
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
    })
  });


  //MISP クリック
  $(document).on("click", ".share-misp", function () {
    var li = $(this).closest("li");
    $.ajax({
      url: '/feeds/share_misp/',
      data: {
        'package_id': $(li).attr('package-id'),
      },
      type: 'get',
      cache: false,
      async: false,
    }).done(function (url) {
      //別ウインドウでurlを開く
      var childWindow = window.open('about:blank');
      childWindow.location.href = url;
      childWindow = null;
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
    });
  });

  //Sighting クリック
  $(document).on("click", ".sighting-splunk", function () {
    var li = $(this).closest("li");
    var feed_id = $(li).attr('feed-id');
    var package_id = $(li).attr('package-id');
    $.ajax({
      url: '/feeds/sighting_splunk',
      data: {
        'feed_id': feed_id,
      },
      type: 'get',
      cache: false,
      async: false,
    }).done(function (sightings_str) {
      var sighting_splunk_modal_body = $('#sighting-splunk-modal-body');
      sighting_splunk_modal_body.empty();

      var sightings = JSON.parse(sightings_str);
      var body_str = '<table class="table stripe hover" id="sighting-splunk-table">';
      body_str += '<thead><tr><th>Type</th><th>Value</th><th>Count</th><th>First Seen</th><th>Last Seen</th><th>Check</th><th>Sighting Object</th></tr></thead>'
      body_str += '<tbody>'
      sightings.forEach(function (val, index, ar) {
        var first_seen = val['first_seen'] == 'N/A' ? '' : val['first_seen'];
        var last_seen = val['last_seen'] == 'N/A' ? '' : val['last_seen'];
        var observable_id = val['observable_id'];
        body_str += '<tr>';
        body_str += '<td>' + val['type'] + '</td>';
        body_str += '<td>' + val['value'] + '</td>';
        body_str += '<td>' + val['count'] + '</td>';
        body_str += '<td>' + val['first_seen'] + '</td>';
        body_str += '<td>' + val['last_seen'] + '</td>';
        body_str += '<td><a href="' + val['url'] + '" target="_blank">Check</a></td>';
        body_str += '<td><a class="create-sighting-object"';
        body_str += 'data-observable-id="' + observable_id + '" ';
        body_str += 'data-package-id="' + package_id + '" ';
        body_str += 'data-feed-id="' + feed_id + '" ';
        body_str += 'data-type="' + val['type'] + '" ';
        body_str += 'data-value="' + val['value'] + '" ';
        body_str += 'data-first-seen="' + first_seen + '" ';
        body_str += 'data-last-seen="' + last_seen + '" ';
        body_str += 'data-count="' + val['count'] + '">Create</a></td>';
        body_str += '</tr>';
      });
      body_str += '</tbody></table>'

      sighting_splunk_modal_body.append(body_str);
      $('#splunk-sighting-modal-body').html(body_str);

      var opt = {
        'columnDefs': [
          { 'targets': 0, 'orderable': true, 'searchable': true }, //type
          { 'targets': 1, 'orderable': true, 'searchable': true }, //value
          { 'targets': 2, 'orderable': true, 'searchable': true }, // Count
          { 'targets': 3, 'orderable': true, 'searchable': true }, // First Seen
          { 'targets': 4, 'orderable': true, 'searchable': true }, // Last Seen
          { 'targets': 5, 'orderable': false, 'searchable': false }, // Check
          { 'targets': 6, 'orderable': false, 'searchable': false } // Create a Sighting Object
        ],
        'paging': false
      }
      $('#sighting-splunk-table').DataTable(opt);
      $('#splunk-sighting-modal-dialog').modal();
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
    });
  });

  //Create a Sightint Object クリック
  $(document).on("click", ".create-sighting-object", function () {
    var f = document.createElement('form');
    f.action = '/feeds/create_sighting_object';
    f.method = 'get';

    var package_id = document.createElement('input');
    package_id.setAttribute('type', 'hidden');
    package_id.setAttribute('name', 'package_id');
    package_id.setAttribute('value', $(this).data('package-id'));
    f.appendChild(package_id);
    var feed_id = document.createElement('input');
    feed_id.setAttribute('type', 'hidden');
    feed_id.setAttribute('name', 'feed_id');
    feed_id.setAttribute('value', $(this).data('feed-id'));
    f.appendChild(feed_id);
    var type = document.createElement('input');
    type.setAttribute('type', 'hidden');
    type.setAttribute('name', 'type');
    type.setAttribute('value', $(this).data('type'));
    f.appendChild(type);
    var value = document.createElement('input');
    value.setAttribute('type', 'hidden');
    value.setAttribute('name', 'value');
    value.setAttribute('value', $(this).data('value'));
    f.appendChild(value);
    var first_seen = document.createElement('input');
    first_seen.setAttribute('type', 'hidden');
    first_seen.setAttribute('name', 'first_seen');
    first_seen.setAttribute('value', $(this).data('first-seen'));
    f.appendChild(first_seen);
    var last_seen = document.createElement('input');
    last_seen.setAttribute('type', 'hidden');
    last_seen.setAttribute('name', 'last_seen');
    last_seen.setAttribute('value', $(this).data('last-seen'));
    f.appendChild(last_seen);
    var count = document.createElement('input');
    count.setAttribute('type', 'hidden');
    count.setAttribute('name', 'count');
    count.setAttribute('value', $(this).data('count'));
    f.appendChild(count);
    var observable_id = document.createElement('input');
    observable_id.setAttribute('type', 'hidden');
    observable_id.setAttribute('name', 'observable_id');
    observable_id.setAttribute('value', $(this).data('observable-id'));
    f.appendChild(observable_id);
    document.body.appendChild(f);
    f.submit();
    return;
  });

  //JIRA downloadクリック
  $(document).on("click", ".response-action-jira", function () {
    var li = $(this).closest(".feed-li");
    $.ajax({
      url: '/feeds/call_jira/',
      data: {
        'feed_id': $(li).attr('feed-id'),
        'package_id': $(li).attr('package-id'),
      },
      type: 'get',
      cache: false,
      async: false,
    }).done(function (data) {
      var childWindow = window.open('about:blank');
      childWindow.location.href = data['url'];
      childWindow = null;
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
    });
  });

  //Action downloadクリック
  $(document).on("click", ".response-action", function () {
    if ($(this).hasClass('selected') == true) {
      //menu 非表示
      $(this).removeClass('selected')
      $(this).next('.response-action-menu-ul').slideUp('fast');

    } else {
      //menu 表示
      $(this).addClass('selected');
      $(this).next('.response-action-menu-ul').slideDown('fast');
    }
  });

  //Phantom 連携クリック
  $(document).on('click', '.response-action-phantom', function () {
    var li = $(this).closest(".feed-li");
    $.ajax({
      url: '/feeds/run_phantom_playbook/',
      data: {
        'feed_id': li.attr('feed-id'),
      },
      type: 'get',
      cache: false,
      async: false,
    }).done(function (data) {
      var childWindow = window.open('about:blank');
      childWindow.location.href = data['url'];
      childWindow = null;
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
    });
  });

  //STIX downloadクリック
  $(document).on("click", ".download-stix", function () {
    if ($(this).hasClass('selected') == true) {
      //menu 非表示
      $(this).removeClass('selected')
      $(this).next('.stix-download-menu-ul').slideUp('fast');

    } else {
      //menu 表示
      $(this).addClass('selected');
      $(this).next('.stix-download-menu-ul').slideDown('fast');
    }
  });

  $(document).on("click", ".download-stix-content", function () {
    var li = $(this).closest("li");
    var f = document.createElement('form');
    f.action = '/feeds/download_stix/';
    f.method = 'get';

    var feed_id = document.createElement('input');
    feed_id.setAttribute('type', 'hidden');
    feed_id.setAttribute('name', 'package_id');
    feed_id.setAttribute('value', $(this).data('package-id'));
    f.appendChild(feed_id);
    var stix_version = document.createElement('input');
    stix_version.setAttribute('type', 'hidden');
    stix_version.setAttribute('name', 'version');
    stix_version.setAttribute('value', $(this).data('version'));
    f.appendChild(stix_version);
    document.body.appendChild(f);
    f.submit();

  });

  //CSV downloadクリック
  $(document).on("click", ".download-csv", function () {
    var li = $(this).closest("li");
    var isStop = false;
    $.ajax({
      url: '/feeds/is_exist_indicator/',
      data: {
        'feed_id': $(li).attr('feed-id'),
        'csrfmiddlewaretoken': $(li).attr('csrf'),
      },
      type: 'post',
      cache: false,
      async: false,
    }).done(function (data) {
      if (data == 'False') {
        // CSVの中身が0
        alert('No indicators found')
        isStop = true;
      }
    }).fail(function (XMLHttpRequest, textStatus, errorThrown) {
      var msg = XMLHttpRequest.statusText + ': ' + XMLHttpRequest.responseText;
      alert(msg);
      isStop = true;
    });

    //CSVの中身が0
    if (isStop == true) {
      return;
    }
    //download
    var f = document.createElement('form');
    f.action = '/feeds/download_csv/';
    f.method = 'post';

    var feed_id = document.createElement('input');
    feed_id.setAttribute('type', 'hidden');
    feed_id.setAttribute('name', 'feed_id');
    feed_id.setAttribute('value', $(li).attr('feed-id'));

    var feed_csrf = document.createElement('input');
    feed_csrf.setAttribute('type', 'hidden');
    feed_csrf.setAttribute('name', 'csrfmiddlewaretoken');
    feed_csrf.setAttribute('value', $(li).attr('csrf'));

    f.appendChild(feed_id);
    f.appendChild(feed_csrf);
    document.body.appendChild(f);
    f.submit();
  });

  //PDF downloadクリック
  $(document).on("click", ".download-pdf", function () {
    var li = $(this).closest("li");

    var f = document.createElement('form');
    f.action = '/feeds/download_pdf/';
    f.method = 'post';

    var feed_id = document.createElement('input');
    feed_id.setAttribute('type', 'hidden');
    feed_id.setAttribute('name', 'feed_id');
    feed_id.setAttribute('value', $(li).attr('feed-id'));

    var feed_csrf = document.createElement('input');
    feed_csrf.setAttribute('type', 'hidden');
    feed_csrf.setAttribute('name', 'csrfmiddlewaretoken');
    feed_csrf.setAttribute('value', $(li).attr('csrf'));

    var package_id = document.createElement('input');
    package_id.setAttribute('type', 'hidden');
    package_id.setAttribute('name', 'package_id');
    package_id.setAttribute('value', $(li).attr('package-id'));

    f.appendChild(feed_id);
    f.appendChild(feed_csrf);
    f.appendChild(package_id);
    document.body.appendChild(f);
    f.submit();
  });

  $("ul.stream").on("click", ".like", function () {
    var li = $(this).closest("li");
    var package_id = $(li).attr("package-id");
    var csrf = $(li).attr("csrf");
    $.ajax({
      url: '/feeds/like/',
      data: {
        'package_id': package_id,
        'csrfmiddlewaretoken': csrf
      },
      type: 'post',
      cache: false,
      success: function (data) {
        if ($(".like", li).hasClass("unlike")) {
          $(".like", li).removeClass("unlike");
          $(".like .text", li).text(gettext("Like"));
        }
        else {
          $(".like", li).addClass("unlike");
          $(".like .text", li).text(gettext("Unlike"));
        }
        $(".like .like-count", li).text(data);
      }
    });
    return false;
  });

  $("ul.stream").on("click", ".comment", function () {
    var post = $(this).closest(".post");
    if ($(".comments", post).hasClass("tracking")) {
      $(".comments", post).slideUp();
      $(".comments", post).removeClass("tracking");
    }
    else {
      $(".comments", post).show();
      $(".comments", post).addClass("tracking");
      $(".comments input[name='post']", post).focus();
      //var feed = $(post).closest("li").attr("feed-id");
      var package_id = $(post).closest("li").attr("package-id");
      $.ajax({
        url: '/feeds/comment/',
        //data: { 'feed': feed },
        data: { 'package_id': package_id },
        cache: false,
        beforeSend: function () {
          $("ol", post).html("<li class='loadcomment'><img src='/static/img/loading.gif'></li>");
        },
        success: function (data) {
          $("ol", post).html(data);
          $(".comment-count", post).text($("ol li", post).not(".empty").length);
        }
      });
    }
    return false;
  });

  $("ul.stream").on("click", ".attach", function () {
    var li = $(this).closest("li");

    var f = document.createElement('form');
    f.action = '/feeds/attach/';
    f.method = 'post';

    var file_id = document.createElement('input');
    file_id.setAttribute('type', 'hidden');
    file_id.setAttribute('name', 'file_id');
    file_id.setAttribute('value', $(this).attr('file-id'));

    var feed_id = document.createElement('input');
    feed_id.setAttribute('type', 'hidden');
    feed_id.setAttribute('name', 'feed_id');
    feed_id.setAttribute('value', $(li).attr('feed-id'));

    var feed_csrf = document.createElement('input');
    feed_csrf.setAttribute('type', 'hidden');
    feed_csrf.setAttribute('name', 'csrfmiddlewaretoken');
    feed_csrf.setAttribute('value', $(li).attr('csrf'));

    f.appendChild(file_id);
    f.appendChild(feed_id);
    f.appendChild(feed_csrf);
    document.body.appendChild(f);
    f.submit();
  });

  $("ul.stream").on("keydown", ".comments input[name='post']", function (evt) {
    var keyCode = evt.which ? evt.which : evt.keyCode;
    if (keyCode == 13) {
      var form = $(this).closest("form");
      var container = $(this).closest(".comments");
      var input = $(this);
      $.ajax({
        url: '/feeds/comment/',
        data: $(form).serialize(),
        type: 'post',
        cache: false,
        beforeSend: function () {
          $(input).val("");
        },
        success: function (data) {
          console.log(data)
          $("ol", container).html(data);
          var post_container = $(container).closest(".post");
          $(".comment-count", post_container).text($("ol li", container).length);
        }
      });
      return false;
    }
  });

  var load_feeds = function () {
    if (!$("#load_feed").hasClass("no-more-feeds")) {
      var page = $("#load_feed input[name='page']").val();
      var next_page = parseInt($("#load_feed input[name='page']").val()) + 1;
      $("#load_feed input[name='page']").val(next_page);
      $.ajax({
        url: '/feeds/load/',
        data: $("#load_feed").serialize(),
        cache: false,
        beforeSend: function () {
          $("div.more-link").hide();
          $(".load").show();
        },
        success: function (data) {
          if (data.length > 0) {
            $("ul.stream").append(data)
          }
          else {
            $("#load_feed").addClass("no-more-feeds");
          }
        },
        complete: function () {
          $(".load").hide();
          $("div.more-link").show();
        }
      });
    }
  };

  $("#load_feed").bind("enterviewport", load_feeds).bullseye();

  $("div.more-link").click(function () {
    load_feeds();
  });

  var check_interval = 5000
  function check_new_feeds() {
    if (is_post === true){
      window.setTimeout(check_new_feeds, check_interval);
      return
    }
    var last_feed = $(".stream li:first-child").attr("feed-date");
    var feed_source = $("#feed_source").val();
    if (last_feed != undefined) {
      $.ajax({
        url: '/feeds/check/',
        data: {
          'last_feed': last_feed,
          'feed_source': feed_source
        },
        cache: false,
        success: function (data) {
          if (parseInt(data) > 0) {
            $(".stream-update .new-posts").text(data);
            $(".stream-update").show();
            $(document).attr("title", "(" + data + ") " + page_title);
          }
        },
        complete: function () {
          window.setTimeout(check_new_feeds, check_interval);
        }
      });
    }
    else {
      window.setTimeout(check_new_feeds, check_interval);
    }
  };
  if (screen_type == 'feeds') {
    check_new_feeds();
  }
  $(".stream-update a").click(function () {
    var last_feed = $(".stream li:first-child").attr("feed-date");
    var feed_source = $("#feed_source").val();
    $.ajax({
      url: '/feeds/load_new/',
      data: {
        'last_feed': last_feed,
        'feed_source': feed_source
      },
      cache: false,
      success: function (data) {
        $("ul.stream").prepend(data);
      },
      complete: function () {
        hide_stream_update();
      }
    });
    return false;
  });

  $("input,textarea").attr("autocomplete", "off");

  //定期時間ごとに like,comment 情報を更新しているが処理速度低下のため一旦コメントアウトする
  function update_feeds() {
    if (is_post === true){
      window.setTimeout(update_feeds, check_interval);
      return
    }
    var first_feed = $(".stream .feed-li:first-child").attr("feed-date");
    var last_feed = $(".stream .feed-li:last-child").attr("feed-date");
    var feed_source = $("#feed_source").val();

    if (first_feed != undefined && last_feed != undefined) {
      $.ajax({
        url: '/feeds/update/',
        data: {
          'first_feed': first_feed,
          'last_feed': last_feed,
          'feed_source': feed_source
        },
        cache: false,
        success: function (data) {
          $.each(data, function (id, feed) {
            var li = $("li[package-id='" + id + "']");
            $(".like-count", li).text(feed.likes);
            $(".comment-count", li).text(feed.comments);
          });
        },
        complete: function () {
          window.setTimeout(update_feeds, check_interval);
        }
      });
    }
    else {
      window.setTimeout(update_feeds, check_interval);
    }
  };
  update_feeds();

  function track_comments() {
    if (is_post === true){
      window.setTimeout(track_comments, 30000);
      return
    }
    $(".tracking").each(function () {
      var container = $(this);
      var package_id = $(this).closest("li").attr("package-id");
      $.ajax({
        url: '/feeds/track_comments/',
        data: { 'package_id': package_id },
        cache: false,
        success: function (data) {
          $("ol", container).html(data);
          var post_container = $(container).closest(".post");
          $(".comment-count", post_container).text($("ol li", container).length);
        }
      });
    });
    window.setTimeout(track_comments, 30000);
  };
  track_comments();

  $("ul.stream").on("click", ".remove-feed", function () {
    var li = $(this).closest("li");
    var package_id = $(li).attr("package-id");
    var csrf = $(li).attr("csrf");
    $.ajax({
      url: '/feeds/remove/',
      data: {
        'package_id': package_id,
        'csrfmiddlewaretoken': csrf
      },
      type: 'post',
      cache: false,
      success: function (data) {
        $(li).fadeOut(400, function () {
          $(li).remove();
        });
      }
    });
  });

  // content に文字入力するたびに count 文字数を減らす
  $(document).on("keyup", ".compose-content", function () {
    // Content の文字数上限
    var limit = 10240;
    var length = limit - $(this).val().length;
    var form = $(this).closest("form");
    if (length <= 0) {
      $(".form-group", form).addClass("has-error");
    }
    else {
      $(".form-group", form).removeClass("has-error");
    }
    var count_span = $(this).parents('.compose-content-div').find('.help-count');
    count_span.text(length);
  });

  //Title Link クリックした時
  $('.title-link').click(function () {
    var expanded_str = $(this).attr("aria-expanded");
    var expanded = false;
    if (expanded_str == undefined) {
      // aria-expanded が付与されていない状態でのクリック
      expanded = true;
    }
    else {
      if (expanded_str == 'true') {
        //expanded の状態からのクリック
        expanded = false;
      }
      else {
        //expanded されていない状態からのクリック
        expanded = true;
      }
    }
    if (expanded == true) {
      //表示される前に feed 情報取得
      var package_id = $(this).parents('li').attr('package-id');
      var span_comment_count = $(this).parents('.panel-group').find('.comment-count');
      var a_text_like = $(this).parents('.panel-group').find('.like').children('.text');
      var span_like_count = $(this).parents('.panel-group').find('.like-count');
      $.ajax({
        url: '/feeds/get_like_comment/',
        data: {
          'package_id': package_id,
        },
        type: 'get',
        cache: false,
        success: function (data) {
          //like (boolean) によって非常を変える
          if (data['like'] == true) {
            a_text_like.text(gettext('Unlike'))
          } else {
            a_text_like.text(gettext('Like'))
          }
          //comment count 更新
          span_comment_count.text(data['comments']);
          //like count 更新
          span_like_count.text(data['likes']);
        }
      });
    }
  });
});
