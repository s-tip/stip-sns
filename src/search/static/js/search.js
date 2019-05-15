$(function () {
  $(".feed-results li").click(function () {
    var feed = $(this).attr("feed-id");
    location.href = "/feeds/id/" + feed + "/";
  });

});