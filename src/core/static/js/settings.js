$(function () {

	$('#id_country').change(function(){
		var country_code = $(this).val();

		//ajaxで取得
	    $.ajax({
	      url: '/settings/get_administrative_area/',
	      data: {
	        'country_code': country_code,
	      },
	      type: 'get',
	      cache: false,
	      success: function (data) {
		    $('#id_administrative_area option').remove();
		    $.each(data,function(i,v){
		    	var code = v['code'];
		    	var administraive_area = v['administraive_area'];
		    	$('#id_administrative_area').append($("<option>").val(code).text(administraive_area));
		    });
	      }
	    });
	});
});