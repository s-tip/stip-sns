from django.utils.datastructures import MultiValueDictKeyError

# textfieldからitem_name指定の値を取得。未定義時はdefault_value
def get_text_field_value(request, item_name, default_value=None):
    if request.method == 'GET':
        l = request.GET
    elif request.method == 'POST':
        l = request.POST
    else:
        return default_value
    try:
        v = l[item_name]
        if len(v) == 0:
            return default_value
        else:
            # テキストフィールドから取得する場合は前後の空白は取り除く
            return v.strip()
    except MultiValueDictKeyError:
        return default_value
