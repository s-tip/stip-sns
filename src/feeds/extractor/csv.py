from feeds.extractor.common import CommonExtractor, FileExtractor

class CSVExtractor(FileExtractor):
    TARGET_EXT_STRING = '.csv'

    #指定の CSV ファイルを開き、indicators, cve, threat_actors の要素を返却する
    @classmethod
    def _get_element_from_target_file(cls,file_,ta_list=[],white_list=[]):
        confirm_indicators = []
        confirm_ttps = []
        confirm_tas = []
        with open(file_.file_path,'r') as fp:
            lines = fp.readlines()
            #各行から Observable を取得する
            row = 1
            extract_dict = {}
            for line in lines:
                #末尾の改行トリミング
                line = line.rstrip()
                #この行に含まれる Property を取得する
                try:
                    #まず utf-8 で str->unicode
                    line = line.decode('utf-8')
                except:
                    #失敗したら shift_jis で str -> unicode
                    line = line.decode('shift_jis')

                #観測事象チェック
                col,type_,value = CSVExtractor._get_object_from_csv_line(line) 
                #存在する場合はリストに追加する
                if type_ is not None:
                    #重複チェック
                    duplicate_flag,extract_dict = CommonExtractor.is_duplicate(extract_dict,type_,value)
                    if duplicate_flag == False:
                        #重複していないので登録
                        #Title を作成する
                        title = '%s-Row-%d-COL-%d-%s' % (file_.file_name,row,col,type_)
                        #white_list check
                        white_flag = cls._is_included_white_list(value,white_list)
                        #white_list に含まれない場合に checked をつける  
                        confirm_indicators.append((type_,value.decode('utf-8'),title,file_.file_name,(white_flag == False)))
                #cve チェック
                cve = CSVExtractor._get_cve_from_csv_line(line)
                if cve is not None:
                    duplicate_flag,extract_dict = CommonExtractor.is_duplicate(extract_dict,cls.CVE_TYPE_STR,cve)
                    if duplicate_flag == False:
                        #重複していないので登録
                        confirm_ttps.append((cls.CVE_TYPE_STR,cve,title,file_.file_name,True))
                #Threat Actor チェック
                ta = CSVExtractor._get_ta_from_csv_line(line,ta_list)
                if ta is not None:
                    duplicate_flag,extract_dict = CommonExtractor.is_duplicate(extract_dict,cls.TA_TYPE_STR,ta)
                    if duplicate_flag == False:
                        #重複していないので登録
                        confirm_tas.append((cls.TA_TYPE_STR,ta,title,file_.file_name,True))
                row += 1
        return confirm_indicators,confirm_ttps,confirm_tas

    #あるかを判定する、最初に見つかった要素を(列数, object, type)として返却。
    #一行に複数見つかった場合でも最初に見つかった要素のみを有効として返却する
    @staticmethod
    def _get_object_from_csv_line(line):
        #csv の各項目ごとにチェック
        col = 1
        for word in line.split(','):
            if len(word) == 0:
                col += 1
                continue
            #その単語が何かの object に含まれるか
            type_,value = CommonExtractor.get_object_from_word(word)
            if type_ is not None:
                #含まれていたら返却
                return col,type_,value
            #それ以外はパス
            col += 1
        return None,None,None 

    #一行に含まれるカンマごとに区切り、cve があるかを判定する、
    #最初に見つかったCVEを返却
    #一行に複数見つかった場合でも最初に見つかった要素のみを有効として返却する
    @staticmethod
    def _get_cve_from_csv_line(line):
        for item in line.split(','):
            if len(item) == 0:
                continue
            #cve か?
            v = CommonExtractor.get_cve_from_word(item)
            if v is not None:
                return v
        return None

    #一行に含まれるカンマごとに区切り、threat_actor があるかを判定する、
    #最初に見つかった Threat Actorを返却
    #一行に複数見つかった場合でも最初に見つかった要素のみを有効として返却する
    @staticmethod
    def _get_ta_from_csv_line(line,ta_list):
        for item in line.split(','):
            if len(item) == 0:
                continue
            #Threat Actor か?
            #v = CommonExtractor.get_ta_from_line(item,ta_list)
            v = CommonExtractor.get_ta_from_words([item],ta_list)
            if v is not None:
                return v
        return None