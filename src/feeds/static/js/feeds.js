$(function () {
  var page_title = $(document).attr("title");
  var slideTime = 100;
  
  //新規投稿とキャンセルを入れ替える
  function toggle_new_cancle_button(){
      $('#button-new').toggle();
      $('#button-cancel').toggle();
  }
  
  //multiselect
  var account_select_box = $('#account-select-box').multiSelect({
	  keepOrder:true,
	  selectableHeader: "<input type='text' class='search-input' autocomplete='off' placeholder='Find...'>",
	  selectionHeader: "<input type='text' class='search-input' autocomplete='off' placeholder='Find..'>",
	  afterInit: function(ms){
		    var that = this,
		        $selectableSearch = that.$selectableUl.prev(),
		        $selectionSearch = that.$selectionUl.prev(),
		        selectableSearchString = '#'+that.$container.attr('id')+' .ms-elem-selectable:not(.ms-selected)',
		        selectionSearchString = '#'+that.$container.attr('id')+' .ms-elem-selection.ms-selected';

		    that.qs1 = $selectableSearch.quicksearch(selectableSearchString)
		    .on('keydown', function(e){
		      if (e.which === 40){
		        that.$selectableUl.focus();
		        return false;
		      }
		    });

		    that.qs2 = $selectionSearch.quicksearch(selectionSearchString)
		    .on('keydown', function(e){
		      if (e.which == 40){
		        that.$selectionUl.focus();
		        return false;
		      }
		    });
		  },
		  afterSelect: function(){
		    this.qs1.cache();
		    this.qs2.cache();
		  },
		  afterDeselect: function(){
		    this.qs1.cache();
		    this.qs2.cache();
		  }
	  })

  function hide_stream_update() {
    $(".stream-update").hide();
    $(".stream-update .new-posts").text("");
    $(document).attr("title", page_title);
  };

  $("body").keydown(function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    //Nで開く
    if (keyCode == 78) {
      var focus = $(':focus')[0];
      //どこにもフォーカスが当たっていない場合はひらく
      if(focus == undefined){
          $(".btn-compose").click();
    	  return false;
      }
      //textarea/text field中のNはフックしない
      var focus_type = focus.type;
      if(focus_type == 'textarea'){
      	return true;
      }
      if(focus_type == 'text'){
      	return true;
      }
      if(focus_type == 'search'){
      	return true;
      }
      $(".btn-compose").click();
      return false;
    }
  });

  $("#compose-form textarea[name='post']").keydown(function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    //Ctrl + P
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13 )) {
      $(".btn-post").click();
    }
  });

  $(".btn-compose").click(function () {
    //New button→Cancel button
    toggle_new_cancle_button();
    if ($(".compose").hasClass("composing")) {
      $(".compose").removeClass("composing");
      $(".compose").slideUp();
    }
    else {
      $(".compose").addClass("composing");
      
      //compose領域の初期化
      //checkbox
      //$("#compose-stix-2").prop("checked",false);
      //plus, remove button
      //$(".compose-title-button-plus").css("display","none");
      //$(".compose-title-button-remove").css("display","none");
      //$(".compose-content-button-plus").css("display","none");
      //$(".compose-content-button-remove").css("display","none");

      //title
      var screen_name =  $(".compose").attr("screen_name");
      set_title_value(screen_name);

      //text
      //$(".compose textarea").val("");
      //referred-url
      //$("#referred-url").val("");

      //TLP
      //一旦すべてクリアする
      $('.label-tlp').removeClass("active");
      $('.radio-tlp').prop("checked",false);

      var tlp = $(".compose").attr("tlp");
      //TLPに合わせてactiveをつける
      if (tlp == "RED"){
    	  $('#label-tlp-red').addClass("active");
    	  $('#radio-tlp-red').prop("checked",true);
      }else if (tlp == "AMBER"){
    	  $('#label-tlp-amber').addClass("active");
    	  $('#radio-tlp-amber').prop("checked",true);
      }else if (tlp == "GREEN"){
    	  $('#label-tlp-green').addClass("active");
    	  $('#radio-tlp-green').prop("checked",true);
      }else{
    	  $('#label-tlp-white').addClass("active");
    	  $('#radio-tlp-white').prop("checked",true);
      }

      //添付ファイル
 	  var attach_file_div = $('#attach-file-div');
 	  var append_div = $('<div id="attach-file-div"></div>');
 	  append_div.append(attach_file_div.html());
 	  //upload fromを空にした後追加(最初と同じ状態にする)
 	  $('#attach-file-root').empty()
 	  $('#attach-file-root').append(append_div);
 	  
 	  //Sharing Rangeは With the CSC community
      $('#publication-all').prop("checked",true);

      //peoples詳細設定初期化
      $('#account-select-box').multiSelect('deselect_all');

      //他の2つの詳細設定は閉じる
	  $("#publication-people-div").slideUp(slideTime);
	  $("#publication-group-div").slideUp(slideTime);

      //Anonymous Post check
  	  $('#check-annonymous').prop("checked",false);
      
      $(".compose").slideDown(400, function () {
        //$(".compose textarea").focus();
      });
    }
  });

  $(".btn-cancel-compose").click(function () {
    toggle_new_cancle_button();
    $(".compose").removeClass("composing");
    $(".compose").slideUp();
  });
  
  //post 時 添付ファイルがある場合に indicator サーチを行う
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
  var CONFIRM_ITEM_VALUE_CLASS = 'confirm-item-value';
  var CONFIRM_ITEM_VALUE_SELECTOR = '.' + CONFIRM_ITEM_VALUE_CLASS;
  var CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID = 'table_id';
  var CONFIRM_ITEM_CHECKBOX_ATTR_TARGET = 'target';
  var CONFIRM_ITEM_CHECKBOX_ATTR_TITLE = 'title';
  var TABLE_ID_INDICATORS = 'indicators';
  var TABLE_ID_TTPS = 'ttps';
  var TABLE_ID_TAS = 'tas';
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

  //Listbox クリック時処理
  $(document).on('click','.dropdown-menu-indicator-type li a',function(){
  	$(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>');
  	$(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR,$(this).text());
  });

  //STIX 2.x 投稿の title 情報取得
  function get_stix2_title_information(){
	var stix2_titles = [];
	jQuery.each($('.compose-title'),function(){
		var language = $(this).parents('.compose-title-div').find('.compose-title-language-select').val();
		var title_info = {'title' : this.value,'language' : language};
		stix2_titles.push(title_info);
	});
	return stix2_titles;
  };

  //STIX 2.x 投稿の content 情報取得
  function get_stix2_content_information(){
	var stix2_contents = [];
	jQuery.each($('.compose-content'),function(){
		var language = $(this).parents('.compose-content-div').find('.compose-content-language-select').val();
		var content_info = {'content' : this.value,'language' : language};
		stix2_contents.push(content_info);
	});
	return stix2_contents;
  };
  
  //STIX 2.x 投稿か？
  function is_stix2_post(){
	  return $('#compose-stix-2').prop('checked');
  };
  
  //STIX 2.x 投稿の language duplicate check
  function is_duplicate_languages(values){
    var ret = false;
	var languages = [];
	jQuery.each(values,function(index){
		var value = values[index];
		var language = value['language'];
		if (languages.indexOf(language) >= 0){
			ret = true;
			return;
		}
		languages.push(language)
	});
	return ret;
  };

  function confirm_indicators(){
    //modal dialog に Indicators の結果を table として追加する
    function get_file_id_from_file_name(file_name){
    	return file_name.replace(/\./g,'--').replace(/ /g,'--').replace(/'/g,'--').replace(/"/g,'--').replace(/\(/g,'--').replace(/\)/g,'--').replace(/\:/g,'--').replace(/\//g,'--').replace(/\?/g,'--').replace(/=/g,'--')
    };

    function get_file_collapse_id(file_name){
    	return 'collapse-file-' + get_file_id_from_file_name(file_name);
    };
    function get_indicators_collapse_id(file_name){
    	return 'collapse-indicators-' + get_file_id_from_file_name(file_name);
    };
    function get_ttps_collapse_id(file_name){
    	return 'collapse-ttps-' + get_file_id_from_file_name(file_name);
    };
    function get_tas_collapse_id(file_name){
    	return 'collapse-tas-' + get_file_id_from_file_name(file_name);
    };

    function make_extract_tables(table_datas){
    	var indicator_modal_body = $('#indicator-modal-body');
    	//要素を初期化
    	indicator_modal_body.empty()
    	//ファイル毎に modal_body 作成
    	for (file_name in table_datas){
    		indicator_modal_body.append(get_file_modal_body_panel_group(file_name,table_datas));
    	}
    	var opt = {
    			'columnDefs':[
    	            {'targets':0, 'orderable':false, 'searchable': false},
    	            {'targets':1, 'orderable':true,  'searchable': false},
    	            {'targets':2, 'orderable':true,  'searchable': true}
    	        ],
    	        'paging': false
    	}
    	$('.indicator-table').DataTable(opt);
    };

    function get_file_modal_body_panel_group(file_name,table_datas){
    	var begin = '<div class="panel-group">';
    	var end = '</div>';
    	var div = begin + get_file_modal_body_panel_default(file_name,table_datas) + end;
    	return div;
    };

    function get_file_modal_body_panel_default(file_name,table_datas){
        var begin = '<div class="panel panel-default">';
        var end = '</div>';
        var div = begin + get_file_modal_body_panel_heading(file_name) + get_file_modal_body_panel_collapse(file_name,table_datas) + end;
        return div;
    };

    function get_file_modal_body_panel_heading(file_name){
    	//ここで file のリンクのdivを作っている
    	var begin = '<div class="panel-heading">';
    	var content = '<h4 class="panel-title">' + get_file_modal_body_panel_heading_anchor(file_name) + '</h4>';
    	var end = '</div>';
    	var div = begin + content + end;
    	return div
    };

    function get_file_modal_body_panel_heading_anchor(file_name){
    	var anchor = '#' + get_file_collapse_id(file_name);
    	var begin = '<a data-toggle="collapse" href="' + anchor + '">';
    	if(file_name == 'S-TIP-SNS-Post-Content'){
    		var content = 'S-TIP SNS Post Content';
    	}
    	else if (file_name.indexOf('Referred-URL:') == 0){
    		//Referred- URL: で始まっている場合はそのまま使う
    		var content = file_name;
    	}
    	else{
    		var content = 'Attachment: ' + file_name;
    	}
        var end = '</a>';
        var a = begin + content + end;
        return a;
    };

    function get_file_modal_body_panel_collapse(file_name,table_datas){
    	//ここで file のリンクをクリックした時に展開される div を作成している
    	var begin = '<div id="' + get_file_collapse_id(file_name) + '" class="panel-collapse collapse">';
    	var end = '</div>';
    	var div = begin + get_confirm_modal_body_panel_default(file_name,table_datas) + end;
    	return div;
    };
    
    //確認項目 (indicator, ttps) を表示する
    function get_confirm_modal_body_panel_default(file_name,table_datas){
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
        if (TABLE_ID_INDICATORS in table_data){
        	div_indicators = begin_indicators + get_indicators_modal_body_panel_heading(file_name) + get_indicators_modal_body_panel_collapse(file_name,table_data[TABLE_ID_INDICATORS]) + end_indicators;
        }
        if (TABLE_ID_TTPS in table_data){
        	div_ttps = begin_ttps + get_ttps_modal_body_panel_heading(file_name) + get_ttps_modal_body_panel_collapse(file_name,table_data[TABLE_ID_TTPS]) + end_ttps;
        }
        if (TABLE_ID_TAS in table_data){
        	div_tas = begin_tas + get_tas_modal_body_panel_heading(file_name) + get_tas_modal_body_panel_collapse(file_name,table_data[TABLE_ID_TAS]) + end_tas;
        }
        return div_indicators + div_ttps + div_tas;
    };

    function get_indicators_modal_body_panel_heading(file_name){
    	//ここで table のリンクのdiv (indicators) を作っている
    	var begin = '<div class="panel-heading">';
    	var content = '<h4 class="panel-title">' + get_indicators_modal_body_panel_heading_anchor(file_name) + '</h4>';
    	var end = '</div>';
    	var div = begin + content + end;
    	return div
    };
    
    function get_indicators_modal_body_panel_heading_anchor(file_name){
    	var anchor = '#' + get_indicators_collapse_id(file_name);
    	var begin = '<a data-toggle="collapse" href="' + anchor + '">';
    	var content = '>> Indicators ';
        var end = '</a>';
        var a = begin + content + end;
        return a;
    };    
    
    function get_indicators_modal_body_panel_collapse(file_name,indicators){
    	//ここで indicators のリンクをクリックした時に展開される div を作成している
    	var begin = '<div id="' + get_indicators_collapse_id(file_name)  + '" class="panel-collapse collapse">';
    	var end = '</div>';
    	var file_id = get_file_id_from_file_name(file_name)
    	var div = begin + get_confirm_table(file_name,TABLE_ID_INDICATORS,indicators) + end;
    	return div;
    }    

    function get_ttps_modal_body_panel_heading(file_name){
    	//ここで table のリンクのdiv (TTPs) を作っている
    	var begin = '<div class="panel-heading">';
    	var content = '<h4 class="panel-title">' + get_ttps_modal_body_panel_heading_anchor(file_name) + '</h4>';
    	var end = '</div>';
    	var div = begin + content + end;
    	return div
    }; 
    
    function get_ttps_modal_body_panel_heading_anchor(file_name){
    	var anchor = '#' + get_ttps_collapse_id(file_name);
    	var begin = '<a data-toggle="collapse" href="' + anchor + '">';
    	var content = '>> TTPs ';
        var end = '</a>';
        var a = begin + content + end;
        return a;
    };    
    
    function get_ttps_modal_body_panel_collapse(file_name,ttps){
    	//ここで ttps のリンクをクリックした時に展開される div を作成している
    	var begin = '<div id="' + get_ttps_collapse_id(file_name) + '" class="panel-collapse collapse">';
    	var end = '</div>';
    	var div = begin + get_confirm_table(file_name,TABLE_ID_TTPS,ttps) + end;
    	return div;
    };


    function get_tas_modal_body_panel_heading(file_name){
    	//ここで table のリンクのdiv (threat_actors) を作っている
    	var begin = '<div class="panel-heading">';
    	var content = '<h4 class="panel-title">' + get_tas_modal_body_panel_heading_anchor(file_name) + '</h4>';
    	var end = '</div>';
    	var div = begin + content + end;
    	return div
    }; 
    
    function get_tas_modal_body_panel_heading_anchor(file_name){
    	var anchor = '#' + get_tas_collapse_id(file_name);
    	var begin = '<a data-toggle="collapse" href="' + anchor + '">';
    	var content = '>> Threat Actors ';
        var end = '</a>';
        var a = begin + content + end;
        return a;
    };    
    
    function get_tas_modal_body_panel_collapse(file_name,tas){
    	//ここで threat_actors のリンクをクリックした時に展開される div を作成している
    	var begin = '<div id="' + get_tas_collapse_id(file_name) + '" class="panel-collapse collapse">';
    	var end = '</div>';
    	var div = begin + get_confirm_table(file_name,TABLE_ID_TAS,tas) + end;
    	return div;
    };

	function get_confirm_table(file_name,table_id,items){
    	var file_id = get_file_id_from_file_name(file_name)
    	var begin =  '<table class="table stripe hover indicator-table" id="' + file_id + '">';
    	var end =  '</table>';
    	var table = begin + get_confirm_table_head(file_id,table_id) + get_confirm_table_tbody(file_id,table_id,items) + end;
    	return table
    };
		
	//indicator table に追加する tbody を返却する
	function get_confirm_table_tbody(file_id,table_id,items){
		var tbody = ''
		var begin = '<tbody>';
		var end = '<tbody>';
			
		tbody += begin;
		for (index in items){
			var item = items[index]
			var type_ = item[0];
			var value_ = item[1];
			var title = item[2];
			var checked = item[3];
    	    tbody += get_confirm_table_tr(type_,value_,title,file_id,table_id,checked);
		}
		tbody += end;
		return tbody;
	};

	//indicator table に追加する tr を返却する
	function get_confirm_table_tr(type_,value_,title,file_id,table_id,checked){
		//共通部分 (prefix)
        var target_table_td_1_prefix = 
        	'<td><div class="from-checkbox"><label class="confirm-item-label"><input type="checkbox" class="form-check-input '
        	+ CONFIRM_ITEM_CHECKBOX_CLASS
        	+'" '
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
        var target_table_td_1_suffix =  '/></label></div></td>';
        var target_table_td_1 = '';
        //checked に応じて属性を付与する
        if (checked == true){
        	target_table_td_1 = target_table_td_1_prefix + ' checked' + target_table_td_1_suffix;
        	
        }else{
        	target_table_td_1 = target_table_td_1_prefix + target_table_td_1_suffix;
        }
        var target_table_td_2 = '';
        //Threat Actor と CVE の時は変更なしのテキスト表示
        if ((type_ == TYPE_THREAT_ACTOR) || (type_ == TYPE_CVE)){
        	target_table_td_2 =  '<td><p class="' + CONFIRM_ITEM_TYPE_CLASS + '" ' + LISTBOX_TYPE_ATTR + '="' + type_ + '">' + type_ + '</p></td>';
        }
        //それ以外の時はリストボックスで選択可
        else{
        	target_table_td_2 =  
        		'<td>'
        		+ '<div class="btn-group">'
        		+ '<button class="btn btn-small dropdown-toggle ' + CONFIRM_ITEM_TYPE_CLASS + '" data-toggle="dropdown" ' + LISTBOX_TYPE_ATTR + '="' + type_ + '">'
        		+ type_
        		+ ' <span class="caret"></span>'
        		+ '</button>'
        		+ '<ul class="dropdown-menu dropdown-menu-indicator-type">'
        		+ '<li><a href="#">' + TYPE_IPV4 + '</a></li>'
        		+ '<li><a href="#">' + TYPE_MD5 + '</a></li>'
        		+ '<li><a href="#">' + TYPE_SHA1 + '</a></li>'
        		+ '<li><a href="#">' + TYPE_SHA256 + '</a></li>'
        		+ '<li><a href="#">' + TYPE_SHA512 + '</a></li>'
        		+ '<li><a href="#">' + TYPE_DOMAIN + '</a></li>'
        		+ '<li><a href="#">' + TYPE_FILE_NAME + '</a></li>'
        		+ '<li><a href="#">' + TYPE_EMAIL_ADDRESS + '</a></li>'
        		+ '</ul>'
        		+ '</div>'
        		+ '</td>';
        }
        var target_table_td_3 =  '<td><span style="display:none">' + value_ +'</span><input type="text" class="' + CONFIRM_ITEM_VALUE_CLASS + ' form-control" value="' + value_ + '"/></td>';
    	var target_table_tr =  '<tr class="' + CONFIRM_ITEM_TR_CLASS + '">' + target_table_td_1 + target_table_td_2 + target_table_td_3 + '</tr>';
    	return target_table_tr;
    };

    //indicator table に追加する header を返却する
	function get_confirm_table_head(file_id,table_id){
		var tr_1_check = '<a class="' + ALL_CHECK_CLASS + '" target="' + file_id + '" table_id="' + table_id + '"><span class="glyphicon glyphicon-check"></span></a>';
		var tr_1_uncheck = '<a class="' + ALL_UNCHECKED_CLASS +'" target="' + file_id + '" table_id="' + table_id + '"><span class="glyphicon glyphicon-unchecked"></span></a>';
		var th_1 = '<th>' + tr_1_check + tr_1_uncheck + '</th>';
		var th_2 = '<th>Type</th>';
		var th_3 = '<th>Value</th>';
		var tr = '<tr>' + th_1 + th_2 + th_3 + '</tr>';
		var thead = '<thead>' + tr + '</thead>';
		return thead;
	};

    //複数ファイル添付対応
    var counter = 0;
    jQuery.each($('.file-attach'),function(){
    	if(this.files.length > 0){
    		var name = 'attach_' + counter;
    		this.name = name;
    		counter++;
    	}
    });

    //フィールドにファイルを追加したのでajax送信方法を追加
    var fd = new FormData($('#compose-form').get(0));

	//stix2 フラグ
    var is_stix2 = is_stix2_post();
	fd.append('stix2',is_stix2);

	if(is_stix2 == false){
		//STIX 2.1 checkbox が off の時 (STIX 1.x の場合)
		//post  の長さが 0 の時はエラー
	    var content  = $('#compose-content');
		if (content.val().length == 0){
			alert(gettext('Cannot to post it due to 0-length content.'));
			return;
		}
		//title が 2組以上あったらエラー
		if($('.compose-title-div').length > 1){
			alert(gettext('Choose just one title field.'));
			return;
		}
		//content が 2組以上あったらエラー
		if($('.compose-content-div').length > 1){
			alert(gettext('Choose just one content field.'));
			return;
		}
	}
	else{
		//STIX 2.1 checkbox が on の時 (STIX 2.x の場合)
		//複数ある content が一つでも長さ 0 の場合はエラー
		jQuery.each($('.compose-content'),function(){
			if($(this).val().length == 0){
				alert(gettext('Cannot to post it due to 0-length content.'));
				return;
			}
		});
		//複数ある content 情報から言語情報などをまとめる
		var titles = get_stix2_title_information();
		var contents = get_stix2_content_information()
		if (is_duplicate_languages(titles) == true){
			alert(gettext('Duplicate Same Language Title'));
			return;
		}
		if (is_duplicate_languages(contents) == true){
			alert(gettext('Duplicate Same Language Content'));
			return;
		}
		fd.append('stix2_titles',JSON.stringify(titles));	
		fd.append('stix2_contents',JSON.stringify(contents));	
	}

    //publicationsによって変更する
    var publication = $("#compose-form input[name='publication']:checked").val();
    var people = [];
    if (publication == 'people'){
    	jQuery.each($('#account-select-box option:selected'),function(){
    		people.push(this.value)
    	});
    	if (people.length == 0){
    		alert('Select Sharing Accoutns')
    		return;
    	}
    	fd.append('people',people);
    }
    else if(publication == 'group'){
    	if($("#compose-form input[name='group']").val().length == 0){
    		alert('Select Sharing Group')
    		return;
    	}
    }
    var button = $(".btn-post");

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
    	if(Object.keys(data['indicators']).length > 0){
    		for (file_name in data['indicators']){
    			if (!(file_name in table_datas)){
    				table_datas[file_name] = []
    			}
    			table_datas[file_name][TABLE_ID_INDICATORS] = data['indicators'][file_name]
    		}
    	}
    	// ttps あれば追加する
    	if(Object.keys(data['ttps']).length > 0){
    		for (file_name in data['ttps']){
    			if (!(file_name in table_datas)){
    				table_datas[file_name] = []
    			}
    			table_datas[file_name][TABLE_ID_TTPS] = data['ttps'][file_name]
    		}
    	}
    	// tas あれば追加する
    	if(Object.keys(data['tas']).length > 0){
    		for (file_name in data['tas']){
    			if (!(file_name in table_datas)){
    				table_datas[file_name] = []
    			}
    			table_datas[file_name][TABLE_ID_TAS] = data['tas'][file_name]
    		}
    	}
    	// table_data があれば modal 表示
    	if(Object.keys(table_datas).length > 0){
    		make_extract_tables(table_datas);
    	    $('#confirm_indicators_modal_dialog').modal();
    	}else{
    		//存在しない
    	    $.ajax({
    	        url: '/feeds/post/',
    	        method: 'post',
    	        data: fd,
    	        processData: false,
    	        contentType: false,
    	        cache: false,
    	        beforeSend: function(xhr,settings){
    	        	button.prop('disabled',true);
    	        }
    	    }).done(function (data) {
    	    	$("ul.stream").prepend(data);
    	    	$(".compose").slideUp();
    	    	$(".compose").removeClass("composing");
    	    	hide_stream_update();
    	    }).fail(function(XMLHttpRequest, textStatus, errorThrown){
    	   		var msg = XMLHttpRequest.statusText+ ': ' + XMLHttpRequest.responseText;
    	   		alert(msg);
    	   	}).always(function(){
    	   		button.prop('disabled',false);
                toggle_new_cancle_button();
    	   	});
    	}

    }).fail(function(XMLHttpRequest, textStatus, errorThrown){
   		var msg = XMLHttpRequest.statusText+ ': ' + XMLHttpRequest.responseText;
   		alert(msg);
   	}).always(function(){

   	});
  };
  
  //STIX 2.1 出力チェックボックスのステータス変更時
  $("#compose-stix-2").click(function(){
	  if($(this).prop('checked') == true){
		 $('.compose-title-language-div').css('display','inline-block');
		 $('.compose-title-plus-button').css('display','inline-block');
		 $('.compose-title-remove-button').css('display','inline-block');
		 $('.compose-content-language-div').css('display','inline-block');
		 $('.compose-content-plus-button').css('display','inline-block');
		 $('.compose-content-remove-button').css('display','inline-block');

	  }else{
		 $('.compose-title-language-div').css('display','none');
		 $('.compose-title-plus-button').css('display','none');
		 $('.compose-title-remove-button').css('display','none');
		 $('.compose-content-language-div').css('display','none');
		 $('.compose-content-plus-button').css('display','none');
		 $('.compose-content-remove-button').css('display','none');
	  }
  });
  
  //title の plus ボタンクリック
  $(document).on("click",".compose-title-plus-button",function () {
	  var compose_title_div = $('.compose-title-div');
	  var append_div = $('<div class="row compose-title-div"><br/></div>');
	  append_div.append(compose_title_div.html());
	  $('#compose-title-root-div').append(append_div);
  });

  //title の remove ボタンクリック
  $(document).on("click",".compose-title-remove-button",function () {
	  // 1 つは必ず残す
	  if($(".compose-title-div").length < 2){
		  return;
	  }
	  //対象の compose-title-div を除去する
	  $(this).parents(".compose-title-div").remove();
  });

  //content の plus ボタンクリック
  $(document).on("click",".compose-content-plus-button",function () {
	  var compose_content_div = $('.compose-content-div');
	  var append_div = $('<div class="row compose-content-div"><br/></div>');
	  append_div.append(compose_content_div.html());
	  $('#compose-content-root-div').append(append_div);
  });

  //content の remove ボタンクリック
  $(document).on("click",".compose-content-remove-button",function () {
	  // 1 つは必ず残す
	  if($(".compose-content-div").length < 2){
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
      var indicators = [];
      var ttps = [];
      var tas = [];
	  $(CONFIRM_ITEM_TR_SELECTOR).each(function(index,element){
		  var checkbox_elem = $(element).find(CONFIRM_ITEM_CHECKBOX_SELECTOR);
		  var table_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID);
          if(checkbox_elem.prop('checked') == true){
    		  var type_elem = $(element).find(CONFIRM_ITEM_TYPE_SELECTOR);
    		  var value_elem = $(element).find(CONFIRM_ITEM_VALUE_SELECTOR);
    		  var file_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TARGET);
    		  var title = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TITLE);
    		  var type_ = type_elem.attr(LISTBOX_TYPE_ATTR);
    		  var value_ = value_elem.val();

    		  var item = {}
    		  item['type'] = type_;
    		  item['value'] = value_;
    		  item['title'] = title;
    		  if(table_id == TABLE_ID_INDICATORS){
    			  indicators.push(item);
    		  }
    		  if(table_id == TABLE_ID_TTPS){
    			  ttps.push(item);
    		  }
    		  if(table_id == TABLE_ID_TAS){
    			  tas.push(item);
    		  }
          }
	  });
	  
	  //フィールドにファイルを追加したのでajax送信方法を追加
	  var fd = new FormData($('#compose-form').get(0));
	  fd.append('indicators',JSON.stringify(indicators));
	  fd.append('ttps',JSON.stringify(ttps));
	  fd.append('tas',JSON.stringify(tas));
	  //複数ある content 情報から言語情報などをまとめる
	  fd.append('stix2',is_stix2_post());
	  fd.append('stix2_titles',JSON.stringify(get_stix2_title_information()));	
	  fd.append('stix2_contents',JSON.stringify(get_stix2_content_information()));

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
	  }).fail(function(XMLHttpRequest, textStatus, errorThrown){
	  	var msg = XMLHttpRequest.statusText+ ': ' + XMLHttpRequest.responseText;
	  	alert(msg);
	  }).always(function(){
		  //button toggle 処理はこの呼び出し元で行うため、ここでは実施しない
   	      button.prop('disabled',false);
          toggle_new_cancle_button();
	  });
  });

  $(document).on("click",ALL_CHECK_SELECTOR,function () {
	  //all-check の対象 (target, table_id) の checkbox すべてを check する
	  toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)),get_table_id_from_confirm_item($(this)),true);
  });

  $(document).on("click",ALL_UNCHECKED_SELECTOR,function () {
	  //all-check の対象 (target, table_id) の checkbox すべてを uncheck する
	  toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)),get_table_id_from_confirm_item($(this)),false);
  });
  
  //指定の要素から target を取得する
  function get_target_from_confirm_item(elem){
	  return elem.attr('target');
  };

  //指定の要素から table_id を取得する
  function get_table_id_from_confirm_item(elem){
	  return elem.attr('table_id');
  };

  //指定の target の checkbox を status で指定された状態にする
  function toggle_confirm_table_checkbox(target,table_id,status){
	  //target と table_id が一致したチェックボックスのみ変更する
	  $(CONFIRM_ITEM_CHECKBOX_SELECTOR).each(function(index,element){
    	  if((get_target_from_confirm_item($(element)) == target) &&
    		 (get_table_id_from_confirm_item($(element)) == table_id)){
              $(element).prop('checked',status);
    	  }
	  });
  };

  function add_file_select(){
	  var attach_file_div = $('#attach-file-div');
	  var append_div = $('<div id="attach-file-div"></div>');
	  append_div.append(attach_file_div.html());
	  //upload fromを追加する
	  $('#attach-file-root').append(append_div);
  };

  //ゴミ箱ボタンclick
  $(document).on("click",".btn-remove",function () {
	  //upload_formとtextを削除する
	  var attach_file_div =  $(this).parent().parent().parent()
	  var file_attach_text = attach_file_div.find('#file-attach-text');
	  var file_attach = attach_file_div.find('#file-attach')
	  //value削除する
	  file_attach_text.val('');
	  file_attach.val('');
	  //フォーム要素を削除する(2個以上の場合)
	  if($('#attach-file-root').children('#attach-file-div').length > 1){
		  attach_file_div.remove();
	  }
  });


  //ファイルが選択されたら
  $(document).on('change', '#file-attach', function(){
	  var file_attach_text = $(this).parent().parent().parent().find('#file-attach-text');
	  file_attach_text.val($(this).val().replace(/C:\\fakepath\\/g,''));
	  //ファイルフィールド追加
	  add_file_select();
  });
  
  //Anonymous Post がチェックされたら
  $('#check-annonymous').change(function(){
	  r = confirm('Keep the current title? (Cancel to change it to deafult)');
	  if (r == false){
		 //cancel押下 -> タイトル変更
		  if ($(this).is(':checked') == true){
			  //Anonymousを設定する
			  set_title_value('Anonymous');
		  }else{
			  //ログインユーザー名を設定する
			  set_title_value($(this).attr('user_name'));
		  }		  
	  }
	  //Author変更
	  if ($(this).is(':checked') == true){
		  set_author_value('Anonymous@Anonymous');
	  }else{
		  set_author_value($(this).attr('author_name'));
	  }
	  $('#compose-title').focus();
  });
  
  //Author の値を変更する
  function set_author_value(author){
	  $('#span-author').text(author);
  }
  
  //指定されたユーザ名をもとにタイトルフィールドに文字列を設定する
  function set_title_value(user_name){
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
  $(document).on("click",".share-ctim-gv",function () {
	    var li = $(this).closest("li");
	    $.ajax({
	        url: '/feeds/get_ctim_gv_url/',
	        data: {
	          'package_id': $(li).attr('package-id'),
	        },
	        type: 'get',
	        cache: false,
	        async: false,
	    }).done(function(url){
        	//別ウインドウでurlを開く
        	var childWindow = window.open('about:blank');
        	childWindow.location.href = url;
        	childWindow = null;
	    }).fail(function(XMLHttpRequest, textStatus, errorThrown){
	   		var msg = XMLHttpRequest.statusText+ ': ' + XMLHttpRequest.responseText;
	   		alert(msg);
	   	});
  });

  
  //MISP クリック
  $(document).on("click",".share-misp",function () {
	    var li = $(this).closest("li");
	    $.ajax({
	        url: '/feeds/share_misp/',
	        data: {
	          'package_id': $(li).attr('package-id'),
	        },
	        type: 'get',
	        cache: false,
	        async: false,
	    }).done(function(url){
        	//別ウインドウでurlを開く
        	var childWindow = window.open('about:blank');
        	childWindow.location.href = url;
        	childWindow = null;
	    }).fail(function(XMLHttpRequest, textStatus, errorThrown){
	   		var msg = XMLHttpRequest.statusText+ ': ' + XMLHttpRequest.responseText;
	   		alert(msg);
	   	});
  });

  //JIRA downloadクリック
  $(document).on("click",".share-ctim-jira",function () {
	    var li = $(this).closest("li");
	    $.ajax({
	        url: '/feeds/call_jira/',
	        data: {
	          'feed_id': $(li).attr('feed-id'),
	          'package_id': $(li).attr('package-id'),
	        },
	        type: 'get',
	        cache: false,
	        async: false,
	    }).done(function(data){
        	var childWindow = window.open('about:blank');
        	childWindow.location.href = data['url'];
        	childWindow = null;
	    }).fail(function(XMLHttpRequest, textStatus, errorThrown){
	   		var msg = XMLHttpRequest.statusText+ ': ' + XMLHttpRequest.responseText;
	   		alert(msg);
	   	});
  });

  //STIX downloadクリック
  $(document).on("click",".download-stix",function () {
	    var li = $(this).closest("li");

	    var f = document.createElement('form');
	    f.action = '/feeds/download_stix/';
	    f.method = 'post';

	    var feed_id = document.createElement('input');
	    feed_id.setAttribute('type','hidden');
	    feed_id.setAttribute('name','feed_id');
	    feed_id.setAttribute('value',$(li).attr('feed-id'));

	    var feed_csrf = document.createElement('input');
	    feed_csrf.setAttribute('type','hidden');
	    feed_csrf.setAttribute('name','csrfmiddlewaretoken');
	    feed_csrf.setAttribute('value',$(li).attr('csrf'));

	    f.appendChild(feed_id);
	    f.appendChild(feed_csrf);
	    document.body.appendChild(f);
	    f.submit();
  });
  
  //CSV downloadクリック
  $(document).on("click",".download-csv",function () {
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
	        if(data == 'False'){
	        	// CSVの中身が0
	        	alert('No indicators found')
	        	isStop = true;
	        }
	    }).fail(function(XMLHttpRequest, textStatus, errorThrown){
	   		var msg = XMLHttpRequest.statusText+ ': ' + XMLHttpRequest.responseText;
	   		alert(msg);
	   		isStop = true;
	   	});

	    //CSVの中身が0
	    if(isStop == true){
	    	return;
	    }
	    //download
	    var f = document.createElement('form');
	    f.action = '/feeds/download_csv/';
	    f.method = 'post';

	    var feed_id = document.createElement('input');
	    feed_id.setAttribute('type','hidden');
	    feed_id.setAttribute('name','feed_id');
	    feed_id.setAttribute('value',$(li).attr('feed-id'));

	    var feed_csrf = document.createElement('input');
	    feed_csrf.setAttribute('type','hidden');
	    feed_csrf.setAttribute('name','csrfmiddlewaretoken');
	    feed_csrf.setAttribute('value',$(li).attr('csrf'));

	    f.appendChild(feed_id);
	    f.appendChild(feed_csrf);
	    document.body.appendChild(f);
	    f.submit();
  });

  //PDF downloadクリック
  $(document).on("click",".download-pdf",function () {
	    var li = $(this).closest("li");

	    var f = document.createElement('form');
	    f.action = '/feeds/download_pdf/';
	    f.method = 'post';

	    var feed_id = document.createElement('input');
	    feed_id.setAttribute('type','hidden');
	    feed_id.setAttribute('name','feed_id');
	    feed_id.setAttribute('value',$(li).attr('feed-id'));

	    var feed_csrf = document.createElement('input');
	    feed_csrf.setAttribute('type','hidden');
	    feed_csrf.setAttribute('name','csrfmiddlewaretoken');
	    feed_csrf.setAttribute('value',$(li).attr('csrf'));

	    var package_id = document.createElement('input');
	    package_id.setAttribute('type','hidden');
	    package_id.setAttribute('name','package_id');
	    package_id.setAttribute('value',$(li).attr('package-id'));

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
    file_id.setAttribute('type','hidden');
    file_id.setAttribute('name','file_id');
    file_id.setAttribute('value',$(this).attr('file-id'));

    var feed_id = document.createElement('input');
    feed_id.setAttribute('type','hidden');
    feed_id.setAttribute('name','feed_id');
    feed_id.setAttribute('value',$(li).attr('feed-id'));

    var feed_csrf = document.createElement('input');
    feed_csrf.setAttribute('type','hidden');
    feed_csrf.setAttribute('name','csrfmiddlewaretoken');
    feed_csrf.setAttribute('value',$(li).attr('csrf'));

    f.appendChild(file_id);
    f.appendChild(feed_id);
    f.appendChild(feed_csrf);
    document.body.appendChild(f);
    f.submit();
  });

  $("ul.stream").on("keydown", ".comments input[name='post']", function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
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
  function check_new_feeds () {
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
        complete: function() {
          window.setTimeout(check_new_feeds, check_interval);
        }
      });
    }
    else {
      window.setTimeout(check_new_feeds, check_interval);
    }
  };
  check_new_feeds();

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
  function update_feeds () {
    var first_feed = $(".stream li:first-child").attr("feed-date");
    var last_feed = $(".stream li:last-child").attr("feed-date");
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
          $.each(data, function(id, feed) {
              var li = $("li[package-id='" + id + "']");
              $(".like-count", li).text(feed.likes);
              $(".comment-count", li).text(feed.comments);
          });
        },
        complete: function () {
          window.setTimeout(update_feeds, 30000);
        }
      });
    }
    else {
      window.setTimeout(update_feeds, 30000);
    }
  };
  update_feeds();

  function track_comments () {
    $(".tracking").each(function () {
      var container = $(this);
      var package_id = $(this).closest("li").attr("package-id");
      $.ajax({
        url: '/feeds/track_comments/',
        data: {'package_id': package_id},
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
    var feed = $(li).attr("feed-id");
    var csrf = $(li).attr("csrf");
    $.ajax({
      url: '/feeds/remove/',
      data: {
        'feed': feed,
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
  $(document).on("keyup",".compose-content",function () {
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
  
  //Publicationのラジオボタンが変更があったら
  $(".publication-radio").change(function(){
	  var v = $(this).val();
	  if (v == 'people'){
		  $("#publication-people-div").slideDown(slideTime);
		  $("#publication-group-div").slideUp(slideTime);
		  
	  }
	  else if (v == 'group'){
		  $("#publication-people-div").slideUp(slideTime);
		  $("#publication-group-div").slideDown(slideTime);
	  }
	  else if (v == 'all'){
		  $("#publication-people-div").slideUp(slideTime);
		  $("#publication-group-div").slideUp(slideTime);
	  }
	  else{
		  $("#publication-people-div").slideUp(slideTime);
		  $("#publication-group-div").slideUp(slideTime);
	  }
	  
  });

  //dropdown(group)
  $('#dropdown-sharing-group li a').click(function(){
      $(this).parents('.dropdown').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>');
      $(this).parents('.dropdown').find('input[name="group"]').val($(this).attr('data-value'));
  }); 

  //Title Link クリックした時
  $('.title-link').click(function(){
	  var expanded_str = $(this).attr("aria-expanded");
	  var expanded = false;
	  if (expanded_str == undefined){
		  // aria-expanded が付与されていない状態でのクリック
		  expanded = true;
	  }
	  else{
		  if (expanded_str == 'true'){
			  //expanded の状態からのクリック
			  expanded = false;
		  }
		  else{
			  //expanded されていない状態からのクリック
			  expanded = true;
		  }
	  }
	  if (expanded == true){
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
                	if(data['like'] == true){
                		a_text_like.text(gettext('Unlike'))
                	}else{
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