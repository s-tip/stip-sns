# -*- coding: utf-8 -*-
import pytz
import datetime
from stix.core.stix_package import STIXPackage
from stix.core.stix_header import STIXHeader
from feeds.feed_stix_common import FeedStixCommon

class FeedStixLike(FeedStixCommon):
    def __init__(self,origin_feed,like,creator=None):
        super(FeedStixLike,self).__init__()
        self.stix_package = self._make_stix_package(origin_feed,like,creator)
        self.file_name = ''
        
    def _get_stix_header(self,origin_feed,like,creator=None):
        origin_feed_pacakge_id = origin_feed.package_id
        #header作成
        stix_header = STIXHeader()
        if like:
            #like -> unlike
            stix_header.title = 'Unlike to %s' % (origin_feed_pacakge_id)
            stix_header.description = 'Unlike to %s' % (origin_feed_pacakge_id)
            self.file_name = 'Unlike_%s' % (origin_feed_pacakge_id)
        else:
            #unlike -> like
            stix_header.title = 'Like to %s' % (origin_feed_pacakge_id)
            stix_header.description = 'Like to %s' % (origin_feed_pacakge_id)
            self.file_name = 'Like_%s' % (origin_feed_pacakge_id)
        #TLP などの情報は orginal_feed と合わせる
        stix_header.handling = self._get_stix_header_marking(origin_feed,creator)
        #Information Source 格納
        stix_header.information_source = self._make_information_source()
        return stix_header

    #feed情報から STIX 作成する
    def _make_stix_package(self,origin_feed,like,creator=None):
        #package ID作成
        package_id = self.generator.create_id(prefix='Package')

        #package作成
        stix_package = STIXPackage(id_=package_id)
        stix_package.timestamp = datetime.datetime.now(tz=pytz.timezone(origin_feed.user.timezone))
        
        #header格納
        stix_package.stix_header = self._get_stix_header(origin_feed,like,creator)
            
        #Like元の Feed の Package ID を Related Package に追加する
        stix_package.add_related_package(origin_feed.package_id)
        return stix_package
    
