from ctirs.models import SNSConfig


# Header に埋め込む動的情報
def headers(request):
    d = {}
    # SNS Header Title
    d['sns_base_header_title'] = SNSConfig.get_sns_header_title()
    # BodyColor
    d['sns_base_body_color'] = SNSConfig.get_sns_body_color()
    # GitVersion
    d['git_version'] = SNSConfig.get_sns_version()
    return d
