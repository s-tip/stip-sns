import json


class StixCustomizer(object):
    __instance = None

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

    def init_custozer_conf(self, conf_file_path):
        with open(conf_file_path, 'r') as fp:
            self.j = json.load(fp)
