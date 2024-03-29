from feeds.extractor.common import CommonExtractor, FileExtractor, CTIElementExtractorBean, BaseExtractor
from stip.common.stix_customizer import StixCustomizer


class CSVExtractor(FileExtractor):
    TARGET_EXT_STRING = '.csv'

    # 指定の CSV ファイルを開き、indicators, cve, threat_actors の要素を返却する
    @classmethod
    def _get_element_from_target_file(cls, file_, list_param):
        eeb = CTIElementExtractorBean()
        custom_objects = StixCustomizer.get_instance().get_custom_objects()
        ta_list = list_param.ta_list
        white_list = list_param.white_list
        with open(file_.file_path, 'rb') as fp:
            lines = fp.readlines()
            # 各行から Observable を取得する
            row = 1
            extract_dict = {}
            for line in lines:
                # 末尾の改行トリミング
                line = line.rstrip()
                # この行に含まれる Property を取得する
                try:
                    # まず utf-8 で str->unicode
                    line = line.decode('utf-8')
                except BaseException:
                    # 失敗したら shift_jis で str -> unicode
                    line = line.decode('shift_jis')

                # 観測事象チェック
                col, type_, value = CSVExtractor._get_object_from_csv_line(line)
                # 存在する場合はリストに追加する
                if type_ is not None:
                    # 重複チェック
                    duplicate_flag, extract_dict = CommonExtractor.is_duplicate(extract_dict, type_, value)
                    if not duplicate_flag:
                        # 重複していないので登録
                        # Title を作成する
                        title = '%s-Row-%d-COL-%d-%s' % (file_.file_name, row, col, type_)
                        # white_list check
                        white_flag = cls._is_included_white_list(value, white_list)
                        # white_list に含まれない場合に checked をつける
                        eeb.append_indicator((type_, value, title, file_.file_name, (white_flag is False)))
                # cve チェック
                cve, col = CSVExtractor._get_cve_from_csv_line(line)
                if cve is not None:
                    duplicate_flag, extract_dict = CommonExtractor.is_duplicate(extract_dict, cls.CVE_TYPE_STR, cve)
                    if not duplicate_flag:
                        # 重複していないので登録
                        title = '%s-Row-%d-COL-%d-%s' % (file_.file_name, row, col, cls.CVE_TYPE_STR)
                        eeb.append_ttp((cls.CVE_TYPE_STR, cve, title, file_.file_name, True))
                # Threat Actor チェック
                ta, col = CSVExtractor._get_ta_from_csv_line(line, ta_list)
                if ta is not None:
                    duplicate_flag, extract_dict = CommonExtractor.is_duplicate(extract_dict, cls.TA_TYPE_STR, ta)
                    if not duplicate_flag:
                        # 重複していないので登録
                        title = '%s-Row-%d-COL-%d-%s' % (file_.file_name, row, col, cls.TA_TYPE_STR)
                        eeb.append_ta((cls.TA_TYPE_STR, ta, title, file_.file_name, True))

                custom_object_list, col = CSVExtractor._get_custom_objects_from_csv_line(line, custom_objects)
                for co in custom_object_list:
                    obj_name, prop_name, obj_value = co
                    type_ = 'CUSTOM_OBJECT:%s/%s' % (obj_name, prop_name)
                    title = '%s-Row-%d-COL-%d-%s' % (file_.file_name, row, col, type_)
                    duplicate_flag, extract_dict = CommonExtractor.is_duplicate(extract_dict, type_, obj_value)
                    if not duplicate_flag:
                        eeb.append_custom_object((type_, obj_value, title, file_.file_name, True))
                row += 1
        return eeb

    # あるかを判定する、最初に見つかった要素を(列数, object, type)として返却。
    # 一行に複数見つかった場合でも最初に見つかった要素のみを有効として返却する
    @staticmethod
    def _get_object_from_csv_line(line):
        # csv の各項目ごとにチェック
        col = 1
        for word in line.split(','):
            if len(word) == 0:
                col += 1
                continue
            # その単語が何かの object に含まれるか
            type_, value = CommonExtractor.get_object_from_word(word)
            if type_ is not None:
                # 含まれていたら返却
                return col, type_, value
            # それ以外はパス
            col += 1
        return None, None, None

    # 一行に含まれるカンマごとに区切り、cve があるかを判定する、
    # 最初に見つかったCVEを返却
    # 一行に複数見つかった場合でも最初に見つかった要素のみを有効として返却する
    @staticmethod
    def _get_cve_from_csv_line(line):
        col = 1
        for item in line.split(','):
            if len(item) == 0:
                col += 1
                continue
            # cve か?
            v = CommonExtractor.get_cve_from_word(item)
            if v is not None:
                return v, col
        return None, None

    # 一行に含まれるカンマごとに区切り、threat_actor があるかを判定する、
    # 最初に見つかった Threat Actorを返却
    # 一行に複数見つかった場合でも最初に見つかった要素のみを有効として返却する
    @staticmethod
    def _get_ta_from_csv_line(line, ta_list):
        col = 1
        for item in line.split(','):
            if len(item) == 0:
                col += 1
                continue
            # Threat Actor か?
            v = CommonExtractor.get_ta_from_words([item], ta_list)
            if v is not None:
                return v, col
        return None, None

    @staticmethod
    def _get_custom_objects_from_csv_line(line, custom_objects):
        col = 1
        for item in line.split(','):
            if len(item) == 0:
                col += 1
                continue
            v = CSVExtractor._get_custom_objects_from_words([item], custom_objects)
            if len(v) > 0:
                return v, col
        return [], None


    @staticmethod
    def _get_custom_objects_from_words(words, custom_objects):
        ret = []
        if custom_objects is None:
            return ret
        for word in words:
            word = BaseExtractor._remove_parentheses(word)
            for o_ in custom_objects:
                for prop in o_['properties']:
                    if prop['pattern'] is not None:
                        matches = prop['pattern'].findall(word)
                        if len(matches) == 0:
                            continue
                        ret.append((
                            BaseExtractor.decode(o_['name']),
                            BaseExtractor.decode(prop['name']),
                            BaseExtractor.decode(matches[0])))
        return ret
