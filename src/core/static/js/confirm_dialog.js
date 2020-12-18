var ALL_CHECK_CLASS = 'cofirm-header-checkbox-all-check';
var ALL_CHECK_SELECTOR = '.' + ALL_CHECK_CLASS;
var ALL_UNCHECKED_CLASS = 'cofirm-header-checkbox-all-unchecked';
var ALL_UNCHECKED_SELECTOR = '.' + ALL_UNCHECKED_CLASS;
var CONFIRM_ITEM_TR_CLASS = 'confirm-item-tr';
var CONFIRM_ITEM_TR_SELECTOR = '.' + CONFIRM_ITEM_TR_CLASS;
var CONFIRM_ITEM_CHECKBOX_CLASS = 'confirm-item-checkbox';
var CONFIRM_ITEM_CHECKBOX_SELECTOR = '.' + CONFIRM_ITEM_CHECKBOX_CLASS;
var CONFIRM_ITEM_TYPE_CLASS = 'confirm-item-type';
var CONFIRM_ITEM_TYPE_SELECTOR = '.' + CONFIRM_ITEM_TYPE_CLASS;
var CONFIRM_ITEM_STIX2_INDICATOR_TYPES_CLASS = 'confirm-item-stix2-indicator-types';
var CONFIRM_ITEM_STIX2_INDICATOR_TYPES_SELECTOR = '.' + CONFIRM_ITEM_STIX2_INDICATOR_TYPES_CLASS;
var CONFIRM_ITEM_VALUE_CLASS = 'confirm-item-value';
var CONFIRM_ITEM_VALUE_SELECTOR = '.' + CONFIRM_ITEM_VALUE_CLASS;
var CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID = 'table_id';
var CONFIRM_ITEM_CHECKBOX_ATTR_TARGET = 'target';
var CONFIRM_ITEM_CHECKBOX_ATTR_TITLE = 'title';
var TABLE_ID_INDICATORS = 'indicators'
var TABLE_ID_TTPS = 'ttps'
var TABLE_ID_TAS = 'tas'
var TYPE_IPV4 = 'ipv4';
var TYPE_URI = 'uri';
var TYPE_MD5 = 'md5';
var TYPE_SHA1 = 'sha1';
var TYPE_SHA256 = 'sha256';
var TYPE_SHA512 = 'sha512';
var TYPE_DOMAIN = 'domain';
var TYPE_FILE_NAME = 'file_name';
var TYPE_EMAIL_ADDRESS = 'email_address';
var TYPE_CVE = 'cve';
var TYPE_THREAT_ACTOR = 'threat_actor';
var LISTBOX_TYPE_ATTR = 'type';
var LISTBOX_STIX2_INDICATOR_TYPES_ATTR = 'stix2-indicator-types';

function display_confirm_dialog (data) {
    var table_datas = [];
    if (Object.keys(data['indicators']).length > 0) {
        for (file_name in data['indicators']) {
            if (!(file_name in table_datas)) {
                table_datas[file_name] = []
            }
            table_datas[file_name][TABLE_ID_INDICATORS] = data['indicators'][file_name]
        }
    }
    if (Object.keys(data['ttps']).length > 0) {
        for (file_name in data['ttps']) {
          if (!(file_name in table_datas)) {
              table_datas[file_name] = []
          }
          table_datas[file_name][TABLE_ID_TTPS] = data['ttps'][file_name]
        }
    }
    if (Object.keys(data['tas']).length > 0) {
        for (file_name in data['tas']) {
          if (!(file_name in table_datas)) {
              table_datas[file_name] = []
          }
          table_datas[file_name][TABLE_ID_TAS] = data['tas'][file_name]
        }
    }
    if (Object.keys(table_datas).length > 0) {
        make_extract_tables(table_datas);
        $('#confirm_indicators_modal_dialog').modal();
        return true;
    } else{
        return false;
    }

}



    function get_file_id_from_file_name(file_name) {
      return file_name.replace(/\-/g, '--2d').replace(/\./g, '--2e').replace(/ /g, '--20').replace(/'/g, '--27').replace(/"/g, '--22').replace(/\(/g, '--28').replace(/\)/g, '--29').replace(/\:/g, '--3a').replace(/\//g, '--2f').replace(/\?/g, '--3f').replace(/=/g, '--3d').replace(/\[/g, '--5b').replace(/\]/g, '--5d').replace(/\{/g, '--7b').replace(/\}/g, '--7d').replace(/\#/g, '--23').replace(/\@/g, '--40').replace(/\!/g, '--21').replace(/\$/g, '--24').replace(/\&/g, '--26').replace(/\+/g, '--2b').replace(/\,/g, '--2c').replace(/\;/g, '--3b').replace(/\%/g, '--25')
    };

    function get_file_collapse_id(file_name) {
      return 'collapse-file-' + get_file_id_from_file_name(file_name);
    };
    function get_indicators_collapse_id(file_name) {
      return 'collapse-indicators-' + get_file_id_from_file_name(file_name);
    };
    function get_ttps_collapse_id(file_name) {
      return 'collapse-ttps-' + get_file_id_from_file_name(file_name);
    };
    function get_tas_collapse_id(file_name) {
      return 'collapse-tas-' + get_file_id_from_file_name(file_name);
    };

    function make_extract_tables(table_datas) {
      var indicator_modal_body = $('#indicator-modal-body');
      //要素を初期化
      indicator_modal_body.empty()
      //ファイル毎に modal_body 作成
      for (file_name in table_datas) {
        indicator_modal_body.append(get_file_modal_body_panel_group(file_name, table_datas));
      }
      var opt = {
        'columnDefs': [
          { 'targets': 0, 'orderable': false, 'searchable': false },
          { 'targets': 1, 'orderable': true, 'searchable': false },
          { 'targets': 2, 'orderable': true, 'searchable': true }
        ],
        'paging': false
      }
      $('.indicator-table').DataTable(opt);
    };

    function get_file_modal_body_panel_group(file_name, table_datas) {
      var begin = '<div class="panel-group">';
      var end = '</div>';
      var div = begin + get_file_modal_body_panel_default(file_name, table_datas) + end;
      return div;
    };

    function get_file_modal_body_panel_default(file_name, table_datas) {
      var begin = '<div class="panel panel-default">';
      var end = '</div>';
      var div = begin + get_file_modal_body_panel_heading(file_name) + get_file_modal_body_panel_collapse(file_name, table_datas) + end;
      return div;
    };

    function get_file_modal_body_panel_heading(file_name) {
      //ここで file のリンクのdivを作っている
      var begin = '<div class="panel-heading">';
      var content = '<h4 class="panel-title">' + get_file_modal_body_panel_heading_anchor(file_name) + '</h4>';
      var end = '</div>';
      var div = begin + content + end;
      return div
    };

    function get_file_modal_body_panel_heading_anchor(file_name) {
      var anchor = '#' + get_file_collapse_id(file_name);
      var begin = '<a data-toggle="collapse" href="' + anchor + '">';
      if (file_name == 'S-TIP-SNS-Post-Content') {
        var content = 'S-TIP SNS Post Content';
      }
      else if (file_name.indexOf('Referred-URL:') == 0) {
        //Referred- URL: で始まっている場合はそのまま使う
        var content = file_name;
      }
      else {
        var content = 'Attachment: ' + file_name;
      }
      var end = '</a>';
      var a = begin + content + end;
      return a;
    };

    function get_file_modal_body_panel_collapse(file_name, table_datas) {
      //ここで file のリンクをクリックした時に展開される div を作成している
      var begin = '<div id="' + get_file_collapse_id(file_name) + '" class="panel-collapse collapse">';
      var end = '</div>';
      var div = begin + get_confirm_modal_body_panel_default(file_name, table_datas) + end;
      return div;
    };

    //確認項目 (indicator, ttps) を表示する
    function get_confirm_modal_body_panel_default(file_name, table_datas) {
      var begin_indicators = '<div class="panel panel-default">';
      var end_indicators = '</div>';
      var begin_ttps = '<div class="panel panel-default">';
      var end_ttps = '</div>';
      var begin_tas = '<div class="panel panel-default">';
      var end_tas = '</div>';
      var div_indicators = '';
      var div_ttps = '';
      var div_tas = '';
      var table_data = table_datas[file_name];
      if (TABLE_ID_INDICATORS in table_data) {
        div_indicators = begin_indicators + get_indicators_modal_body_panel_heading(file_name) + get_indicators_modal_body_panel_collapse(file_name, table_data[TABLE_ID_INDICATORS]) + end_indicators;
      }
      if (TABLE_ID_TTPS in table_data) {
        div_ttps = begin_ttps + get_ttps_modal_body_panel_heading(file_name) + get_ttps_modal_body_panel_collapse(file_name, table_data[TABLE_ID_TTPS]) + end_ttps;
      }
      if (TABLE_ID_TAS in table_data) {
        div_tas = begin_tas + get_tas_modal_body_panel_heading(file_name) + get_tas_modal_body_panel_collapse(file_name, table_data[TABLE_ID_TAS]) + end_tas;
      }
      return div_indicators + div_ttps + div_tas;
    };

    function get_indicators_modal_body_panel_heading(file_name) {
      //ここで table のリンクのdiv (indicators) を作っている
      var begin = '<div class="panel-heading">';
      var content = '<h4 class="panel-title">' + get_indicators_modal_body_panel_heading_anchor(file_name) + '</h4>';
      var end = '</div>';
      var div = begin + content + end;
      return div
    };

    function get_indicators_modal_body_panel_heading_anchor(file_name) {
      var anchor = '#' + get_indicators_collapse_id(file_name);
      var begin = '<a data-toggle="collapse" href="' + anchor + '">';
      var content = '>> Indicators ';
      var end = '</a>';
      var a = begin + content + end;
      return a;
    };

    function get_indicators_modal_body_panel_collapse(file_name, indicators) {
      //ここで indicators のリンクをクリックした時に展開される div を作成している
      var begin = '<div id="' + get_indicators_collapse_id(file_name) + '" class="panel-collapse collapse">';
      var end = '</div>';
      var file_id = get_file_id_from_file_name(file_name)
      var div = begin + get_confirm_table(file_name, TABLE_ID_INDICATORS, indicators) + end;
      return div;
    }

    function get_ttps_modal_body_panel_heading(file_name) {
      //ここで table のリンクのdiv (TTPs) を作っている
      var begin = '<div class="panel-heading">';
      var content = '<h4 class="panel-title">' + get_ttps_modal_body_panel_heading_anchor(file_name) + '</h4>';
      var end = '</div>';
      var div = begin + content + end;
      return div
    };

    function get_ttps_modal_body_panel_heading_anchor(file_name) {
      var anchor = '#' + get_ttps_collapse_id(file_name);
      var begin = '<a data-toggle="collapse" href="' + anchor + '">';
      var content = '>> TTPs ';
      var end = '</a>';
      var a = begin + content + end;
      return a;
    };

    function get_ttps_modal_body_panel_collapse(file_name, ttps) {
      //ここで ttps のリンクをクリックした時に展開される div を作成している
      var begin = '<div id="' + get_ttps_collapse_id(file_name) + '" class="panel-collapse collapse">';
      var end = '</div>';
      var div = begin + get_confirm_table(file_name, TABLE_ID_TTPS, ttps) + end;
      return div;
    };


    function get_tas_modal_body_panel_heading(file_name) {
      //ここで table のリンクのdiv (threat_actors) を作っている
      var begin = '<div class="panel-heading">';
      var content = '<h4 class="panel-title">' + get_tas_modal_body_panel_heading_anchor(file_name) + '</h4>';
      var end = '</div>';
      var div = begin + content + end;
      return div;
    };

    function get_tas_modal_body_panel_heading_anchor(file_name) {
      var anchor = '#' + get_tas_collapse_id(file_name);
      var begin = '<a data-toggle="collapse" href="' + anchor + '">';
      var content = '>> Threat Actors ';
      var end = '</a>';
      var a = begin + content + end;
      return a;
    };

    function get_tas_modal_body_panel_collapse(file_name, tas) {
      //ここで threat_actors のリンクをクリックした時に展開される div を作成している
      var begin = '<div id="' + get_tas_collapse_id(file_name) + '" class="panel-collapse collapse">';
      var end = '</div>';
      var div = begin + get_confirm_table(file_name, TABLE_ID_TAS, tas) + end;
      return div;
    };

    function get_confirm_table(file_name, table_id, items) {
      var file_id = get_file_id_from_file_name(file_name)
      var begin = '<table class="table stripe hover indicator-table" id="' + file_id + '">';
      var end = '</table>';
      var table = begin + get_confirm_table_head(file_id, table_id) + get_confirm_table_tbody(file_id, table_id, items) + end;
      return table
    };

    //indicator table に追加する tbody を返却する
    function get_confirm_table_tbody(file_id, table_id, items) {
      var tbody = ''
      var begin = '<tbody>';
      var end = '<tbody>';

      tbody += begin;
      for (index in items) {
        var item = items[index]
        var type_ = item[0];
        var value_ = item[1];
        var title = item[2];
        var checked = item[3];
        tbody += get_confirm_table_tr(type_, value_, title, file_id, table_id, checked);
      }
      tbody += end;
      return tbody;
    };

    //indicator table に追加する tr を返却する
    function get_confirm_table_tr(type_, value_, title, file_id, table_id, checked) {
      //共通部分 (prefix)
      var target_table_td_1_prefix =
        '<td><div class="from-checkbox"><label class="confirm-item-label"><input type="checkbox" class="form-check-input '
        + CONFIRM_ITEM_CHECKBOX_CLASS
        + '" '
        + CONFIRM_ITEM_CHECKBOX_ATTR_TARGET
        + '="'
        + file_id
        + '" '
        + CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID
        + '="'
        + table_id
        + '" '
        + CONFIRM_ITEM_CHECKBOX_ATTR_TITLE
        + '="'
        + title
        + '"';
      //共通部分 (suffix)
      var target_table_td_1_suffix = '/></label></div></td>';
      var target_table_td_1 = '';
      //checked に応じて属性を付与する
      if (checked == true) {
        target_table_td_1 = target_table_td_1_prefix + ' checked' + target_table_td_1_suffix;

      } else {
        target_table_td_1 = target_table_td_1_prefix + target_table_td_1_suffix;
      }
      var target_table_td_2 = '';
      //CVE
      if (type_ == TYPE_CVE) {
        target_table_td_2 = '<td><p class="' + CONFIRM_ITEM_TYPE_CLASS + '" ' + LISTBOX_TYPE_ATTR + '="' + type_ + '">' + type_ + '</p></td>';
      }
      //Tharet Actors
      else if (type_ == TYPE_THREAT_ACTOR) {
        DEFAULT_TA_TYPE = 'unknown';
        target_table_td_2 =
          '<td>'
          + '<div class="btn-group">'
          + '<button class="btn btn-small dropdown-toggle ' + CONFIRM_ITEM_TYPE_CLASS + '" data-toggle="dropdown" ' + LISTBOX_TYPE_ATTR + '="' + DEFAULT_TA_TYPE + '">'
          + DEFAULT_TA_TYPE
          + ' <span class="caret"></span>'
          + '</button>'
          + '<ul class="dropdown-menu dropdown-menu-ta-type">'
          + '<li><a>' + 'activist' + '</a></li>'
          + '<li><a>' + 'competitor' + '</a></li>'
          + '<li><a>' + 'crime-syndicate' + '</a></li>'
          + '<li><a>' + 'criminal' + '</a></li>'
          + '<li><a>' + 'hacker' + '</a></li>'
          + '<li><a>' + 'insider-accidental' + '</a></li>'
          + '<li><a>' + 'insider-disgruntled' + '</a></li>'
          + '<li><a>' + 'nation-state' + '</a></li>'
          + '<li><a>' + 'sensationalist' + '</a></li>'
          + '<li><a>' + 'spy' + '</a></li>'
          + '<li><a>' + 'terrolist' + '</a></li>'
          + '<li><a>' + 'unknown' + '</a></li>'
          + '</ul>'
          + '</div>'
          + '</td>';
      }
      // Indicators
      else {
        DEFAULT_STIX2_INDICATOR_TYPES = 'malicious-activity';
        target_table_td_2 =
          '<td>'
          + '<div class="btn-group">'
          + '<button class="btn btn-small dropdown-toggle ' + CONFIRM_ITEM_TYPE_CLASS + '" data-toggle="dropdown" ' + LISTBOX_TYPE_ATTR + '="' + type_ + '">'
          + type_
          + ' <span class="caret"></span>'
          + '</button>'
          + '<ul class="dropdown-menu dropdown-menu-indicator-type">'
          + '<li><a>' + TYPE_IPV4 + '</a></li>'
          + '<li><a>' + TYPE_MD5 + '</a></li>'
          + '<li><a>' + TYPE_SHA1 + '</a></li>'
          + '<li><a>' + TYPE_SHA256 + '</a></li>'
          + '<li><a>' + TYPE_SHA512 + '</a></li>'
          + '<li><a>' + TYPE_DOMAIN + '</a></li>'
          + '<li><a>' + TYPE_FILE_NAME + '</a></li>'
          + '<li><a>' + TYPE_EMAIL_ADDRESS + '</a></li>'
          + '</ul>'
          + '</div>'
          + '</td>'

          + '<td>'
          + '<div class="btn-group">'
          + '<button class="btn btn-small dropdown-toggle ' + CONFIRM_ITEM_STIX2_INDICATOR_TYPES_CLASS + '" data-toggle="dropdown" ' + LISTBOX_STIX2_INDICATOR_TYPES_ATTR + '="' + DEFAULT_STIX2_INDICATOR_TYPES + '">'
          + DEFAULT_STIX2_INDICATOR_TYPES
          + ' <span class="caret"></span>'
          + '</button>'
          + '<ul class="dropdown-menu dropdown-menu-stix2-indicator-types">'
          + '<li><a>' + 'anomalous-activity' + '</a></li>'
          + '<li><a>' + 'anonymization' + '</a></li>'
          + '<li><a>' + 'benign' + '</a></li>'
          + '<li><a>' + 'compromised' + '</a></li>'
          + '<li><a>' + 'malicious-activity' + '</a></li>'
          + '<li><a>' + 'attribution' + '</a></li>'
          + '<li><a>' + 'unknown' + '</a></li>'
          + '</ul>'
          + '</div>'
          + '</td>';
      }
      var target_table_td_3 = '<td><span style="display:none">' + value_ + '</span><input type="text" class="' + CONFIRM_ITEM_VALUE_CLASS + ' form-control" value="' + value_ + '"/></td>';
      var target_table_tr = '<tr class="' + CONFIRM_ITEM_TR_CLASS + '">' + target_table_td_1 + target_table_td_2 + target_table_td_3 + '</tr>';
      return target_table_tr;
    };

    //indicator table に追加する header を返却する
    function get_confirm_table_head(file_id, table_id) {
      if (table_id == TABLE_ID_INDICATORS) {
        var th_2 = '<th>Type</th>' + '<th>STIX2 Indicator Type</th>';
      }
      else if (table_id == TABLE_ID_TAS) {
        var th_2 = '<th>STIX2 Threat Actors Type</th>';
      }
      else {
        var th_2 = '<th>Type</th>';
      }
      var tr_1_check = '<a class="' + ALL_CHECK_CLASS + '" target="' + file_id + '" table_id="' + table_id + '"><span class="glyphicon glyphicon-check"></span></a>';
      var tr_1_uncheck = '<a class="' + ALL_UNCHECKED_CLASS + '" target="' + file_id + '" table_id="' + table_id + '"><span class="glyphicon glyphicon-unchecked"></span></a>';
      var th_1 = '<th>' + tr_1_check + tr_1_uncheck + '</th>';
      var th_3 = '<th>Value</th>';
      var tr = '<tr>' + th_1 + th_2 + th_3 + '</tr>';
      var thead = '<thead>' + tr + '</thead>';
      return thead;
    };

function get_confirm_data() {
    //各々の confirm-item-tr ごとに checkbox がついていたら form の引数に追加する
    var indicators = [];
    var ttps = [];
    var tas = [];
    $(CONFIRM_ITEM_TR_SELECTOR).each(function (index, element) {
      var checkbox_elem = $(element).find(CONFIRM_ITEM_CHECKBOX_SELECTOR);
      var table_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID);
      if (checkbox_elem.prop('checked') == true) {
        var type_elem = $(element).find(CONFIRM_ITEM_TYPE_SELECTOR);
        var value_elem = $(element).find(CONFIRM_ITEM_VALUE_SELECTOR);
        var file_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TARGET);
        var title = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TITLE);
        var type_ = type_elem.attr(LISTBOX_TYPE_ATTR);
        var value_ = value_elem.val();
        var stix2_indicator_types = 'malicious-activity';

        var item = {}
        item['type'] = type_;
        item['value'] = value_;
        item['title'] = title;
        if (table_id == TABLE_ID_INDICATORS) {
          var stix2_indicator_types_elem = $(element).find(CONFIRM_ITEM_STIX2_INDICATOR_TYPES_SELECTOR);
          var stix2_indicator_types = stix2_indicator_types_elem.attr(LISTBOX_TYPE_ATTR);
          item['stix2_indicator_types'] = stix2_indicator_types;
          indicators.push(item);
        }
        if (table_id == TABLE_ID_TTPS) {
          ttps.push(item);
        }
        if (table_id == TABLE_ID_TAS) {
          tas.push(item);
        }
      }
    });
    return{
        'indicators': indicators,
        'ttps': ttps,
        'tas': tas,
    }

}


  function toggle_confirm_table_checkbox(target, table_id, status) {
    //target と table_id が一致したチェックボックスのみ変更する
    $(CONFIRM_ITEM_CHECKBOX_SELECTOR).each(function (index, element) {
      if ((get_target_from_confirm_item($(element)) == target) &&
        (get_table_id_from_confirm_item($(element)) == table_id)) {
        $(element).prop('checked', status);
      }
    });
  };

  //指定の要素から target を取得する
  function get_target_from_confirm_item(elem) {
    return elem.attr('target');
  };

  function get_table_id_from_confirm_item(elem) {
    return elem.attr('table_id');
  };

$(function () {
  $(document).on('click', '.dropdown-menu-indicator-type li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>');
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text());
  });
  $(document).on('click', '.dropdown-menu-stix2-indicator-types li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>');
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text());
  });
  $(document).on('click', '.dropdown-menu-ta-type li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>');
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text());
  });

  $(document).on("click", ALL_CHECK_SELECTOR, function () {
    //all-check の対象 (target, table_id) の checkbox すべてを check する
    toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)), get_table_id_from_confirm_item($(this)), true);
  });

  $(document).on("click", ALL_UNCHECKED_SELECTOR, function () {
    //all-check の対象 (target, table_id) の checkbox すべてを uncheck する
    toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)), get_table_id_from_confirm_item($(this)), false);
  })
});