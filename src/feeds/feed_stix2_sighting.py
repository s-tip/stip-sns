# -*- coding: utf-8 -*
import json
from stix2 import parse
from stix2.v21.sro import Sighting
from stix2.v21.sdo import ObservedData
from stix2elevator import elevate_file
from stix2elevator.options import initialize_options, set_option_value
from stix2elevator.stix_stepper import step_bundle
from stix2matcher.matcher import match
from feeds.feed_stix2 import _get_stip_identname


def insert_sighting_object(
        stix2,
        type_, value_, observable_id,
        count, first_seen, last_seen,
        stip_user):

    identity = _get_stip_identname(stip_user)
    observed_data = get_observed_data_from_value(type_, value_, identity)
    indicator = get_indicator_from_observed_data(stix2, observed_data)
    if indicator is None:
        return stix2
    external_references = [get_external_reference(indicator.description, observable_id)]
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


def get_external_reference(title, observable_id):
    return {
        u'source_name': title,
        u'external_id': observable_id
    }


def convert_to_stix2_from_stix_file_path(stix_file_path):
    # 1.x -> 2.0
    initialize_options()
    set_option_value('validator_args', '--silent')
    set_option_value('silent', 'True')
    stix20_str = elevate_file(stix_file_path)
    stix20 = parse(replace_stix2_tlp(stix20_str))

    # 2.0 -> 2.1
    stix20_json = json.loads(str(stix20))
    stix21_json_str = step_bundle(stix20_json)
    stix2 = parse(stix21_json_str)
    return stix2


def replace_stix2_tlp(stix2_str):
    stix2 = json.loads(stix2_str)
    modified_refs = {}
    objects = []

    for object_ in stix2[u'objects']:
        try:
            if object_[u'type'] == u'marking-definition':
                if object_[u'definition_type'] == u'tlp':
                    color = object_[u'definition'][u'tlp'].lower()
                    stix_tlp = get_stix2_tlp(color)
                    objects.append(stix_tlp)
                    modified_refs[object_[u'id']] = stix_tlp[u'id']
                    continue
                elif object_[u'definition_type'] == u'ais':
                    # omit
                    modified_refs[object_[u'id']] = None
                    continue
            objects.append(object_)
        except KeyError:
            import traceback
            traceback.print_exc()
            objects.append(object_)

    for object_ in objects:
        if u'object_marking_refs' in object_:
            object_marking_refs = []
            for object_marking_ref in object_[u'object_marking_refs']:
                if object_marking_ref in modified_refs:
                    if modified_refs[object_marking_ref] is None:
                        # omit
                        pass
                    else:
                        object_marking_refs.append(modified_refs[object_marking_ref])
                else:
                    object_marking_refs.append(object_marking_ref)
            object_[u'object_marking_refs'] = object_marking_refs
    stix2[u'objects'] = objects
    return stix2


def get_stix2_tlp(color):
    if color == u'white':
        return get_stix2_tlp_white()
    if color == u'green':
        return get_stix2_tlp_green()
    if color == u'amber':
        return get_stix2_tlp_amber()
    if color == u'red':
        return get_stix2_tlp_red()
    return None


def get_stix2_marking_definition():
    d = {}
    d[u'type'] = u'marking-definition'
    d[u'created'] = u'2017-01-20T00:00:00.000Z'
    d[u'definition_type'] = u'tlp'
    return d


def get_stix2_tlp_white():
    d = get_stix2_marking_definition()
    d[u'id'] = u'marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9'
    tlp = { u'tlp': u'white'}
    d[u'definition'] = tlp
    return d


def get_stix2_tlp_green():
    d = get_stix2_marking_definition()
    d[u'id'] = u'marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da'
    tlp = {u'tlp': u'green'}
    d[u'definition'] = tlp
    return d


def get_stix2_tlp_amber():
    d = get_stix2_marking_definition()
    d[u'id'] = u'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'
    tlp = {u'tlp': u'amber'}
    d[u'definition'] = tlp
    return d


def get_stix2_tlp_red():
    d = get_stix2_marking_definition()
    d[u'id'] = u'marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed'
    tlp = {u'tlp': u'red'}
    d[u'definition'] = tlp
    return d


def get_observed_data_from_value(type_, value_, identity):
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


def get_indicator_from_observed_data(stix2, observed_data):
    stix2_json = json.loads(str(observed_data))

    for object_ in stix2.objects:
        if object_.type != 'indicator':
            continue
        matches = match(object_.pattern, [stix2_json])
        if len(matches) == 0:
            continue
        return object_
    return None
