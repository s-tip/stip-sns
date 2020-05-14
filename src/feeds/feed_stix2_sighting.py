import json
from stix2 import parse
from stix2.v21.sro import Sighting
from stix2.v21.sdo import ObservedData
from stix2elevator import elevate_file
from stix2elevator.options import initialize_options, set_option_value
from stix2elevator.stix_stepper import step_bundle
from stix2matcher.matcher import match
from feeds.feed_stix2 import _get_individual_identity


def insert_sighting_object(
        stix2,
        type_, value_, observable_id,
        count, first_seen, last_seen,
        stip_user):

    identity = _get_individual_identity(stip_user)
    observed_data = _get_observed_data_from_value(type_, value_, identity)
    indicator = _get_indicator_from_observed_data(stix2, observed_data)
    if indicator is None:
        return stix2
    external_references = [_get_external_reference(indicator.description, observable_id)]
    if len(first_seen) == 0:
        first_seen = None
    if len(last_seen) == 0:
        last_seen = None
    sighting = Sighting(
        created_by_ref=identity,
        sighting_of_ref=indicator,
        first_seen=first_seen,
        last_seen=last_seen,
        count=count,
        external_references=external_references
    )
    stix2.objects.append(identity)
    stix2.objects.append(sighting)
    return stix2


def _get_external_reference(title, observable_id):
    return {
        'source_name': title,
        'external_id': observable_id
    }


def convert_to_stix_1x_to_21(stix_file_path):
    # 1.x -> 2.0
    initialize_options()
    set_option_value('validator_args', '--silent')
    set_option_value('silent', 'True')
    stix20_str = elevate_file(stix_file_path)
    stix20 = _replace_stix2_tlp(stix20_str)
    # for stix2-elevator issue
    stix20_new = {}
    stix20_new['id'] = stix20['id']
    stix20_new['spec_version'] = stix20['spec_version']
    stix20_new['type'] = stix20['type']
    stix20_new['objects'] = []
    for o_ in stix20['objects']:
        if o_['type'] == 'identity':
            if 'identity_class' not in o_:
                o_['identity_class'] = 'unknown'
        stix20_new['objects'].append(o_)
    stix20_str = json.dumps(stix20_new)
    stix20_o = parse(stix20_str)
    stix20_json = json.loads(str(stix20_o))
    return convert_to_stix_20_to_21(stix20_json)


def convert_to_stix_20_to_21(stix20_json):
    # 2.0 -> 2.1
    initialize_options()
    set_option_value('validator_args', '--silent')
    set_option_value('silent', 'True')
    stix21 = step_bundle(stix20_json)

    # for stix2-elevator issue
    stix21_new = {}
    stix21_new['id'] = stix21['id']
    stix21_new['type'] = stix21['type']
    stix21_new['objects'] = []
    for o_ in stix21['objects']:
        if o_['type'] == 'indicator':
            if 'pattern_type' not in o_:
                o_['pattern_type'] = 'stix'
        if o_['type'] == 'malware':
            if 'is_family' not in o_:
                o_['is_family'] = False
        stix21_new['objects'].append(o_)
    stix2 = parse(stix21_new, allow_custom=True)
    return stix2


def _replace_stix2_tlp(stix2_str):
    stix2 = json.loads(stix2_str)
    modified_refs = {}
    objects = []

    for object_ in stix2['objects']:
        try:
            if object_['type'] == 'marking-definition':
                if object_['definition_type'] == 'tlp':
                    color = object_['definition']['tlp'].lower()
                    stix_tlp = _get_stix2_tlp(color)
                    objects.append(stix_tlp)
                    modified_refs[object_['id']] = stix_tlp['id']
                    continue
                elif object_['definition_type'] == 'ais':
                    # omit
                    modified_refs[object_['id']] = None
                    continue
            objects.append(object_)
        except KeyError:
            import traceback
            traceback.print_exc()
            objects.append(object_)

    for object_ in objects:
        if 'object_marking_refs' in object_:
            object_marking_refs = []
            for object_marking_ref in object_['object_marking_refs']:
                if object_marking_ref in modified_refs:
                    if modified_refs[object_marking_ref] is None:
                        # omit
                        pass
                    else:
                        object_marking_refs.append(modified_refs[object_marking_ref])
                else:
                    object_marking_refs.append(object_marking_ref)
            object_['object_marking_refs'] = object_marking_refs
    stix2['objects'] = objects
    return stix2


def _get_stix2_tlp(color):
    if color == 'white':
        return _get_stix2_tlp_white()
    if color == 'green':
        return _get_stix2_tlp_green()
    if color == 'amber':
        return _get_stix2_tlp_amber()
    if color == 'red':
        return _get_stix2_tlp_red()
    return None


def _get_stix2_marking_definition():
    d = {}
    d['type'] = 'marking-definition'
    d['created'] = '2017-01-20T00:00:00.000Z'
    d['definition_type'] = 'tlp'
    return d


def _get_stix2_tlp_white():
    d = _get_stix2_marking_definition()
    d['id'] = 'marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9'
    tlp = {'tlp': 'white'}
    d['definition'] = tlp
    return d


def _get_stix2_tlp_green():
    d = _get_stix2_marking_definition()
    d['id'] = 'marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da'
    tlp = {'tlp': 'green'}
    d['definition'] = tlp
    return d


def _get_stix2_tlp_amber():
    d = _get_stix2_marking_definition()
    d['id'] = 'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'
    tlp = {'tlp': 'amber'}
    d['definition'] = tlp
    return d


def _get_stix2_tlp_red():
    d = _get_stix2_marking_definition()
    d['id'] = 'marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed'
    tlp = {'tlp': 'red'}
    d['definition'] = tlp
    return d


def _get_observed_data_from_value(type_, value_, identity):
    od_time_property = str(identity.created)
    objects = {}
    observed_data_object = None
    if type_ == 'domain':
        observed_data_object = {
            'type': 'domain-name',
            'value': value_
        }
    elif type_ == 'ipv4':
        observed_data_object = {
            'type': 'ipv4-addr',
            'value': value_
        }

    if observed_data_object is None:
        return None

    objects['0'] = observed_data_object
    observed_data = ObservedData(
        first_observed=od_time_property,
        last_observed=od_time_property,
        number_observed=1,
        created_by_ref=identity,
        objects=objects
    )
    return observed_data


def _get_indicator_from_observed_data(stix2, observed_data):
    stix2_json = json.loads(str(observed_data))

    for object_ in stix2.objects:
        if object_.type != 'indicator':
            continue
        matches = match(object_.pattern, [stix2_json])
        if len(matches) == 0:
            continue
        return object_
    return None
