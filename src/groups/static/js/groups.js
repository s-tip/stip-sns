$(function () {
	//削除ボタン
    $(document).on("click",".button-delete-group",function () {
    	var ret = confirm(gettext("Delete This Group?"));
    	if(ret == false){
    		return;
    	}
    	var group_id = $(this).attr("group_id");
    	var f = $("#form-delete-group");
    	var input = document.createElement('input');
    	input.setAttribute('type','hidden');
    	input.setAttribute('name','id_');
    	input.setAttribute('value',group_id);
    	f.append(input);
    	f.submit()
	});
});