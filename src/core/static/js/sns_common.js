var slideTime = 100;
$(function(){
    var account_select_box = $('#account-select-box').multiSelect({
        keepOrder: true,
        selectableHeader: "<input type='text' class='search-input' autocomplete='off' placeholder='Find...'>",
        selectionHeader: "<input type='text' class='search-input' autocomplete='off' placeholder='Find..'>",
        afterInit: function (ms) {
            var that = this,
            $selectableSearch = that.$selectableUl.prev(),
            $selectionSearch = that.$selectionUl.prev(),
            selectableSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selectable:not(.ms-selected)',
            selectionSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selection.ms-selected';

            that.qs1 = $selectableSearch.quicksearch(selectableSearchString).on('keydown', function (e) {
                if (e.which === 40) {
                    that.$selectableUl.focus();
                    return false;
                }
            });

            that.qs2 = $selectionSearch.quicksearch(selectionSearchString).on('keydown', function (e) {
                if (e.which == 40) {
                    that.$selectionUl.focus();
                    return false;
                }
            });
        },
        afterSelect: function () {
          this.qs1.cache();
          this.qs2.cache();
        },
        afterDeselect: function () {
          this.qs1.cache();
          this.qs2.cache();
        }
    });

    $(".publication-radio").change(function () {
        var v = $(this).val();
        if (v == 'people') {
            $("#publication-people-div").slideDown(slideTime);
            $("#publication-group-div").slideUp(slideTime);
        }
        else if (v == 'group') {
            $("#publication-people-div").slideUp(slideTime);
            $("#publication-group-div").slideDown(slideTime);
        }
        else if (v == 'all') {
            $("#publication-people-div").slideUp(slideTime);
            $("#publication-group-div").slideUp(slideTime);
        }
        else {
            $("#publication-people-div").slideUp(slideTime);
            $("#publication-group-div").slideUp(slideTime);
        }
    });

    $('#dropdown-sharing-group li a').click(function () {
        $(this).parents('.dropdown').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>');
        $(this).parents('.dropdown').find('input[name="group"]').val($(this).attr('data-value'));
    });
});
