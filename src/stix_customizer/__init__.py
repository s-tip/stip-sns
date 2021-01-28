import re
import json
from stix2.properties import StringProperty
from stix2.v21.sdo import CustomObject


class StixCustomizer(object):
    __instance = None
    ALLOWD_TYPE = ['string', 'list']

    @staticmethod
    def get_instance():
        if StixCustomizer.__instance is None:
            StixCustomizer()
        return StixCustomizer.__instance

    def __init__(self):
        if StixCustomizer.__instance is not None:
            raise Exception('Use get_instance method.')
        else:
            StixCustomizer.__instance = self
        self.conf_json = None
        self.custom_objects = []
        self.custom_properties = []

    def init_customizer_conf(self, conf_file_path):
        with open(conf_file_path, 'r') as fp:
            j = json.load(fp)
        objects = []
        custom_objects = []
        custom_properties = []
        if 'objects' in j:
            for o_ in j['objects']:
                if 'name' not in o_:
                    print('No name in an object. skip!!')
                    continue
                if 'properties' not in o_:
                    print('No properties in an object. skip!!')
                    continue
                properties = []
                co_properties = []
                for prop in o_['properties']:
                    if 'name' not in prop:
                        print('No name in a property. skip!!')
                        continue
                    # if 'required' not in prop:
                    #    print('No required in a property. skip!!')
                    #    continue
                    if 'type' not in prop:
                        print('No type in a property. skip!!')
                        continue
                    if prop['type'] not in self.ALLOWD_TYPE:
                        print('Invalid type. skip!!: ' + prop['type'])
                        continue
                    # co_properties.append((prop['name'], StringProperty(required=prop['required'])))
                    co_properties.append((prop['name'], StringProperty(required=False)))
                    if 'regexp' in prop:
                        try:
                            prop['pattern'] = re.compile(prop['regexp'])
                        except Exception:
                            print('Invalid regexp. skip!!: ' + prop['regexp'])
                            continue
                    else:
                        prop['pattern'] = None
                    custom_objects.append(o_['name'])
                    custom_properties.append(prop['name'])
                    properties.append(prop)

                co_properties.append(('name', StringProperty(required=True)))
                co_properties.append(('description', StringProperty(required=True)))
                @CustomObject(o_['name'], co_properties)
                class CutomObjectTemp:
                    pass
                o_['properties'] = properties
                o_['class'] = CutomObjectTemp
                objects.append(o_)
        self.conf_json = {
            'objects': objects
        }
        self.custom_objects = sorted(list(set(custom_objects)))
        self.custom_properties = sorted(list(set(custom_properties)))

    def get_custom_object_list(self):
        return self.custom_objects

    def get_custom_property_list(self):
        return self.custom_properties
        
    def get_custom_objects(self):
        if self.conf_json is None:
            return None
        if 'objects' not in self.conf_json:
            return None
        return self.conf_json['objects']
