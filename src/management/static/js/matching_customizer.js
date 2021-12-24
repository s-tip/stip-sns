$(function() {

  const NODE_TYPE_OBJECT = 'eclipse'
  const NODE_TYPE_PROPERTY = 'box'
  const NODE_DEFAULT_COLOR = '#D2E5FF'

  const EDGE_TYPE_CONTAINS = 'contains'
  const EDGE_TYPE_MATCH = 'match'

  const DATA_TYPE_OBJECT = 'object'
  const DATA_TYPE_PROPERTY = 'property'

  const OPERATION_TYPE_ADD_NODE = 'add_node'
  const OPERATION_TYPE_EDIT_NODE = 'edit_node'
  const OPERATION_TYPE_ADD_EDGE = 'add_edge'
  const OPERATION_TYPE_EDIT_EDGE = 'edit_edge'

  var network = null
  var matching_names = {}

  function destroy() {
    if (network !== null) {
      network.destroy()
      network = null
      matching_names = {}
    }
  }

  function updateGraph(dataSource) {
    if (dataSource == null) {
      return
    }
    var show_config = $('#enable-visjs-config').prop('checked')
    var nodes = new vis.DataSet([])
    var edges = new vis.DataSet([])
    var store_object = {}
     
    $.each(dataSource.matching_patterns,function(key_obj,mp) {
      var matches = []
      $.each(mp.targets, function(key_target,target) {
        var obj_name = target.split(':')[0]
        var prop_name = target.split(':')[1]
        var obj_node = null
        if (obj_name in store_object) {
          obj_node = store_object[obj_name].node
        } else {
          obj_node = _get_node_from_object(obj_name)
          nodes.add(obj_node)
          store_object[obj_name] = {
            properties: {},
            node: obj_node
          }
        }
        var properties = store_object[obj_name].properties
        if (prop_name in properties) {
          prop_node = properties[prop_name]
        } else {
          prop_node = _get_node_from_property(obj_name, prop_name)
          nodes.add(prop_node)
          store_object[obj_name].properties[prop_name] = prop_node
        }

        var edge = _get_edge(obj_node.id, prop_node.id, EDGE_TYPE_CONTAINS, null)
        edges.add(edge)
        matches.push(prop_node)
      })
      $.each(matches, function(key_source, source) {
        $.each(matches, function(key_target, target) {
          if (key_source < key_target) {
            var edge = _get_edge(source.id, target.id, EDGE_TYPE_MATCH, mp.name)
            edges.add(edge)
            matching_names[edge.id] = mp.name
          }
        })
      })
    })
    _start_network(nodes, edges, null)
  }

  function _get_node_from_object(obj_name) {
    var d = {
      type:  DATA_TYPE_OBJECT,
      parent: null,
      color: NODE_DEFAULT_COLOR, 
      label: obj_name,
      shape: NODE_TYPE_OBJECT
    }
    return d
  }

  function _init_property_node() {
    var prop = {
      type:  DATA_TYPE_PROPERTY,
      parent: null,
      color: NODE_DEFAULT_COLOR, 
      label: '',
      shape: NODE_TYPE_PROPERTY
    }
    return prop
  }

  function _get_node_from_property(obj_name, prop_name) {
    var node = _init_property_node()
    node.parent = obj_name
    node.label = prop_name
    return node
  }

  function _get_edge(obj_id, prop_id, edge_type, matching_name) {
    var d = {
      from: obj_id,
      to: prop_id,
      matching_name: matching_name,
      label: edge_type,
      type: edge_type
    }
    d.color = {
      opacity: 1.0,
      color: '#777777'
    }
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
          editEdgeWithoutDrag(OPERATION_TYPE_ADD_EDGE,data, callback)
        },
        editEdge: {
          editWithoutDrag: function(data, callback) {
            document.getElementById('edge-operation').innerText =
              'Edit Edge'
            editEdgeWithoutDrag(OPERATION_TYPE_EDIT_EDGE, data, callback)
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
    $('#add-type-object').prop('checked', true)
    $('#add-node-popUp').css({'display': 'block'})
  }

  function editNode(data, callback) {
    $('#edit-node-name').val(data.label)

    var title = ''
    if (data.type == DATA_TYPE_PROPERTY) {
      title = 'Edit Custom Property'
      $('#edit-type-property').prop('checked', true)
    } else {
      title = 'Edit Custom Object'
      $('#edit-type-object').prop('checked', true)
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

    data.label = node_base
    if (node_type == DATA_TYPE_OBJECT) {
      before_label = data.label
      data.shape = NODE_TYPE_OBJECT
      data.type = DATA_TYPE_OBJECT
    } else if (node_type == DATA_TYPE_PROPERTY) {
      data.shape = NODE_TYPE_PROPERTY
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
      }
    } else {
      if (node_type == DATA_TYPE_OBJECT) {
        inheritProperty(before_label, data.label)
      }
    }
    clearNodePopUp(operation_type)
    callback(data)
  }

  function inheritProperty(before_label, after_label) {
    $.each(network.body.nodes, function(key,index) {
      var node = network.body.nodes[key].options
      if (node.type == DATA_TYPE_PROPERTY) {
        if (node.parent == before_label) {
          network.body.nodes[key].options.parent = after_label
        }
      }
    })
  }

  function getNode(node_id) {
    var id_ = null
    if (typeof(node_id) == 'string') {
      id_ = node_id
    } else {
      id_ = node_id.id
    }
    return network.body.nodes[id_]
  }

  function isExistObjectNode(node) {
    var ret = false
    $.each(network.body.nodes, function(key,network_node) {
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

  function editEdgeWithoutDrag(operation_type, data, callback) {
    var from = getNode(data.from)
    var to = getNode(data.to)

    data.type = null
    if (from.options.type == DATA_TYPE_OBJECT) {
      if (to.options.type == DATA_TYPE_OBJECT) {
        alert('Cannot create an edge between "OBJECT" type nodes')
        return
      } else {
        data.type = EDGE_TYPE_CONTAINS
      }
    } else {
      if (to.options.type == DATA_TYPE_OBJECT) {
        data.type = EDGE_TYPE_CONTAINS
      } else {
        data.type = EDGE_TYPE_MATCH
      }
    }

    if (data.type == EDGE_TYPE_CONTAINS) {
      _set_contains_edge_dialog(operation_type, data, from, to, callback)
    } else {
      _set_matthing_edge_dialog(operation_type, data, from, to, callback)
    }
  }

  function _set_contains_edge_dialog(operation_type, data, from, to, callback) {
    if (operation_type == OPERATION_TYPE_EDIT_EDGE) {
      alert('Cannot edit a contains edge')
      callback(null)
      return
    }
    var prop = null
    if (from.options.type == DATA_TYPE_PROPERTY) {
      prop = data.from
      data.from = to.id
      data.to = from.id
    } else {
      prop = data.to
      data.from = from.id
      data.to = to.id
    }
    var connect_nodes = network.getConnectedNodes(prop)
    var already_flag = false
    $.each(connect_nodes,function(key, node_id) {
      var connect_node = getNode(node_id)
      if (connect_node.options.type == DATA_TYPE_OBJECT) {
        alert('Cannot connect nodes which has already an edge')
        already_flag = true
        return true
      }
    })
    if (already_flag == true) {
      callback(null)
      return
    }
    save_contains_edge(data, from, to, callback)
  }

  function _set_matthing_edge_dialog(operation_type, data, from, to, callback) {
    if ((from.options.parent == undefined) || (to.options.parent == undefined)) {
      alert('Cannot connect property nodes which do not define a parent object')
      callback(null)
      return
    }
    data.from = from.id
    data.to = to.id

    var matching_name = null
    if (operation_type == OPERATION_TYPE_EDIT_EDGE) {
      matching_name = matching_names[data.id]
    } else {
      matching_name = ''
    }
    $('#edit-edge-rule-name').val(matching_name)
    document.getElementById('edge-saveButton').onclick = save_matching_edge.bind(
      this,
      data,
      from,
      to,
      callback
    )
    document.getElementById('edge-cancelButton').onclick = cancelEdgeEdit.bind(this, callback)
    document.getElementById('edge-operation').innerText = 'Connect a matching link.'
    document.getElementById('edge-div-rule-name').style.display = 'block'
    document.getElementById('edge-popUp').style.display = 'block'
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

  function save_matching_edge(data, from, to, callback) {
    data.label = data.type
    data.smooth = false
    data.chosen = false
    clearEdgePopUp()
    callback(data)
    matching_names[data.id] = $('#edit-edge-rule-name').val()
  }

  function save_contains_edge(data, from, to, callback) {
    data.label = data.type
    data.smooth = false
    data.chosen = false
    network.body.nodes[data.to].options.parent = network.body.nodes[data.from].options.label
    clearEdgePopUp()
    callback(data)
  }

  $('#discard-button').on('click', function() {
    ret = confirm('Would you like to discard the configuration?')
    if (ret == true) {
      network.destroy()
      init_draw()
    }
  })

  $('#save-button').on('click', function() {
    var work_matching_patterns =  {}
    $.each(network.body.edges, function(key, edge) {
      var options = edge.options
      function _get_target_from_node(node) {
        var target = {}
        target.object = node.options.parent
        target.property = node.options.label
        return target
      }

      function _has_target(targets, target){
        var flag = false
        $.each(targets, function(key, elem) {
          if ((target.object == elem.object) && (target.property == elem.property)) {
            flag = true
            return true
          }
        })
        return flag
      }

      function _add_target(matching_name, target) {
        var targets = null
        if (matching_name in work_matching_patterns == true) {
          targets = work_matching_patterns[matching_name]
        } else {
          targets = []
        }
        if (_has_target(targets, target) == false) {
          targets.push(target)
        }
        work_matching_patterns[matching_name] = targets
        return
      }

      if (options.label == EDGE_TYPE_MATCH) {
        var matching_name = matching_names[edge.id]
        var node = null
        node = _get_target_from_node(edge.from)
        _add_target(matching_name, node)
        node = _get_target_from_node(edge.to)
        _add_target(matching_name, node)
      }
    })

    var matching_patterns = []
    $.each(work_matching_patterns, function(name, targets) {
      matching_patterns.push({
        name: name,
        type: 'Exact',
        targets: targets
      })
    })

    var pd = {}
    pd.matching_patterns = matching_patterns

    $.ajax({
      url: '/management/matching_customizer/set_configuration/',
      data:JSON.stringify(pd),
      contentType: 'application/json',
      dataType: 'json', 
      type: 'post',
      cache: false,
      async: false,
    })
    .done(function(data, textStatus, jqXHR) {
      alert('Matching Customizer Settings are successfully saved')
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      if (jqXHR.status == 201) {
        alert('Mathching Customizer Settings are successfully saved')
      } else {
        alert(jqXHR.statusText)
      }
    })
  })

  function init_draw() {
    $.ajax({
      url: '/management/matching_customizer/get_configuration/',
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
