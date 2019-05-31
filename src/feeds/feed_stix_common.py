# -*- coding: utf-8 -*-
from mixbox import idgen
from mixbox.namespaces import Namespace
from stix.extensions.marking.simple_marking import SimpleMarkingStructure
from stix.data_marking import Marking, MarkingSpecification
from stix.core.stix_package import STIXPackage
from stix.extensions.marking import ais
from stix.extensions.marking.tlp import TLPMarkingStructure
from stix.common.information_source import InformationSource
from stix.common.identity import Identity
from cybox.common.tools import ToolInformationList,ToolInformation
import stip.common.const as const
from ctirs.models import SNSConfig

#comment,like,stix 共通処理
class FeedStixCommon(object):

    def __init__(self):
        #namespace dictionary
        self.ns_dict = {
            SNSConfig.get_stix_ns_url(): SNSConfig.get_stix_ns_name(),
        }
        ns_ctim_sns = Namespace(SNSConfig.get_stix_ns_url(),SNSConfig.get_stix_ns_name(),schema_location=None) 
        #id generator
        idgen.set_id_namespace(ns_ctim_sns)
        self.generator = idgen._get_generator()

    
    #Information Source を作成して返却
    def _make_information_source(self):
        #Tool情報作成
        tool = ToolInformation()
        tool.name = const.SNS_TOOL_NAME.decode('utf-8')
        tool.vendor = const.SNS_TOOL_VENDOR.decode('utf-8')
        tools = ToolInformationList()
        tools.append(tool)
        #Identity 作成
        identity = Identity(name=SNSConfig.get_sns_identity_name())
        #Information Source 作成
        information_source = InformationSource()
        information_source.tools = tools
        information_source.identity = identity
        return information_source

    #<marking:Marking_Structure>のStatementを作成する
    def _make_marking_specification_statement(self,key,value,controlled_structure=None):
        simple_marking_structres = SimpleMarkingStructure()
        statement = '%s: %s' % (key,value)
        simple_marking_structres.statement = statement
        marking_specification = MarkingSpecification()
        marking_specification.marking_structures = simple_marking_structres
        marking_specification.controlled_structure = controlled_structure
        return marking_specification

    #STIX Header に Marking 情報を追加する
    def _get_stix_header_marking(self,feed,creator=None):
        if creator == None:
            user = feed.user
        else:
            user = creator
        s = STIXPackage()
        if user.region is not None:
            country_name_code = user.region.country_code
            admin_area_name_code = user.region.code
        else:
            country_name_code = user.country_code
            admin_area_name_code = None
    
        industry_type = ais.OTHER
        organisation_name = ais.OTHER
    
        ais_tlp = feed.tlp
        #REDの場合はAISではエラーとなるのでNoneとする
        if ais_tlp == 'RED':
            ais_tlp = None
        ais.add_ais_marking(s,
                        False,
                        'EVERYONE',
                        ais_tlp,
                        country_name_code=country_name_code,
                        country_name_code_type='ISO_3166-1_alpha-2',
                        admin_area_name_code=admin_area_name_code,
                        organisation_name=organisation_name,
                        industry_type=industry_type.encode('utf-8'),
                        admin_area_name_code_type="ISO_3166-2",
                        )
        ais_marking_specification =  s.stix_header.handling.marking[0]
        #Marking作成
        marking = Marking()
        marking.add_marking(ais_marking_specification)
        
        #汎用のTLPmarking_specification作成
        marking_specification = self._get_tlp_marking_structure(feed)
        marking.add_marking(marking_specification)
        
        #Critical Infrastructure
        marking_critical_infrastructure = self._make_marking_specification_statement(const.STIP_SNS_CI_KEY,user.ci)
        marking.add_marking(marking_critical_infrastructure)
        
        #スクリーン名
        marking_screen_name = self._make_marking_specification_statement(const.STIP_SNS_SCREEN_NAME_KEY, user.get_screen_name())
        marking.add_marking(marking_screen_name)

        #username
        marking_user_name = self._make_marking_specification_statement(const.STIP_SNS_USER_NAME_KEY, user.username)
        marking.add_marking(marking_user_name)

        #会社名
        marking_affiliation = self._make_marking_specification_statement(const.STIP_SNS_AFFILIATION_KEY, user.affiliation)
        marking.add_marking(marking_affiliation)

        #region code
        if user.region is not None:
            marking_region_code = self._make_marking_specification_statement(const.STIP_SNS_REGION_CODE_KEY, user.region.code)
            marking.add_marking(marking_region_code)
        
        #Sharing Range
        if feed.sharing_range_type == const.SHARING_RANGE_TYPE_KEY_ALL:
            sharing_range = 'CIC Community'
        elif feed.sharing_range_type == const.SHARING_RANGE_TYPE_KEY_GROUP:
            sharing_range = 'Group: %s' % (feed.sharing_group.en_name)
        elif feed.sharing_range_type == const.SHARING_RANGE_TYPE_KEY_PEOPLE:
            sharing_range = 'People: '
            feed.save()
            for sharing_stip_user in feed.tmp_sharing_people:
                sharing_range += sharing_stip_user.username
                sharing_range += ','
            #最後の改行を取り除く
            sharing_range = sharing_range[:-1]
        marking_sharing_range = self._make_marking_specification_statement('Sharing Range',sharing_range)
        marking.add_marking(marking_sharing_range)        

        #referred_url
        if feed.referred_url is not None:
            marking_referred_url = self._make_marking_specification_statement(const.STIP_SNS_REFERRED_URL_KEY, feed.referred_url)
            marking.add_marking(marking_referred_url)        
        #stix2_package_id
        if feed.stix2_package_id is not None and len(feed.stix2_package_id) != 0:
            marking_stix2_package_id = self._make_marking_specification_statement(const.STIP_SNS_STIX2_PACKAGE_ID_KEY, feed.stix2_package_id)
            marking.add_marking(marking_stix2_package_id)        
        return marking
    
    #汎用のTLPmarking_specification作成
    def _get_tlp_marking_structure(self,feed):
        tlp_marking_structure = TLPMarkingStructure()
        tlp_marking_structure.color = feed.tlp
        marking_specification = MarkingSpecification()
        marking_specification.marking_structures = tlp_marking_structure
        marking_specification.controlled_structure = '../../../../descendant-or-self::node() | ../../../../descendant-or-self::node()/@*'
        return marking_specification
    
    #STIX Package instanceを返却する
    def get_stix_package(self):
        return self.stix_package

    #STIXのコンテンツをxml形式で返却する
    def get_xml_content(self):
        return self.stix_package.to_xml(ns_dict=self.ns_dict,encoding='utf-8')
