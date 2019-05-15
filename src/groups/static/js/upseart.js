$(function () {
    $(document).on("click","#button-upsert",function () {
    	var f = $("#form-upsert-group");
    	var fd = new FormData(f.get(0));
	    var people = [];
    	jQuery.each($('#account-select-box option:selected'),function(){
    		people.push(this.value)
    	});
    	var input = document.createElement('input');
    	input.setAttribute('type','hidden');
    	input.setAttribute('name','members');
    	input.setAttribute('value',people.join(','));
    	f.append(input);
    	f.submit()

	});

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
  	  });

    //multi select初期化
    var member_list = $("#id_members").val().split(',');
    //member list に含まれるアカウントは選択済とする
    jQuery.each(member_list,function(){
    	account_select_box.multiSelect('select',this.valueOf());
    });
});