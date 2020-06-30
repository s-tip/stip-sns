$(document)
  .ajaxError(function(e, xhr, opts, error) {
    console.log('AjaxError：' + error);
    if(error == 'Unauthorized'){
      alert('Session Timeout!!. Back to the Login Page.')
      window.location.href = '/login'
    }else{
      alert(error);
  }
});
