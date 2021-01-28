const ALL_CHECK_CLASS = 'cofirm-header-checkbox-all-check'
const ALL_CHECK_SELECTOR = '.' + ALL_CHECK_CLASS
const ALL_UNCHECKED_CLASS = 'cofirm-header-checkbox-all-unchecked'
const ALL_UNCHECKED_SELECTOR = '.' + ALL_UNCHECKED_CLASS
const CONFIRM_ITEM_TR_CLASS = 'confirm-item-tr'
const CONFIRM_ITEM_TR_SELECTOR = '.' + CONFIRM_ITEM_TR_CLASS
const CONFIRM_ITEM_CHECKBOX_CLASS = 'confirm-item-checkbox'
const CONFIRM_ITEM_CHECKBOX_SELECTOR = '.' + CONFIRM_ITEM_CHECKBOX_CLASS
const CONFIRM_ITEM_TYPE_CLASS = 'confirm-item-type'
const CONFIRM_ITEM_TYPE_SELECTOR = '.' + CONFIRM_ITEM_TYPE_CLASS
const CONFIRM_ITEM_STIX2_INDICATOR_TYPES_CLASS = 'confirm-item-stix2-indicator-types'
const CONFIRM_ITEM_STIX2_INDICATOR_TYPES_SELECTOR = '.' + CONFIRM_ITEM_STIX2_INDICATOR_TYPES_CLASS
const CONFIRM_ITEM_CUSTOM_PROPERTY_TYPE_CLASS = 'confirm-item-custom-property-type'
const CONFIRM_ITEM_CUSTOM_PROPERTY_TYPE_SELECTOR = '.' + CONFIRM_ITEM_CUSTOM_PROPERTY_TYPE_CLASS
const CONFIRM_ITEM_VALUE_CLASS = 'confirm-item-value'
const CONFIRM_ITEM_VALUE_SELECTOR = '.' + CONFIRM_ITEM_VALUE_CLASS
const CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID = 'table_id'
const CONFIRM_ITEM_CHECKBOX_ATTR_TARGET = 'target'
const CONFIRM_ITEM_CHECKBOX_ATTR_TITLE = 'title'
const TABLE_ID_INDICATORS = 'indicators'
const TABLE_ID_TTPS = 'ttps'
const TABLE_ID_TAS = 'tas'
const TABLE_ID_CUSTOM_OBJECTS = 'custom_objects'
const TYPE_IPV4 = 'ipv4'
const TYPE_MD5 = 'md5'
const TYPE_SHA1 = 'sha1'
const TYPE_SHA256 = 'sha256'
const TYPE_SHA512 = 'sha512'
const TYPE_DOMAIN = 'domain'
const TYPE_FILE_NAME = 'file_name'
const TYPE_EMAIL_ADDRESS = 'email_address'
const TYPE_CVE = 'cve'
const TYPE_CUSTOM_OBJECT_PREFIX = 'CUSTOM_OBJECT:'
const TYPE_THREAT_ACTOR = 'threat_actor'
const LISTBOX_TYPE_ATTR = 'type'

function display_confirm_dialog (data) {
  const table_datas = []
  if (Object.keys(data.indicators).length > 0) {
    for (file_name in data.indicators) {
      if (!(file_name in table_datas)) {
        table_datas[file_name] = []
      }
      table_datas[file_name][TABLE_ID_INDICATORS] = data.indicators[file_name]
    }
  }
  if (Object.keys(data.ttps).length > 0) {
    for (file_name in data.ttps) {
      if (!(file_name in table_datas)) {
        table_datas[file_name] = []
      }
      table_datas[file_name][TABLE_ID_TTPS] = data.ttps[file_name]
    }
  }
  if (Object.keys(data.tas).length > 0) {
    for (file_name in data.tas) {
      if (!(file_name in table_datas)) {
        table_datas[file_name] = []
      }
      table_datas[file_name][TABLE_ID_TAS] = data.tas[file_name]
    }
  }

  var custom_object_list = []
  if (Object.keys(data['custom_object_list']).length > 0) {
    custom_object_list = data['custom_object_list']
  }
  $('#confirm_indicators_modal_dialog').data('custom_object_list', custom_object_list)
  var custom_property_list = []
  if (Object.keys(data['custom_property_list']).length > 0) {
    custom_property_list = data['custom_property_list']
  }
  $('#confirm_indicators_modal_dialog').data('custom_property_list', custom_property_list)
  if (Object.keys(data.custom_objects).length > 0) {
    for (file_name in data.custom_objects) {
      if (!(file_name in table_datas)) {
        table_datas[file_name] = []
      }
      table_datas[file_name][TABLE_ID_CUSTOM_OBJECTS] = data.tas[file_name]
    }
  }

  if (Object.keys(table_datas).length > 0) {
    make_extract_tables(table_datas)
    $('#confirm_indicators_modal_dialog').modal()
    return true
  } else {
    return false
  }
}

function make_extract_tables (table_datas) {
  const indicator_modal_body = $('#indicator-modal-body')
  indicator_modal_body.empty()
  for (file_name in table_datas) {
    indicator_modal_body.append(_get_file_modal_body_panel_group(file_name, table_datas))
  }
  const opt = {
    columnDefs: [
      { targets: 0, orderable: false, searchable: false },
      { targets: 1, orderable: true, searchable: false },
      { targets: 2, orderable: true, searchable: true }
    ],
    paging: false
  }
  $('.indicator-table').DataTable(opt)
}

function _get_file_id_from_file_name (file_name) {
  return file_name.replace(/\-/g, '--2d').replace(/\./g, '--2e').replace(/ /g, '--20').replace(/'/g, '--27').replace(/"/g, '--22').replace(/\(/g, '--28').replace(/\)/g, '--29').replace(/\:/g, '--3a').replace(/\//g, '--2f').replace(/\?/g, '--3f').replace(/=/g, '--3d').replace(/\[/g, '--5b').replace(/\]/g, '--5d').replace(/\{/g, '--7b').replace(/\}/g, '--7d').replace(/\#/g, '--23').replace(/\@/g, '--40').replace(/\!/g, '--21').replace(/\$/g, '--24').replace(/\&/g, '--26').replace(/\+/g, '--2b').replace(/\,/g, '--2c').replace(/\;/g, '--3b').replace(/\%/g, '--25')
}
function _get_file_collapse_id (file_name) {
  return 'collapse-file-' + _get_file_id_from_file_name(file_name)
}
function _get_indicators_collapse_id (file_name) {
  return 'collapse-indicators-' + _get_file_id_from_file_name(file_name)
}
function _get_ttps_collapse_id (file_name) {
  return 'collapse-ttps-' + _get_file_id_from_file_name(file_name)
}
function _get_tas_collapse_id (file_name) {
  return 'collapse-tas-' + _get_file_id_from_file_name(file_name)
}
function _get_custom_objects_collapse_id (file_name) {
  return 'collapse-custom-objects-' + _get_file_id_from_file_name(file_name)
}

function _get_file_modal_body_panel_group (file_name, table_datas) {
  const div = $('<div>', {
    class: 'panel-group'
  })
  div.append(_get_file_modal_body_panel_default(file_name, table_datas))
  return div
}

function _get_file_modal_body_panel_default (file_name, table_datas) {
  const div = $('<div>', {
    class: 'panel panel-default'
  })
  div.append(_get_file_modal_body_panel_heading(file_name))
  div.append(_get_file_modal_body_panel_collapse(file_name, table_datas))
  return div
}

function _get_file_modal_body_panel_heading (file_name) {
  const div = $('<div>', {
    class: 'panel-heading'
  })
  const h4 = $('<h4>', {
    class: 'panel-title'
  })
  h4.append(_get_file_modal_body_panel_heading_anchor(file_name))
  div.append(h4)
  return div
}

function _get_file_modal_body_panel_heading_anchor (file_name) {
  const anchor = '#' + _get_file_collapse_id(file_name)
  const a = $('<a>', {
    'data-toggle': 'collapse',
    href: anchor
  })
  let content = ''
  if (file_name == 'S-TIP-SNS-Post-Content') {
    content = 'S-TIP SNS Post Content'
  } else if (file_name.indexOf('Referred-URL:') == 0) {
    content = file_name
  } else {
    content = 'Attachment: ' + file_name
  }
  a.text(content)
  return a
}

function _get_file_modal_body_panel_collapse (file_name, table_datas) {
  const div_template = $('<div>', {
    class: 'panel panel-default'
  })
  const table_data = table_datas[file_name]
  const div = $('<div>', {
    id: _get_file_collapse_id(file_name),
    class: 'panel-collapse collapse'
  })
  if (TABLE_ID_INDICATORS in table_data) {
    const div_indicators = div_template.clone()
    div_indicators.append(_get_indicators_modal_body_panel_heading(file_name))
    div_indicators.append(_get_indicators_modal_body_panel_collapse(file_name, table_data[TABLE_ID_INDICATORS]))
    div.append(div_indicators)
  }
  if (TABLE_ID_TTPS in table_data) {
    const div_ttps = div_template.clone()
    div_ttps.append(_get_ttps_modal_body_panel_heading(file_name))
    div_ttps.append(_get_ttps_modal_body_panel_collapse(file_name, table_data[TABLE_ID_TTPS]))
    div.append(div_ttps)
  }
  if (TABLE_ID_TAS in table_data) {
    const div_tas = div_template.clone()
    div_tas.append(_get_tas_modal_body_panel_heading(file_name))
    div_tas.append(_get_tas_modal_body_panel_collapse(file_name, table_data[TABLE_ID_TAS]))
    div.append(div_tas)
  }
   if (TABLE_ID_CUSTOM_OBJECTS in table_data) {
    const div_custom_objects = div_template.clone()
    div_custom_objects.append(_get_custom_objects_modal_body_panel_heading(file_name))
    div_custom_objects.append(_get_custom_objects_modal_body_panel_collapse(file_name, table_data[TABLE_ID_CUSTOM_OBJECTS]))
    div.append(div_custom_objects)
  }
  return div
}

function _get_common_modal_body_panel_heading (anchor) {
  const div = $('<div>', {
    class: 'panel-heading'
  })
  const h4 = $('<h4>', {
    class: 'panel-title'
  })
  h4.append(anchor)
  div.append(h4)
  return div
}

function _get_indicators_modal_body_panel_heading (file_name) {
 return _get_common_modal_body_panel_heading(
   _get_indicators_modal_body_panel_heading_anchor(file_name))
}

function _get_ttps_modal_body_panel_heading (file_name) {
 return _get_common_modal_body_panel_heading(
   _get_ttps_modal_body_panel_heading_anchor(file_name))
}

function _get_tas_modal_body_panel_heading (file_name) {
 return _get_common_modal_body_panel_heading(
   _get_tas_modal_body_panel_heading_anchor(file_name))
}

function _get_custom_objects_modal_body_panel_heading (file_name) {
 return _get_common_modal_body_panel_heading(
   _get_custom_objects_modal_body_panel_heading_anchor(file_name))
}

function _get_common_modal_body_panel_heading_anchor (id_, text) {
  const anchor = '#' + id_
  const a = $('<a>', {
    'data-toggle': 'collapse',
    href: anchor
  })
  a.text(`>> ${text} `)
  return a
}

function _get_indicators_modal_body_panel_heading_anchor (file_name) {
 return _get_common_modal_body_panel_heading_anchor(
   _get_indicators_collapse_id(file_name),
   'Indicators')
}

function _get_ttps_modal_body_panel_heading_anchor (file_name) {
 return _get_common_modal_body_panel_heading_anchor(
   _get_ttps_collapse_id(file_name),
   'TTPs')
}

function _get_tas_modal_body_panel_heading_anchor (file_name) {
 return _get_common_modal_body_panel_heading_anchor(
   _get_tas_collapse_id(file_name),
   'Threat Actors')
}

function _get_custom_objects_modal_body_panel_heading_anchor (file_name) {
 return _get_common_modal_body_panel_heading_anchor(
   _get_custom_objects_collapse_id(file_name),
   'Custom Objects')
}

function _get_common_modal_body_panel_collapse (id_, table) {
  const div = $('<div>', {
    id: id_,
    class: 'panel-collapse collapse'
  })
  div.append(table)
  return div
}

function _get_indicators_modal_body_panel_collapse (file_name, indicators) {
  return _get_common_modal_body_panel_collapse (
    _get_indicators_collapse_id(file_name),
    _get_confirm_table(file_name, TABLE_ID_INDICATORS, indicators))
}

function _get_ttps_modal_body_panel_collapse (file_name, ttps) {
  return _get_common_modal_body_panel_collapse (
    _get_ttps_collapse_id(file_name),
    _get_confirm_table(file_name, TABLE_ID_TTPS, ttps))
}

function _get_tas_modal_body_panel_collapse (file_name, tas) {
  return _get_common_modal_body_panel_collapse (
    _get_tas_collapse_id(file_name),
    _get_confirm_table(file_name, TABLE_ID_TAS, tas))
}

function _get_custom_objects_modal_body_panel_collapse (file_name, custom_objects) {
  return _get_common_modal_body_panel_collapse (
    _get_custom_objects_collapse_id(file_name),
    _get_confirm_table(file_name, TABLE_ID_CUSTOM_OBJECTS, custom_objects))
}

function _get_confirm_table (file_name, table_id, items) {
  const file_id = _get_file_id_from_file_name(file_name)
  const table = $('<table>', {
    class: 'table stripe hover indicator-table',
    id: file_id
  })
  table.append(_get_confirm_table_head(file_id, table_id))
  table.append(_get_confirm_table_tbody(file_id, table_id, items))
  return table
}

function _get_confirm_table_tbody (file_id, table_id, items) {
  const tbody = $('<tbody>')
  for (const item of items) {
    let [type_, value_, title, checked] = item
    tbody.append(
      _get_confirm_table_tr(type_, value_, title, file_id, table_id, checked)
    )
  }
  return tbody
}

function _get_confirm_table_tr_first_td (title, file_id, table_id, checked) {
  const td = $('<td>')
  const div = $('<div>', {
    class: 'from-checkbox'
  })
  const label = $('<label>', {
    class: 'confirm-item-label'
  })
  const checkbox = $('<input>', {
    type: 'checkbox',
    class: `form-check-input ${CONFIRM_ITEM_CHECKBOX_CLASS}`,
    target: file_id,
    table_id: table_id,
    title: title
  })
  if (checked) {
    checkbox.attr('checked', true)
  }
  label.append(checkbox)
  div.append(label)
  td.append(div)
  return td
}

function _get_confirm_table_tr_last_td (value_) {
  const td = $('<td>')
  const span = $('<span>', {
    style: 'display:none'
  })
  span.text(value_)
  td.append(span)
  const input_text = $('<input>', {
    type: 'text',
    class: `${CONFIRM_ITEM_VALUE_CLASS} form-control`,
    value: value_
  })
  td.append(input_text)
  return td
}

function _get_confirtm_table_tr_td_pulldown (button, li_list, ul_class) {
  const td = $('<td>')
  const div = $('<div>', {
    class: 'btn-group'
  })
  const span = $('<span>', {
    class: 'caret'
  })
  button.append(span)
  div.append(button)

  const ul = $('<ul>', {
    class: `dropdown-menu ${ul_class}`
  })
  for (const li_name of li_list) {
    const li = $('<li>').append($('<a>').text(li_name))
    ul.append(li)
  }
  div.append(ul)
  td.append(div)
  return td
}

function _get_confirm_table_tr_cve_td_list (type_) {
  const td_list = []
  const td = $('<td>')
  const p = $('<p>', {
    class: `${CONFIRM_ITEM_TYPE_CLASS}`,
    type: type_
  })
  p.text(type_)
  td.append(p)
  td_list.push(td)
  return td_list
}

function _get_confirm_table_tr_ta_td_list () {
  const DEFAULT_TA_TYPE = 'unknown'
  const TA_LIST = ['activist', 'competitor', 'crime-syndicate', 'criminal', 'hacker', 'insider-accidental',
    'insider-disgruntled', 'nation-state', 'sensationalist', 'spy', 'terrolist', 'unknown']

  const td_list = []
  const button = $('<button>', {
    class: `btn btn-small dropdown-toggle ${CONFIRM_ITEM_TYPE_CLASS}`,
    'data-toggle': 'dropdown',
    type: `${DEFAULT_TA_TYPE}`
  })
  button.text(DEFAULT_TA_TYPE)
  const td = _get_confirtm_table_tr_td_pulldown(button, TA_LIST, 'dropdown-menu-ta-type')
  td_list.push(td)
  return td_list
}

function _get_confirm_table_tr_custom_object_td_list (type_) {
  const CUSTOM_OBJECT_LIST = $('#confirm_indicators_modal_dialog').data('custom_object_list')
  const CUSTOM_PROPERTY_LIST = $('#confirm_indicators_modal_dialog').data('custom_property_list')
  const type_list = type_.split('CUSTOM_OBJECT:')[1].split('/')
  const custom_object = type_list[0]
  const custom_property = type_list[1]

  const td_list = []
  const button = $('<button>', {
    class: `btn btn-small dropdown-toggle ${CONFIRM_ITEM_TYPE_CLASS}`,
    'data-toggle': 'dropdown',
    type: custom_object
  })
  button.text(custom_object)
  button.prop('disabled', true)
  const td = _get_confirtm_table_tr_td_pulldown(button, CUSTOM_OBJECT_LIST, 'dropdown-menu-custom-object-type')
  td_list.push(td)

  const button_2 = $('<button>', {
    class: `btn btn-small dropdown-toggle ${CONFIRM_ITEM_CUSTOM_PROPERTY_TYPE_CLASS}`,
    'data-toggle': 'dropdown',
    enable: false,
    type: custom_property
  })
  button_2.text(custom_property)
  button_2.prop('disabled', true)
  const td_2 = _get_confirtm_table_tr_td_pulldown(button_2, CUSTOM_PROPERTY_LIST, 'dropdown-menu-custom-property-type')
  td_list.push(td_2)
  return td_list
}

function _get_confirm_table_tr_indicator_td_list (type_) {
  const DEFAULT_STIX2_INDICATOR_TYPES = 'malicious-activity'
  const INDICATOR_LIST = [TYPE_IPV4, TYPE_MD5, TYPE_SHA1, TYPE_SHA256, TYPE_SHA512, TYPE_DOMAIN, TYPE_FILE_NAME, TYPE_EMAIL_ADDRESS]
  const INDICATOR_TYPE_LIST = ['anomalous-activity', 'anonymization', 'benign', 'compromised', 'malicious-activity', 'attribution', 'unknown']
  const td_list = []

  const button_1 = $('<button>', {
    class: `btn btn-small dropdown-toggle ${CONFIRM_ITEM_TYPE_CLASS}`,
    'data-toggle': 'dropdown',
    type: `${type_}`
  })
  button_1.text(type_)
  const td_1 = _get_confirtm_table_tr_td_pulldown(button_1, INDICATOR_LIST, 'dropdown-menu-indicator-type')
  td_list.push(td_1)

  const button_2 = $('<button>', {
    class: `btn btn-small dropdown-toggle ${CONFIRM_ITEM_STIX2_INDICATOR_TYPES_CLASS}`,
    'data-toggle': 'dropdown',
    LISTBOX_STIX2_INDICATOR_TYPES_ATTR: DEFAULT_STIX2_INDICATOR_TYPES
  })
  button_2.text(DEFAULT_STIX2_INDICATOR_TYPES)
  const td_2 = _get_confirtm_table_tr_td_pulldown(button_2, INDICATOR_TYPE_LIST, 'dropdown-menu-stix2-indicator-types')
  td_list.push(td_2)
  return td_list
}

function _get_confirm_table_tr (type_, value_, title, file_id, table_id, checked) {
  let td_list = []

  const first_td = _get_confirm_table_tr_first_td(title, file_id, table_id, checked)
  if (type_ == TYPE_CVE) {
    td_list = _get_confirm_table_tr_cve_td_list(type_)
  } else if (type_ == TYPE_THREAT_ACTOR) {
    td_list = _get_confirm_table_tr_ta_td_list()
  } else if (type_.indexOf(TYPE_CUSTOM_OBJECT_PREFIX) === 0) {
    td_list = _get_confirm_table_tr_custom_object_td_list(type_)
  }
  else {
    td_list = _get_confirm_table_tr_indicator_td_list(type_)
  }
  const last_td = _get_confirm_table_tr_last_td(value_)

  const tr = $('<tr>', {
    class: CONFIRM_ITEM_TR_CLASS
  })
  tr.append(first_td)
  for (const td of td_list) {
    tr.append(td)
  }
  tr.append(last_td)
  return tr
}

function _get_confirm_table_head_first (file_id, table_id) {
  const span_check = $('<span>', {
    class: 'glyphicon glyphicon-check'
  })
  const a_check = $('<a>', {
    class: ALL_CHECK_CLASS,
    target: file_id,
    table_id: table_id
  })
  a_check.append(span_check)

  const span_unchecked = $('<span>', {
    class: 'glyphicon glyphicon-unchecked'
  })
  const a_uncheck = $('<a>', {
    class: ALL_UNCHECKED_CLASS,
    target: file_id,
    table_id: table_id
  })
  a_uncheck.append(span_unchecked)

  const th = $('<th>')
  th.append(a_check)
  th.append(a_uncheck)
  return th
}

function _get_confirm_table_head_last () {
  return $('<th>').text('Value')
}

function _get_confirm_table_head (file_id, table_id) {
  const th_first = _get_confirm_table_head_first(file_id, table_id)
  const th_last = _get_confirm_table_head_last()

  const th_list = []
  if (table_id == TABLE_ID_INDICATORS) {
    const th_1 = $('<th>').text('Type')
    th_list.push(th_1)
    const th_2 = $('<th>').text('STIX2 Indicator Type')
    th_list.push(th_2)
  } else if (table_id == TABLE_ID_TAS) {
    const th = $('<th>').text('STIX2 Threat Actors Type')
    th_list.push(th)
  } else if (table_id == TABLE_ID_CUSTOM_OBJECTS) {
    const th_1 = $('<th>').text('Custom Object')
    th_list.push(th_1)
    const th_2 = $('<th>').text('Custom Property')
    th_list.push(th_2)
  } else {
    const th = $('<th>').text('Type')
    th_list.push(th)
  }

  const tr = $('<tr>')
  tr.append(th_first)
  for (const th of th_list) {
    tr.append(th)
  }
  tr.append(th_last)

  const thead = $('<thead>')
  thead.append(tr)
  return thead
}

function get_confirm_data () {
  const indicators = []
  const ttps = []
  const tas = []
  const custom_objects = []
  $(CONFIRM_ITEM_TR_SELECTOR).each(function (index, element) {
    const checkbox_elem = $(element).find(CONFIRM_ITEM_CHECKBOX_SELECTOR)
    const table_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID)
    if (checkbox_elem.prop('checked') == true) {
      const type_elem = $(element).find(CONFIRM_ITEM_TYPE_SELECTOR)
      const value_elem = $(element).find(CONFIRM_ITEM_VALUE_SELECTOR)
      const file_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TARGET)
      const title = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TITLE)
      const type_ = type_elem.attr(LISTBOX_TYPE_ATTR)
      const value_ = value_elem.val()
      var stix2_indicator_types = 'malicious-activity'

      const item = {}
      item.type = type_
      item.value = value_
      item.title = title
      if (table_id == TABLE_ID_INDICATORS) {
        const stix2_indicator_types_elem = $(element).find(CONFIRM_ITEM_STIX2_INDICATOR_TYPES_SELECTOR)
        var stix2_indicator_types = stix2_indicator_types_elem.attr(LISTBOX_TYPE_ATTR)
        item.stix2_indicator_types = stix2_indicator_types
        indicators.push(item)
      }
      if (table_id == TABLE_ID_TTPS) {
        ttps.push(item)
      }
      if (table_id == TABLE_ID_TAS) {
        tas.push(item)
      }
      if (table_id == TABLE_ID_CUSTOM_OBJECTS) {
        const custom_property_elem = $(element).find(CONFIRM_ITEM_CUSTOM_PROPERTY_TYPE_SELECTOR)
        const custom_property = custom_property_elem.attr(LISTBOX_TYPE_ATTR)
        item.type = `${item.type}/${custom_property}`
        custom_objects.push(item)
      }
    }
  })
  return {
    indicators: indicators,
    ttps: ttps,
    tas: tas,
    custom_objects: custom_objects
  }
}

function toggle_confirm_table_checkbox (target, table_id, status) {
  $(CONFIRM_ITEM_CHECKBOX_SELECTOR).each(function (index, element) {
    if ((get_target_from_confirm_item($(element)) == target) &&
        (get_table_id_from_confirm_item($(element)) == table_id)) {
      $(element).prop('checked', status)
    }
  })
}

function get_target_from_confirm_item (elem) {
  return elem.attr('target')
}

function get_table_id_from_confirm_item (elem) {
  return elem.attr('table_id')
}

$(function () {
  $(document).on('click', '.dropdown-menu-indicator-type li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>')
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text())
  })
  $(document).on('click', '.dropdown-menu-stix2-indicator-types li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>')
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text())
  })
  $(document).on('click', '.dropdown-menu-ta-type li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>')
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text())
  })
  /*
  $(document).on('click', '.dropdown-menu-custom-object-type li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>')
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text())
  })
  $(document).on('click', '.dropdown-menu-custom-property-type li a', function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>')
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text())
  })
  */

  $(document).on('click', ALL_CHECK_SELECTOR, function () {
    toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)), get_table_id_from_confirm_item($(this)), true)
  })

  $(document).on('click', ALL_UNCHECKED_SELECTOR, function () {
    toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)), get_table_id_from_confirm_item($(this)), false)
  })
})
