$(function() {

  const NODE_TYPE_OBJECT = 'eclipse'
  const NODE_TYPE_PROPERTY = 'box'
  const NODE_DEFAULT_COLOR = '#D2E5FF'
  const EDGE_DEFAULT_COLOR = {
      opacity: 1.0,
      color: '#777777'
    }

  const EDGE_TYPE_CONTAINS = 'contains'

  const DATA_TYPE_OBJECT = 'object'
  const DATA_TYPE_PROPERTY = 'property'

  const OPERATION_TYPE_ADD_NODE = 'add_node'
  const OPERATION_TYPE_EDIT_NODE = 'edit_node'

  var network = null

  function destroy() {
    if (network !== null) {
      network.destroy()
      network = null
    }
  }

  function updateGraph(dataSource) {
    if (dataSource == null) {
      return
    }
    var show_config = $('#enable-visjs-config').prop('checked')
    var nodes = new vis.DataSet([])
    var edges = new vis.DataSet([])

    $.each(dataSource.custom_objects, function(key_obj, co) {
      var co_node = _get_node_from_object(co)
      nodes.add(co_node)
      $.each(co.properties, function(key_prop, cp) {
        var cp_node = _get_node_from_property(cp, co_node)
        nodes.add(cp_node)
        var edge = _get_edge(co_node.id, cp_node.id)
        edges.add(edge)
      })
    })
    _start_network(nodes, edges, null)
  }

  function _get_node_from_object(co) {
    var d = {
      type:  DATA_TYPE_OBJECT,
      parent: null,
      label: co.name,
      color: co.color,
      shape: NODE_TYPE_OBJECT
    }
    return d
  }

  function _init_property_node() {
    var required = false
    var val_type = 'string'
    var regexp = null

    var fuzzy_matching = {
      case_insensitive: false,
      match_kata_hira: false,
      match_zen_han: false,
      match_eng_jpn: false,
      list_matching: true,
      lists: [],
    }

    var prop = {
      type:  DATA_TYPE_PROPERTY,
      parent: null,
      label: '',
      color: '',
      required: required,
      val_type: val_type,
      regexp: regexp,
      fuzzy_matching: fuzzy_matching,
      shape: NODE_TYPE_PROPERTY
    }
    return prop
  }

  function _get_node_from_property(cp, co_node) {
    var node = _init_property_node()
    if ('required' in cp) {
      node.required = cp['required']
    }
    if ('type' in cp) {
      node.val_type = cp['type']
    }
    if ('regexp' in cp) {
      node.regexp = cp['regexp']
    }
    if ('fuzzy_matching' in cp) {
      node.fuzzy_matching = cp['fuzzy_matching']
    }
    node.parent = co_node.label
    node.label = cp.name
    node.color = co_node.color
    return node
  }

  function _get_edge(obj_id, prop_id) {
    var d = {
      from: obj_id,
      to: prop_id,
      type: EDGE_TYPE_CONTAINS
    }
    d.color = EDGE_DEFAULT_COLOR
    d.smooth = false
    d.chosen = false
    return d
  }

  function _start_network(nodes, edges, config_dom) {
    var container = document.getElementById('visjs-network')
    var data = {
      nodes: nodes,
      edges: edges
    }

    var default_options = {
      autoResize: false,
      physics: {
        enabled: false,
        stabilization: {
          enabled: true
        }
      },
      manipulation: {
        addNode: function(data, callback) {
          addNode(data, callback)
        },
        editNode: function(data, callback) {
          editNode(data, callback)
        },
        addEdge: function(data, callback) {
          if (data.from == data.to) {
            alert('Can not connect the node to itself.')
            return
          }
          editEdgeWithoutDrag(data, callback)
        },
        editEdge: {
          editWithoutDrag: function(data, callback) {
            document.getElementById('edge-operation').innerText =
              'Edit Edge'
            editEdgeWithoutDrag(data, callback)
          },
        },
      }
    }
    var options = default_options
    destroy()
    network = new vis.Network(container, data, options)
  }

  function addNode(data, callback) {
    $('#add-node-name').val('')
    document.getElementById('add-node-saveButton').onclick = saveNodeData.bind(
      this,
      OPERATION_TYPE_ADD_NODE,
      data,
      callback
    )
    document.getElementById('add-node-cancelButton').onclick =
      clearNodePopUp.bind(this, OPERATION_TYPE_ADD_NODE, callback)

    $('#add-prefix-span').html('x-&nbsp;')
    $('#add-type-object').prop('checked', true)
    $('#add-node-popUp').css({'display': 'block'})
  }

  function editNode(data, callback) {
    $('#edit-node-name').val(data.label)

    var title = ''
    if (data.type == DATA_TYPE_PROPERTY) {
      title = 'Edit Custom Property'
      $('#edit-type-property').prop('checked', true)
      $('#edit-node-object-div').css({'display': 'none'})
      $('#edit-node-property-div').css({'display': 'block'})
      $('#edit-common-regexp').val(data.regexp)
      $('#edit-common-val-type').val(data.val_type)
      $('#edit-common-required').prop('checked', data.required)
      $('#edit-fuzzy-case-insensitive').prop('checked', data.fuzzy_matching.case_insensitive)
      $('#edit-fuzzy-kata-hira').prop('checked', data.fuzzy_matching.match_kata_hira)
      $('#edit-fuzzy-zen-han').prop('checked', data.fuzzy_matching.match_zen_han)
      $('#edit-fuzzy-eng-jpn').prop('checked', data.fuzzy_matching.match_eng_jpn)
      $('#edit-fuzzy-list').prop('checked', data.fuzzy_matching.list_matching)
      if (data.fuzzy_matching.list_matching != true) {
        $('.edit-fuzzy-list-textarea').prop('disabled', true)
      }
      if (data.fuzzy_matching.lists.length != 0) {
        $('#edit-fuzzy-list-init').css({'display': 'none'})
      }
      var list_div = $('#edit-fuzzy-list-div')
      list_div.empty()
      $.each(data.fuzzy_matching.lists, function(key, fuzzy_matching_list) {
        var list_contents = ''
        $.each(fuzzy_matching_list, function(key2, content) {
          list_contents += content
          list_contents += '\n'
        })
        var textarea = $('<textarea>', {
          'class': 'form-control edit-fuzzy-list-textarea',
          'rows': 3
        })
        textarea.val(list_contents)
        list_div.append(textarea)
      })
    } else {
      title = 'Edit Custom Object'
      $('#edit-type-object').prop('checked', true)
      $('#edit-common-color').val(data.color.background)
      $('#edit-node-object-div').css({'display': 'block'})
      $('#edit-node-property-div').css({'display': 'none'})
    }
    $('#edit-node-operation').text(title)

    document.getElementById('edit-node-saveButton').onclick = saveNodeData.bind(
      this,
      OPERATION_TYPE_EDIT_NODE,
      data,
      callback
    )
    document.getElementById('edit-node-cancelButton').onclick =
      cancelNodeEdit.bind(this, callback)
    $('#edit-node-popUp').css({'display': 'block'})
  }

  function clearNodePopUp(operation_type) {
    if (operation_type == OPERATION_TYPE_ADD_NODE) {
      document.getElementById('add-node-saveButton').onclick = null
      document.getElementById('add-node-cancelButton').onclick = null
      $('#add-node-popUp').css({'display': 'none'})
    } else {
      document.getElementById('edit-node-saveButton').onclick = null
      document.getElementById('edit-node-cancelButton').onclick = null
      $('#edit-node-popUp').css({'display': 'none'})
    }
  }

  function cancelNodeEdit(callback) {
    clearNodePopUp(OPERATION_TYPE_EDIT_NODE)
    callback(null)
  }

  function getNodeBase(operation_type) {
    if (operation_type == OPERATION_TYPE_ADD_NODE) {
      return $('#add-node-name').val()
    } else {
      return $('#edit-node-name').val()
    }
  }

  function getNodeType(operation_type) {
    var selector = null
    if (operation_type == OPERATION_TYPE_ADD_NODE) {
      selector = $('#add-type-object')
    } else {
      selector = $('#edit-type-object')
    }
    if (selector.prop('checked') == true) {
      return DATA_TYPE_OBJECT
    } else {
      return DATA_TYPE_PROPERTY
    }
  }

  function saveNodeData(operation_type, data, callback) {
    var node_base = getNodeBase(operation_type)
    var node_type = getNodeType(operation_type)
    var before_label = ''

    if (node_base.length == 0) {
      alert('Fill the Object or Property Name')
      return
    }
    if ((node_base.startsWith('x-') == true) || (node_base.startsWith('x_') == true)) {
      node_base = node_base.substring(2)
    }

    if (node_type == DATA_TYPE_OBJECT) {
      before_label = data.label
      data.shape = NODE_TYPE_OBJECT
      data.label = 'x-' + node_base
      data.type = DATA_TYPE_OBJECT
    } else if (node_type == DATA_TYPE_PROPERTY) {
      data.shape = NODE_TYPE_PROPERTY
      data.label = 'x_' + node_base
      data.type = DATA_TYPE_PROPERTY
    } else {
      alert('Wrong type value')
      return
    }

    if (operation_type == OPERATION_TYPE_ADD_NODE) {
      if (isExistObjectNode(data) == true) {
        alert('The Same Property or Object Node has already existed.')
        return
      }

      data.color = NODE_DEFAULT_COLOR
      if (node_type == DATA_TYPE_PROPERTY) {
        var init_property_node = _init_property_node()
        data.required = init_property_node.required
        data.val_type = init_property_node.val_type
        data.regexp = init_property_node.regexp
        data.fuzzy_matching = init_property_node.fuzzy_matching
      }
    } else {
      if (node_type == DATA_TYPE_OBJECT) {
        data.color = $('#edit-common-color').val()
        inheritProperty(before_label, data.label, data.color)
      } else {
        data.required = $('#edit-common-required').prop('checked')
        data.regexp = $('#edit-common-regexp').val()
        var fuzzy_matching = {}
        fuzzy_matching.case_insensitive = $('#edit-fuzzy-case-insensitive').prop('checked')
        fuzzy_matching.match_kata_hira= $('#edit-fuzzy-kata-hira').prop('checked')
        fuzzy_matching.match_zen_han= $('#edit-fuzzy-zen-han').prop('checked')
        fuzzy_matching.match_eng_jpn= $('#edit-fuzzy-eng-jpn').prop('checked')
        fuzzy_matching.list_matching= $('#edit-fuzzy-list').prop('checked')
        var lists = []
        $.each($('.edit-fuzzy-list-textarea'), function(key, ta) {
          var fuzzy_list = []
          var content = ta.value
          if (content.length == 0) {
            return true
          }
          var lines = content.split('\n')
          $.each(lines, function(key2, line) {
            if (line.length == 0) {
              return true
            }
            fuzzy_list.push(line)
          })
          lists.push(fuzzy_list)
        })
        fuzzy_matching.lists = lists
        data.fuzzy_matching = fuzzy_matching
      }
    }
    clearNodePopUp(operation_type)
    callback(data)
  }

  function inheritProperty(before_label, after_label, after_color) {
    $.each(network.body.nodes, function(key, index) {
      var node = network.body.nodes[key].options
      if (node.type == DATA_TYPE_PROPERTY) {
        if (node.parent == before_label) {
          network.body.nodes[key].options.parent = after_label
          network.body.nodes[key].options.color.background = after_color
        }
      }
    })
  }

  function getNode(node_id) {
    return network.body.nodes[node_id]
  }

  function isExistObjectNode(node) {
    var ret = false
    $.each(network.body.nodes, function(key, network_node) {
      var options = network_node.options
      if (node.type == DATA_TYPE_OBJECT) {
        if ((options.type == DATA_TYPE_OBJECT) && (options.label == node.label)) {
          ret = true
          return false
        }
      } else {
        if ((options.type == DATA_TYPE_PROPERTY) && (options.parent == null) && (options.label == node.label)) {
          ret = true
          return false
        }
      }
    })
    return ret
  }

  function editEdgeWithoutDrag(data, callback) {
    var from = getNode(data.from)
    var to = getNode(data.to)
    if (from.options.type == to.options.type) {
      alert('Cannot conect nodes between same types')
      return
    }

    var prop = null
    if (from.options.type == DATA_TYPE_PROPERTY) {
      prop = data.from
    } else {
      prop = data.to
    }
    if (network.getConnectedNodes(prop).length != 0) {
      alert('Cannot connect nodes which has already an edge')
      return
    }
    data.color = EDGE_DEFAULT_COLOR
    saveEdgeData(data, from, to, callback)
  }

  function clearEdgePopUp() {
    document.getElementById('edge-saveButton').onclick = null
    document.getElementById('edge-cancelButton').onclick = null
    document.getElementById('edge-popUp').style.display = 'none'
  }

  function cancelEdgeEdit(callback) {
    clearEdgePopUp()
    callback(null)
  }

  function saveEdgeData(data, from, to, callback) {
    data.type = EDGE_TYPE_CONTAINS
    data.smooth = false
    data.chosen = false
    network.body.nodes[data.to].options.parent = network.body.nodes[data.from].options.label
    clearEdgePopUp()
    callback(data)
  }

  $('#edit-fuzzy-list').on('change', function() {
    $('.edit-fuzzy-list-textarea').prop('disabled', !$(this).prop('checked'))
  })

  $('.add-type-radio').on('change', function() {
    if ($('#add-type-object').prop('checked') == true) {
      $('#add-prefix-span').html('x-&nbsp;&nbsp;')
    }
    if ($('#add-type-property').prop('checked') == true) {
      $('#add-prefix-span').html('x_&nbsp;&nbsp;')
    }
  })

  $('#edit-fully-list-plus').on('click', function() {
    var list_div = $('#edit-fuzzy-list-div')
    var textarea = $('<textarea>', {
      'class': 'form-control edit-fuzzy-list-textarea',
      'rows': 3
    })
    list_div.append(textarea)
  })

  $('#discard-button').on('click', function() {
    ret = confirm('Would you like to discard the configuration?')
    if (ret == true) {
      network.destroy()
      init_draw()
    }
  })

  $('#save-button').on('click', function() {
    var work_custom_objects = {}
    $.each(network.body.nodes, function(key, network_node) {
      var node = network_node.options
      if (node.type == DATA_TYPE_OBJECT) {
        var co = {}
        co.name = node.label
        co.color = node.color.background
        co.properties = []
        work_custom_objects[co.name] = co
      }
    })
    $.each(network.body.nodes, function(key, network_node) {
      var node = network_node.options
      if (node.type == DATA_TYPE_PROPERTY) {
        var prop = {}
        if ('parent' in node == false) {
          return true
        }
        var co = work_custom_objects[node.parent]
        prop.name = node.label
        prop.required = node.required
        prop.type = node.val_type
        prop.regexp = node.regexp
        prop.fuzzy_matching = node.fuzzy_matching
        co.properties.push(prop)
      }
    })

    var custom_objects = []
    $.each(work_custom_objects, function(key, co) {
      if (co.properties.length == 0) {
        return true
      }
      custom_objects.push(co)
    })

    var pd = {}
    pd.objects = custom_objects

    $.ajax({
      url: '/management/stix_customizer/set_configuration/',
      data:JSON.stringify(pd),
      contentType: 'application/json',
      dataType: 'json', 
      type: 'post',
      cache: false,
      async: false,
    })
    .done(function(data, textStatus, jqXHR) {
      alert('Custom Objects are successfully saved')
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      if (jqXHR.status == 201) {
        alert('Custom Objects are successfully saved')
      } else {
        alert(jqXHR.statusText)
      }
    })
  })

  function init_draw() {
    $.ajax({
      url: '/management/stix_customizer/get_configuration/',
      data: {},
      type: 'get',
      cache: false,
      async: false,
    })
    .done(function(data, textStatus, jqXHR) {
      updateGraph(data)
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      alert(jqXHR.statusText)
    })
  }

  $(window).on('load', function() {
    init_draw()
  })
})
