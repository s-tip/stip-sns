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
const CONFIRM_ITEM_CONFIDENCE_CLASS = 'confirm-item-confidence'
const CONFIRM_ITEM_CONFIDENCE_SELECTOR = '.' + CONFIRM_ITEM_CONFIDENCE_CLASS
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
const DIV_OTHER_OBJECT_SELECT_CLASS = 'div-other-object-select'
const DIV_OTHER_OBJECT_SELECT_SELECTOR = '.' + DIV_OTHER_OBJECT_SELECT_CLASS
const DIV_OTHER_STIX_RADIO_CLASS = 'div-other-stix-radio'
const DIV_OTHER_STIX_RADIO_SELECTOR = '.' + DIV_OTHER_STIX_RADIO_CLASS
const DIV_OTHER_STIX_CONFIDENCE_CLASS = 'div-other-stix-confidence'
const DIV_OTHER_STIX_CONFIDENCE_SELECTOR = '.' + DIV_OTHER_STIX_CONFIDENCE_CLASS
const DIV_OTHER_STIX_PROPERTIES_CLASS = 'div-other-stix-properties'
const DIV_OTHER_STIX_PROPERTIES_SELECTOR = '.' + DIV_OTHER_STIX_PROPERTIES_CLASS

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

  var custom_object_dict = {}
  if (Object.keys(data['custom_object_dict']).length > 0) {
    custom_object_dict = data['custom_object_dict']
  }
  $('#confirm_indicators_modal_dialog').data('custom_object_dict', custom_object_dict)
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
  var div = _get_other_stix_element()
  indicator_modal_body.append(div)
  $('.indicator-table').DataTable(opt)
}

const CONFIRM_ITEM_STIX2_ROOT  = 'confirm-item-stix2-root'
const CONFIRM_ITEM_STIX2_OBJECT  = 'confirm-item-stix2-object'
const CONFIRM_ITEM_STIX2_PROPERTIES  = 'confirm-item-stix2-properties'

const STIX2_SDO = {
  'Attack Pattern': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'aliases' : { 'required': false, 'type' : 'textarea', },
      'external_references' : { 'required': false, 'type' : 'textarea', },
      'kill_chain_phases' : { 'required': false, 'type' : 'textarea', },
    },
    'type' : 'attack-pattern',
  },
  'Campaign': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'aliases' : { 'required': false, 'type' : 'textarea', },
      'first_seen' : { 'required': false, 'type' : 'text', },
      'last_seen' : { 'required': false, 'type' : 'text', },
      'objective' : { 'required': false, 'type' : 'text', },
    },
    'type': 'campaign',
  },
  'Course Of Action': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
    },
    'type': 'course-of-action',
  },
  'Grouping': {
    'properties' : {
      'name' : { 'required': false, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'context' : { 'required': true, 'type' : 'text', },
      'object_refs' : { 'required': true, 'type' : 'textarea', },
    },
    'type': 'grouping',
  },
  'Identity': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'roles' : { 'required': false, 'type' : 'textarea', },
      'identity_class' : { 'required': false, 'type' : 'textarea', },
      'sectors' : { 'required': false, 'type' : 'textarea', },
      'contact_information' : { 'required': false, 'type' : 'text', },
    },
    'type': 'identity',
  },
  'Indicator': {
    'properties' : {
      'name' : { 'required': false, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'indicator_types' : { 'required': false, 'type' : 'textarea', },
      'pattern' : { 'required': true, 'type' : 'text', },
      'pattern_type' : { 'required': true, 'type' : 'text', },
      'pattern_version' : { 'required': false, 'type' : 'text', },
      'valid_from' : { 'required': false, 'type' : 'text', },
      'valid_until' : { 'required': false, 'type' : 'text', },
      'kill_chain_phases' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'indicator',
  },
  'Infrastructure': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'infrastructure_types' : { 'required': false, 'type' : 'textarea', },
      'aliases' : { 'required': false, 'type' : 'textarea', },
      'kill_chain_phases' : { 'required': false, 'type' : 'textarea', },
      'first_seen' : { 'required': false, 'type' : 'text', },
      'last_seen' : { 'required': false, 'type' : 'text', },
    },
    'type': 'infrastructure',
  },
  'Intrusion Set': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'aliases' : { 'required': false, 'type' : 'textarea', },
      'first_seen' : { 'required': false, 'type' : 'text', },
      'last_seen' : { 'required': false, 'type' : 'text', },
      'goals' : { 'required': false, 'type' : 'textarea', },
      'resource_level' : { 'required': false, 'type' : 'text', },
      'primary_motivation' : { 'required': false, 'type' : 'text', },
      'secondary_motivations' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'intrusion-set',
  },
  'Location': {
    'properties' : {
      'name' : { 'required': false, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'latitude' : { 'required': false, 'type' : 'text', },
      'longitude' : { 'required': false, 'type' : 'text', },
      'precision' : { 'required': false, 'type' : 'text', },
      'region' : { 'required': false, 'type' : 'text', },
      'country' : { 'required': false, 'type' : 'text', },
      'administrative_area' : { 'required': false, 'type' : 'text', },
      'city' : { 'required': false, 'type' : 'text', },
      'street_address' : { 'required': false, 'type' : 'text', },
      'postal_code' : { 'required': false, 'type' : 'text', },
    },
    'type': 'location',
  },
  'Malware': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'malware_types' : { 'required': false, 'type' : 'textarea', },
      'is_family' : { 'required': true, 'type' : 'boolean', },
      'aliases' : { 'required': false, 'type' : 'textarea', },
      'kill_chain_phases' : { 'required': false, 'type' : 'textarea', },
      'first_seen' : { 'required': false, 'type' : 'text', },
      'last_seen' : { 'required': false, 'type' : 'text', },
      'operating_system_refs' : { 'required': false, 'type' : 'textarea', },
      'architecture_execution_envs' : { 'required': false, 'type' : 'textarea', },
      'implementation_languages' : { 'required': false, 'type' : 'textarea', },
      'capabilities' : { 'required': false, 'type' : 'textarea', },
      'sample_refs' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'malware',
  },
  'Malware Analysis': {
    'properties' : {
      'product' : { 'required': true, 'type' : 'text', },
      'version' : { 'required': false, 'type' : 'text', },
      'host_vm_ref' : { 'required': false, 'type' : 'text', },
      'operating_system_ref' : { 'required': false, 'type' : 'text', },
      'installed_software_refs' : { 'required': false, 'type' : 'textarea', },
      'configuration_version' : { 'required': false, 'type' : 'text', },
      'modules' : { 'required': false, 'type' : 'textarea', },
      'analysis_engine_version' : { 'required': false, 'type' : 'text', },
      'analysis_definition_version' : { 'required': false, 'type' : 'text', },
      'submitted' : { 'required': false, 'type' : 'text', },
      'analysis_started' : { 'required': false, 'type' : 'text', },
      'analysis_ended' : { 'required': false, 'type' : 'text', },
      'result_name' : { 'required': false, 'type' : 'text', },
      'result' : { 'required': false, 'type' : 'text', },
      'analysis_sco_refs' : { 'required': false, 'type' : 'textarea', },
      'sample_ref' : { 'required': false, 'type' : 'text', },
    },
    'type': 'malware-analysis',
  },
  'Note': {
    'properties' : {
      'abstract' : { 'required': false, 'type' : 'text', },
      'content' : { 'required': true, 'type' : 'text', },
      'authors' : { 'required': false, 'type' : 'textarea', },
      'object_refs' : { 'required': true, 'type' : 'textarea', },
    },
    'type': 'note',
  },
  'Observed Data': {
    'properties' : {
      'first_observed' : { 'required': true, 'type' : 'text', },
      'last_observed' : { 'required': true, 'type' : 'text', },
      'number_observed' : { 'required': true, 'type' : 'text', },
      'objects' : { 'required': false, 'type' : 'textarea', },
      'object_refs' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'observed-data',
  },
  'Opinion': {
    'properties' : {
      'explanation' : { 'required': false, 'type' : 'text', },
      'authors' : { 'required': false, 'type' : 'textarea', },
      'opinion' : { 'required': true, 'type' : 'text', },
      'object_refs' : { 'required': true, 'type' : 'textarea', },
    },
    'type': 'opinion',
  },
  'Report': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'report_types' : { 'required': false, 'type' : 'textarea', },
      'published' : { 'required': true, 'type' : 'text', },
      'object_refs' : { 'required': true, 'type' : 'textarea', },
    },
    'type': 'report',
  },
  'Threat Actor': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'threat_actor_types' : { 'required': false, 'type' : 'textarea', },
      'aliases' : { 'required': false, 'type' : 'textarea', },
      'first_seen' : { 'required': false, 'type' : 'text', },
      'last_seen' : { 'required': false, 'type' : 'text', },
      'roles' : { 'required': false, 'type' : 'textarea', },
      'goals' : { 'required': false, 'type' : 'textarea', },
      'sophistication' : { 'required': false, 'type' : 'text', },
      'resource_level' : { 'required': false, 'type' : 'text', },
      'primary_motivation' : { 'required': false, 'type' : 'text', },
      'secondary_motivations' : { 'required': false, 'type' : 'textarea', },
      'personal_motivations' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'threat-actor',
  },
  'Tool': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'tool_types' : { 'required': false, 'type' : 'textarea', },
      'aliases' : { 'required': false, 'type' : 'textarea', },
      'kill_chain_phases' : { 'required': false, 'type' : 'textarea', },
      'tool_version' : { 'required': false, 'type' : 'text', },
    },
    'type': 'tool',
  },
  'Vulnerability': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'external_references' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'vulnerability',
  },
}

const STIX2_SRO = {
  'Relationship': {
    'properties' : {
      'relationship_type' : { 'required': true, 'type' : 'text', },
      'description' : { 'required': false, 'type' : 'text', },
      'source_ref' : { 'required': true, 'type' : 'text', },
      'target_ref' : { 'required': true, 'type' : 'text', },
      'start_time' : { 'required': false, 'type' : 'text', },
      'stop_time' : { 'required': false, 'type' : 'text', },
    },
    'type': 'relationship',
  },
  'Sighting': {
    'properties' : {
      'description' : { 'required': false, 'type' : 'text', },
      'first_seen' : { 'required': true, 'type' : 'text', },
      'last_seen' : { 'required': true, 'type' : 'text', },
      'count' : { 'required': false, 'type' : 'text', },
      'sighting_of_ref' : { 'required': true, 'type' : 'text', },
      'observed_data_refs' : { 'required': false, 'type' : 'textarea', },
      'where_sighted_refs' : { 'required': false, 'type' : 'textarea', },
      'summary' : { 'required': false, 'type' : 'text', },
    },
    'type': 'sighting',
  },
}

const STIX2_SCO = {
  'Artifact': {
    'properties' : {
      'mime_type' : { 'required': false, 'type' : 'text', },
      'payload_bin' : { 'required': false, 'type' : 'text', },
      'url' : { 'required': false, 'type' : 'text', },
      'hashes' : { 'required': false, 'type' : 'textarea', },
      'encryption_algorithm' : { 'required': false, 'type' : 'textarea', },
      'decryption_key' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'artifact',
  },
  'Autonomous System': {
    'properties' : {
      'number' : { 'required': true, 'type' : 'text', },
      'name' : { 'required': false, 'type' : 'text', },
      'rir' : { 'required': false, 'type' : 'text', },
    },
    'type': 'autonomous-system',
  },
  'Directory': {
    'properties' : {
      'path' : { 'required': true, 'type' : 'text', },
      'path_enc' : { 'required': false, 'type' : 'text', },
      'ctime' : { 'required': false, 'type' : 'text', },
      'mtime' : { 'required': false, 'type' : 'text', },
      'atime' : { 'required': false, 'type' : 'text', },
      'contains_refs' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'directory',
  },
  'Domain Name': {
    'properties' : {
      'value' : { 'required': true, 'type' : 'text', },
      'resolves_to_refs' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'domain-name',
  },
  'Email Address': {
    'properties' : {
      'value' : { 'required': true, 'type' : 'text', },
      'display_name' : { 'required': false, 'type' : 'text', },
      'belongs_to_ref' : { 'required': false, 'type' : 'text', },
    },
    'type': 'email-addr',
  },
  'Email Message': {
    'properties' : {
      'is_multipart' : { 'required': true, 'type' : 'boolean', },
      'date' : { 'required': false, 'type' : 'text', },
      'content_type' : { 'required': false, 'type' : 'text', },
      'from_ref' : { 'required': false, 'type' : 'text', },
      'sender_ref' : { 'required': false, 'type' : 'text', },
      'to_refs' : { 'required': false, 'type' : 'textarea', },
      'cc_refs' : { 'required': false, 'type' : 'textarea', },
      'bcc_refs' : { 'required': false, 'type' : 'textarea', },
      'message_id' : { 'required': false, 'type' : 'text', },
      'subject' : { 'required': false, 'type' : 'text', },
      'received_lines' : { 'required': false, 'type' : 'textarea', },
      'additional_header_fields' : { 'required': false, 'type' : 'textarea', },
      'body' : { 'required': false, 'type' : 'textarea', },
      'body_multipart' : { 'required': false, 'type' : 'textarea', },
      'raw_email_ref' : { 'required': false, 'type' : 'text', },
    },
    'type': 'email-message',
  },
  'File': {
    'properties' : {
      'extensions' : { 'required': false, 'type' : 'textarea', },
      'hashes' : { 'required': false, 'type' : 'textarea', },
      'size' : { 'required': false, 'type' : 'text', },
      'name' : { 'required': false, 'type' : 'text', },
      'name_enc' : { 'required': false, 'type' : 'text', },
      'magic_number_hex' : { 'required': false, 'type' : 'text', },
      'mime_type' : { 'required': false, 'type' : 'text', },
      'ctime' : { 'required': false, 'type' : 'text', },
      'mtime' : { 'required': false, 'type' : 'text', },
      'atime' : { 'required': false, 'type' : 'text', },
      'parent_directory_ref' : { 'required': false, 'type' : 'text', },
      'contains_refs' : { 'required': false, 'type' : 'textarea', },
      'content_ref' : { 'required': false, 'type' : 'text', },
    },
    'type': 'file',
  },
  'IPv4 Address': {
    'properties' : {
      'value' : { 'required': true, 'type' : 'text', },
      'resolves_to_refs' : { 'required': false, 'type' : 'textarea', },
      'belongs_to_refs' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'ipv4-addr',
  },
  'IPv6 Address': {
    'properties' : {
      'value' : { 'required': true, 'type' : 'text', },
      'resolves_to_refs' : { 'required': false, 'type' : 'textarea', },
      'belongs_to_refs' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'ipv6-addr',
  },
  'MAC Address': {
    'properties' : {
      'value' : { 'required': true, 'type' : 'text', },
    },
    'type': 'mac-addr',
  },
  'Mutex': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
    },
    'type': 'mutex',
  },
  'Network': {
    'properties' : {
      'extensions' : { 'required': false, 'type' : 'textarea', },
      'start' : { 'required': false, 'type' : 'text', },
      'end' : { 'required': false, 'type' : 'text', },
      'is_active' : { 'required': false, 'type' : 'boolean', },
      'src_ref' : { 'required': false, 'type' : 'text', },
      'dst_ref' : { 'required': false, 'type' : 'text', },
      'src_port' : { 'required': false, 'type' : 'text', },
      'dst_port' : { 'required': false, 'type' : 'text', },
      'protocols' : { 'required': true, 'type' : 'textarea', },
      'src_byte_count' : { 'required': false, 'type' : 'text', },
      'dst_byte_count' : { 'required': false, 'type' : 'text', },
      'src_packets' : { 'required': false, 'type' : 'text', },
      'dst_packets' : { 'required': false, 'type' : 'text', },
      'ipfix' : { 'required': false, 'type' : 'textarea', },
      'src_payload_ref' : { 'required': false, 'type' : 'text', },
      'dst_payload_ref' : { 'required': false, 'type' : 'text', },
      'encapsulates_refs' : { 'required': false, 'type' : 'textarea', },
      'encapsulated_by_ref' : { 'required': false, 'type' : 'text', },
    },
    'type': 'network',
  },
  'Process': {
    'properties' : {
      'extensions' : { 'required': false, 'type' : 'textarea', },
      'is_hidden' : { 'required': false, 'type' : 'boolean', },
      'pid' : { 'required': false, 'type' : 'text', },
      'created_time' : { 'required': false, 'type' : 'text', },
      'cwd' : { 'required': false, 'type' : 'text', },
      'command_line' : { 'required': false, 'type' : 'text', },
      'environment_variables' : { 'required': false, 'type' : 'textarea', },
      'opened_connection_refs' : { 'required': false, 'type' : 'textarea', },
      'creator_user_ref' : { 'required': false, 'type' : 'text', },
      'image_ref' : { 'required': false, 'type' : 'text', },
      'parent_ref' : { 'required': false, 'type' : 'text', },
      'child_refs' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'process',
  },
  'Software': {
    'properties' : {
      'name' : { 'required': true, 'type' : 'text', },
      'cpe' : { 'required': false, 'type' : 'text', },
      'swid' : { 'required': false, 'type' : 'text', },
      'languages' : { 'required': false, 'type' : 'textarea', },
      'vendor' : { 'required': false, 'type' : 'text', },
      'version' : { 'required': false, 'type' : 'text', },
    },
    'type': 'software',
  },
  'URL': {
    'properties' : {
      'value' : { 'required': true, 'type' : 'text', },
    },
    'type': 'url',
  },
  'User Account': {
    'properties' : {
      'extensions' : { 'required': false, 'type' : 'textarea', },
      'user_id' : { 'required': false, 'type' : 'text', },
      'credential' : { 'required': false, 'type' : 'text', },
      'account_login' : { 'required': false, 'type' : 'text', },
      'account_type' : { 'required': false, 'type' : 'text', },
      'display_name' : { 'required': false, 'type' : 'text', },
      'is_service_account' : { 'required': false, 'type' : 'boolean', },
      'is_privileged' : { 'required': false, 'type' : 'boolean', },
      'can_escalate_privs' : { 'required': false, 'type' : 'boolean', },
      'is_disabled' : { 'required': false, 'type' : 'boolean', },
      'account_created' : { 'required': false, 'type' : 'text', },
      'account_expires' : { 'required': false, 'type' : 'text', },
      'credential_last_changed' : { 'required': false, 'type' : 'text', },
      'account_first_login' : { 'required': false, 'type' : 'text', },
      'account_last_login' : { 'required': false, 'type' : 'text', },
    },
    'type': 'user-account',
  },
  'Windows Registry Key': {
    'properties' : {
      'key' : { 'required': false, 'type' : 'text', },
      'values' : { 'required': false, 'type' : 'textarea', },
      'modified_time' : { 'required': false, 'type' : 'text', },
      'creator_user_ref' : { 'required': false, 'type' : 'text', },
      'number_of_subkeys' : { 'required': false, 'type' : 'text', },
    },
    'type': 'windows-registry-key',
  },
  'X.509 Certificate': {
    'properties' : {
      'is_self_signed' : { 'required': false, 'type' : 'boolean', },
      'hashes' : { 'required': false, 'type' : 'textarea', },
      'version' : { 'required': false, 'type' : 'text', },
      'serial_number' : { 'required': false, 'type' : 'text', },
      'signature_algorithm' : { 'required': false, 'type' : 'text', },
      'issuer' : { 'required': false, 'type' : 'text', },
      'validity_not_before' : { 'required': false, 'type' : 'text', },
      'validity_not_after' : { 'required': false, 'type' : 'text', },
      'subject' : { 'required': false, 'type' : 'text', },
      'subject_public_key_algorithm' : { 'required': false, 'type' : 'text', },
      'subject_public_key_modulus' : { 'required': false, 'type' : 'text', },
      'subject_public_key_exponent' : { 'required': false, 'type' : 'text', },
      'x509_v3_extensions' : { 'required': false, 'type' : 'textarea', },
    },
    'type': 'x509-certificate',
  },
}

const STIX_CATEGORY_TABLE = {
  'SDO': STIX2_SDO,
  'SRO': STIX2_SRO,
  'SCO': STIX2_SCO,
}

function _get_other_stix_element () {
  single_other_div = _create_single_other_object_select_div()
  const div = $('<div>', {
    'id': `div-${CONFIRM_ITEM_STIX2_ROOT}`
  })
  div.append(single_other_div)
  div.append($('<br>'))
  return div
}

function _get_required_label (prop_name) {
  const label = $('<label>', {
   'for': prop_name,
   'class': 'label-stix2-prop-required',
  })
  label.text(`${prop_name}/required`)
  return label
}

function _get_optional_label (prop_name) {
  const label = $('<label>', {
   'for': prop_name,
   'class': 'label-stix2-prop-optional',
  })
  label.text(prop_name)
  return label
}

function _get_stix2_prop_input (prop_name, target_id, object_type, prop_info) {
  const input_id = prop_name
  if (prop_info['type'] == 'text') {
    return $('<input>', {
      'type': 'text',
      'class': 'form-control other-stix2-input',
      'id': input_id,
      'data-object_type': object_type,
      'data-property': prop_name,
      'data-target_id': target_id,
      'aria-describedby': input_id,
    })
  }
  else if (prop_info['type'] == 'textarea') {
    return $('<textarea>', {
      'class': 'form-control other-stix2-input',
      'id': input_id,
      'data-object_type': object_type,
      'data-property': prop_name,
      'data-target_id': target_id,
      'aria-describedby': input_id,
    })
  }
  else if (prop_info['type'] == 'boolean') {
   const div = $('<div>' , {
     'class': 'form-group'
   })
   div.append(_get_boolean_radio_div(target_id, object_type, prop_name))
   return div
  }
  return null
}

function _get_boolean_radio_input(target_id, object_type, prop_name, b){
  const id = prop_name + '_' + Boolean(b).toString()
  const input =  $('<input>', {
    'class': 'form-check-input other-stix2-input',
    'type':  'radio',
    'name': prop_name,
    'value': b,
    'id': id,
    'data-object_type': object_type,
    'data-property': prop_name,
    'data-target_id': target_id,
  })
  input.prop('checked', false)
  return input
}

function _get_boolean_radio_input_unspecified(target_id, object_type, prop_name){
  const id = prop_name + '_unspecified'
  const input =  $('<input>', {
    'class': 'form-check-input other-stix2-input',
    'type':  'radio',
    'name': prop_name,
    'value': 'unspecified',
    'id': id,
    'data-object_type': object_type,
    'data-property': prop_name,
    'data-target_id': target_id,
  })
  input.prop('checked', true)
  return input
}

function _get_boolean_radio_label(prop_name, b){
  const id = prop_name + '_' + Boolean(b).toString()
  return $('<label>', {
    'class': 'form-check-label',
    'for' : id,
    'text': Boolean(b).toString()
  })
}

function _get_boolean_radio_label_unspecified(prop_name) {
  const id = prop_name + '_unspecified'
  return $('<label>', {
    'class': 'form-check-label',
    'for' : id,
    'text': 'unspecified'
  })
}

function _get_boolean_radio_div(target_id, object_type, prop_name){
  const div = $('<div>' , {
    'class': 'form-check'
  })
  div.append(_get_boolean_radio_input(target_id, object_type, prop_name, true))
  div.append(_get_boolean_radio_label(prop_name, true))
  div.append($('<span>').html('&nbsp;'))
  div.append(_get_boolean_radio_input(target_id, object_type, prop_name, false))
  div.append(_get_boolean_radio_label(prop_name, false))
  div.append($('<span>').html('&nbsp;:&nbsp;'))
  div.append(_get_boolean_radio_input_unspecified(target_id, object_type, prop_name))
  div.append(_get_boolean_radio_label_unspecified(prop_name))
  return div
}

function _get_stix2_prop_row (prop_name, target_id, object_type, prop_info) {
  var label = null
  if (prop_info['required'] == true) {
    label = _get_required_label(prop_name)
  }else{
    label = _get_optional_label(prop_name)
  }
  const label_col_div = $('<div>', {
    'class': 'col-sm-4'
  })
  label_col_div.append(label)

  const input_col_div = $('<div>', {
    'class': 'col-sm-8'
  })
  const input = _get_stix2_prop_input (prop_name, target_id, object_type, prop_info)
  input_col_div.append(input)

  const row_div = $('<div>', {
    'class': 'row'
  })

  row_div.append(label_col_div)
  row_div.append(input_col_div)
  return row_div
}

function _update_stix2_properties_div (object_name, root_div) {
  const category = root_div.find('input:radio[name="other_category"]:checked').val()
  const info = STIX_CATEGORY_TABLE[category][object_name]
  const properties = info['properties']
  const object_type = info['type']
  const confidence = root_div.find('input[name="confidence"]').val()

  const container_div = $('<div>', {
    'class': `container-fluid btn-group div-${CONFIRM_ITEM_STIX2_PROPERTIES}`
  })
  const label_row_div = $('<div>', {
    'class': 'row'
  })
  const label_col_div = $('<div>', {
    'class': 'col-sm-12'
  })
  const label = $('<label>', {
    'class': 'confirm-item-label',
    'for': `button-${CONFIRM_ITEM_STIX2_PROPERTIES}`,
  })
  label.text(`Add Properties of "${object_name}"`)
  label_col_div.append(label)
  label_row_div.append(label_col_div)
  container_div.append(label_row_div)

  const object_id = root_div.data('object_id')
  for (const prop_name in properties) {
    row = _get_stix2_prop_row(prop_name, object_id, object_type, properties[prop_name])
    container_div.append(row)
  }
  const div = root_div.find(DIV_OTHER_STIX_PROPERTIES_SELECTOR)
  div.empty()
  div.append(container_div)
}

const STIX_CATEGORY_LABEL_CLASS = 'stix-category-label'

function _get_stix_type_radio () {
  const div_fg = $('<div>', {
    'class': 'form-group'
  })
  for (const item in STIX_CATEGORY_TABLE) {
    const id = `${STIX_CATEGORY_LABEL_CLASS}-${item}`

    const label = $('<label>', {
      'class': 'form-check-label',
      'for' : id,
    })
    label.text(item)
    const input =  $('<input>', {
      'class': `form-check-input ${STIX_CATEGORY_LABEL_CLASS}`,
      'id':  id,
      'type':  'radio',
      'name': 'other_category',
      'value': item,
    })

    const each_div = $('<div>', {
      'class': 'form-check form-check-inline'
    })
    each_div.append(input)
    each_div.append(label)
    div_fg.append(each_div)
  }

  const form = $('<form>')
  form.append(div_fg)

  const div = $('<div>')
  div.append(form)
  return div
}

$(document).on('click', '.other-object-plus-button', function() {
  const other_div = _create_single_other_object_select_div()
  const root_div = $(`#div-${CONFIRM_ITEM_STIX2_ROOT}`)
  root_div.append(other_div)
  root_div.append($('<br>'))
})

$(document).on('click', '.other-object-remove-button', function() {
  $(DIV_OTHER_OBJECT_SELECT_SELECTOR).length
  const remove_div = $(this).parents(DIV_OTHER_OBJECT_SELECT_SELECTOR)
  remove_div.remove()
  if ($(DIV_OTHER_OBJECT_SELECT_SELECTOR).length == 0) {
    const indicator_modal_body = $('#indicator-modal-body')
    indicator_modal_body.empty()
    var div = _get_other_stix_element()
    indicator_modal_body.append(div)
  }
})

function _create_single_other_object_select_div () {
  const span = $('<span>', {
    'class': 'caret'
  })
  const button = $('<button>', {
    'class': `btn btn-small dropdown-toggle`,
    'id': `button-${CONFIRM_ITEM_STIX2_OBJECT}`,
    'data-toggle': 'dropdown',
  })
  button.text('Choose Other Class')
  button.prop('disabled', true)
  button.append(span)

  const ul = $('<ul>', {
    'class': `dropdown-menu ul-${CONFIRM_ITEM_STIX2_OBJECT}`,
  })

  const span_plus_button = $('<span>', {
    'class': 'glyphicon glyphicon-plus-sign btn-sm btn-info other-object-plus-button'
  })
  const span_remove_button = $('<span>', {
    'class': 'glyphicon glyphicon-remove-sign btn-sm btn-danger other-object-remove-button'
  })
  const label_select = $('<label>', {
    'class': 'confirm-item-label',
  })
  label_select.html('Add More STIX Object&nbsp;')
  label_select.append(span_plus_button)
  label_select.append(span_remove_button)

  const radio = _get_stix_type_radio()
  const col_radio = $('<div>', {
    'class': 'col-sm-4',
  })
  col_radio.append(label_select)
  col_radio.append($('<br/>'))
  col_radio.append($('<br/>'))
  col_radio.append(radio)

  const div_button = $('<div>', {
    'class': `col-sm-3 btn-group ${DIV_OTHER_STIX_RADIO_CLASS}`,
  })
  div_button.append(button)
  div_button.append(ul)


  const col_confidence = $('<div>', {
    'class': `col-sm-5 ${DIV_OTHER_STIX_CONFIDENCE_CLASS}`,
  })

  const row_confidence = $('<div>', {
    'class': 'row'
  })
  const col_confidence_label = $('<div>', {
    'class': 'col-sm-12'
  })
  const label_confidence = $('<label>', {
    'class': 'confirm-item-label',
    'for': 'input-confidence'
  })
  label_confidence.text('Confidence')
  col_confidence_label.append(label_confidence)
  row_confidence.append(col_confidence_label)
  col_confidence.append(row_confidence)

  const row_confidence_slider = $('<div>', {
    'class': 'row'
  })
  const col_confidence_slider = $('<div>', {
    'class': 'col-sm-6'
  })
  const input_slider = $('<input>', {
    'type': 'range',
    'min': '0',
    'max': '100',
    'class': 'slider confidence-object-slider',
  })
  const confidence = $('input[name="confidence"]').val()
  input_slider.val(confidence)
  col_confidence_slider.append(input_slider)
  row_confidence_slider.append(col_confidence_slider)
 
  const col_confidence_text = $('<div>', {
    'class': 'col-sm-3'
  })
  const input_confidence = $('<input>', {
    'type': 'text',
    'class': 'form-control input-confidence',
    'id': `input-confidence-${CONFIRM_ITEM_STIX2_OBJECT}`,
    'aria-describedby': 'input-confidence',
  })
  input_confidence.val(confidence)
  col_confidence_text.append(input_confidence)
  row_confidence_slider.append(col_confidence_text)

  const col_confidence_eval_text = $('<div>', {
    'class': 'col-sm-3'
  })
  const input_confidence_eval = $('<input>', {
    'type': 'text',
    'class': 'form-control',
    'disabled': true,
    'id': `input-confidence-eval-${CONFIRM_ITEM_STIX2_OBJECT}`,
  })
  input_confidence_eval.val(get_confidence_eval_string (confidence))
  col_confidence_eval_text.append(input_confidence_eval)
  row_confidence_slider.append(col_confidence_eval_text)
  col_confidence.append(row_confidence_slider)
 
  const row_1 = $('<div>', {
    'class': 'row'
  })
  row_1.append(col_radio)
  row_1.append(div_button)
  row_1.append(col_confidence)
  div_button.hide()
  col_confidence.hide()

  const div = $('<div>', {
    'class': `container-fluid ${DIV_OTHER_OBJECT_SELECT_CLASS}`
  })
  const object_id = new Date().getTime().toString();
  div.data('object_id', object_id)
  div.append(row_1)

  const row_2 = $('<div>', {
    'class': 'row'
  })
  const col_stix2_properties = $('<div>', {
    'class': `col-sm-12 ${DIV_OTHER_STIX_PROPERTIES_CLASS}`
  })
  row_2.append(col_stix2_properties)
  div.append(row_2)
  return div
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
    let [type_, value_, title, checked, confidence] = item
    tbody.append(
      _get_confirm_table_tr(type_, value_, title, file_id, table_id, checked, confidence)
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

function _get_confirm_table_tr_confidence_td (confidence) {
  const td = $('<td>')
  const span = $('<span>', {
    style: 'display:none'
  })
  span.text(confidence)
  td.append(span)
  const input_text = $('<input>', {
    type: 'text',
    class: `${CONFIRM_ITEM_CONFIDENCE_CLASS} form-control`,
    value: confidence
  })
  td.append(input_text)
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

function _get_custom_objects_list () {
  return Object.keys($('#confirm_indicators_modal_dialog').data('custom_object_dict')).sort()
}

function _get_custom_properties_list (custom_object) {
  const custom_object_dict = $('#confirm_indicators_modal_dialog').data('custom_object_dict')
  if (custom_object in custom_object_dict) {
    return custom_object_dict[custom_object].sort()
  } else{
    const l = []
    $.each(custom_object_dict,function (key, properties) {
      $.merge( l , properties )
    })
    return $.unique(l).sort()
  }
}

function _get_confirm_table_tr_custom_object_td_list (type_) {
  const custom_info = type_.split('CUSTOM_OBJECT:')[1]
  const index = custom_info.indexOf('/')
  const custom_object = custom_info.substr(0,index)
  const custom_property = custom_info.substr(index + 1)
  const CUSTOM_OBJECT_LIST = _get_custom_objects_list()
  const CUSTOM_PROPERTY_LIST = _get_custom_properties_list(custom_object)

  const td_list = []
  const button = $('<button>', {
    class: `btn btn-small dropdown-toggle ${CONFIRM_ITEM_TYPE_CLASS}`,
    'data-toggle': 'dropdown',
    type: custom_object
  })
  button.text(custom_object)
  const td = _get_confirtm_table_tr_td_pulldown(button, CUSTOM_OBJECT_LIST, 'dropdown-menu-custom-object-type')
  td_list.push(td)

  const button_2 = $('<button>', {
    class: `btn btn-small dropdown-toggle ${CONFIRM_ITEM_CUSTOM_PROPERTY_TYPE_CLASS}`,
    'data-toggle': 'dropdown',
    enable: false,
    type: custom_property
  })
  button_2.text(custom_property)
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

function _get_confirm_table_tr (type_, value_, title, file_id, table_id, checked, confidence) {
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
  const confidence_td = _get_confirm_table_tr_confidence_td(confidence)
  const last_td = _get_confirm_table_tr_last_td(value_)

  const tr = $('<tr>', {
    class: CONFIRM_ITEM_TR_CLASS
  })
  tr.append(first_td)
  for (const td of td_list) {
    tr.append(td)
  }
  tr.append(confidence_td)
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

function _get_confirm_table_head_confidence () {
  return $('<th>').text('Confidence')
}

function _get_confirm_table_head_last () {
  return $('<th>').text('Value')
}

function _get_confirm_table_head (file_id, table_id) {
  const th_first = _get_confirm_table_head_first(file_id, table_id)
  const th_confidence = _get_confirm_table_head_confidence()
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
  tr.append(th_confidence)
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
  let error_flag = false
  $(CONFIRM_ITEM_TR_SELECTOR).each(function (index, element) {
    const checkbox_elem = $(element).find(CONFIRM_ITEM_CHECKBOX_SELECTOR)
    const table_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TABLE_ID)
    if (checkbox_elem.prop('checked') == true) {
      const type_elem = $(element).find(CONFIRM_ITEM_TYPE_SELECTOR)
      const value_elem = $(element).find(CONFIRM_ITEM_VALUE_SELECTOR)
      const confidence_elem = $(element).find(CONFIRM_ITEM_CONFIDENCE_SELECTOR)
      const file_id = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TARGET)
      const title = checkbox_elem.attr(CONFIRM_ITEM_CHECKBOX_ATTR_TITLE)
      const type_ = type_elem.attr(LISTBOX_TYPE_ATTR)
      const confidence = confidence_elem.val()
      const value_ = value_elem.val()
      var stix2_indicator_types = 'malicious-activity'

      const item = {}
      item.type = type_
      item.confidence = confidence
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
        if(custom_property === undefined){
          alert('Set a custom property')
          error_flag = true
          return null
        }
        item.type = `${item.type}/${custom_property}`
        custom_objects.push(item)
      }
    }
  })

  $('.other-stix2-input').each(function (index, element) {
    var item = {}
    var target_id = $(element).data('target_id')
    if (target_id in other){
      item = other[target_id]
    }else {
      item.type = $(element).data('object_type')
      item.confidence = $(element).parents(DIV_OTHER_OBJECT_SELECT_SELECTOR).find(`#input-confidence-${CONFIRM_ITEM_STIX2_OBJECT}`).val()
    }
    if($(element).prop('type') == 'radio'){
      if($(element).prop('checked')){
        item[$(element).data('property')] = $(element).val()
      }
    }else{
      item[$(element).data('property')] = $(element).val()
    }
    other[target_id] = item
  })

  if (error_flag === true){
    return null
  }
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

function on_change_slider(slider, confidence_text, eval_text) {
  const confidence = Number(slider.val())
  confidence_text.val(confidence)
  set_confidence_eval(confidence, eval_text)
}

function on_change_confidence_text(slider, confidence_text, eval_text) {
  if ($.isNumeric(confidence_text.val()) == false) {
    alert('Integer (0-100) only')
    return false
  }
  const confidence = Number(confidence_text.val())
  if ((confidence < 0) || (100 < confidence)) {
    alert('Integer (0-100) only')
    return false
  }
  slider.val(confidence)
  set_confidence_eval(confidence, eval_text)
  return
}

function get_confidence_eval_string (confidence) {
  if (confidence == 0) {
    eval_string = 'None'
  } else if (confidence < 30) {
    eval_string = 'Low'
  } else if (confidence < 70) {
    eval_string = 'Middle'
  } else {
    eval_string = 'High'
  }
  return eval_string
}
 
function set_confidence_eval(confidence, eval_elem) {
  var eval_string = get_confidence_eval_string(confidence)
  eval_elem.val(eval_string)
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
  $(document).on('click', `.ul-${CONFIRM_ITEM_STIX2_OBJECT} li a`, function () {
    $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text() + ' <span class="caret"></span>')
    $(this).parents('.btn-group').find('.dropdown-toggle').attr(LISTBOX_TYPE_ATTR, $(this).text())
    const root_div = $(this).parents(DIV_OTHER_OBJECT_SELECT_SELECTOR)
    _update_stix2_properties_div($(this).text(), root_div)
  })

  $(document).on('change', `.${STIX_CATEGORY_LABEL_CLASS}`, function () {
    const category = $(this).val()

    const root_div = $(this).parents(DIV_OTHER_OBJECT_SELECT_SELECTOR)
    const select_div = root_div.find(DIV_OTHER_STIX_RADIO_SELECTOR).show()
    const confidence_div = root_div.find(DIV_OTHER_STIX_CONFIDENCE_SELECTOR)
    confidence_div.show()


    const button = select_div.find(`#button-${CONFIRM_ITEM_STIX2_OBJECT}`)
    button.prop('disabled', false)

    const ul = root_div.find(`.ul-${CONFIRM_ITEM_STIX2_OBJECT}`)
    ul.empty()

    for (const class_name in STIX_CATEGORY_TABLE[category]) {
      var a =$('<a>')
      a.text(class_name)
      var li = $('<li>').append(a)
      ul.append(li)
    }
  })

  function _get_confidence_text(elem) {
    return elem.parents(DIV_OTHER_STIX_CONFIDENCE_SELECTOR).find(`#input-confidence-${CONFIRM_ITEM_STIX2_OBJECT}`)
  }
  function _get_eval_text(elem) {
    return elem.parents(DIV_OTHER_STIX_CONFIDENCE_SELECTOR).find(`#input-confidence-eval-${CONFIRM_ITEM_STIX2_OBJECT}`)
  }
  function _get_confidence_slider(elem) {
    return elem.parents(DIV_OTHER_STIX_CONFIDENCE_SELECTOR).find('.confidence-object-slider')
  }

  $(document).on('change', '.confidence-object-slider', function () {
    const confidence_text = _get_confidence_text($(this))
    const eval_text = _get_eval_text($(this))
    on_change_slider($(this), confidence_text, eval_text)
  })

  $(document).on('change', `.input-confidence`, function () {
    const confidence_slider = _get_confidence_slider($(this))
    const confidence_text = _get_confidence_text($(this))
    const eval_text = _get_eval_text($(this))
    on_change_confidence_text(confidence_slider, confidence_text, eval_text)
  })
  $(document).on('click', ALL_CHECK_SELECTOR, function () {
    toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)), get_table_id_from_confirm_item($(this)), true)
  })

  $(document).on('click', ALL_UNCHECKED_SELECTOR, function () {
    toggle_confirm_table_checkbox(get_target_from_confirm_item($(this)), get_table_id_from_confirm_item($(this)), false)
  })
})
