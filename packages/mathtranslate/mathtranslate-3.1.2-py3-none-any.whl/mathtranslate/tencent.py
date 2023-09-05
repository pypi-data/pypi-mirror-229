from .tencentcloud.common import credential, exception
from .tencentcloud.tmt.v20180321 import tmt_client
from .config import config


class Translator:
    def __init__(self):
        self.cred = credential.Credential(config.tencent_secret_id, config.tencent_secret_key)
        self.client = tmt_client.TmtClient(self.cred, 'ap-shanghai')

    def is_error_request_frequency(self, e: exception.TencentCloudSDKException):
        code = e.get_code()
        if code == 'RequestLimitExceeded':
            return True
        else:
            return False

    def translate(self, text, language_to, language_from):
        request = tmt_client.models.TextTranslateRequest()
        request.Source = language_from
        request.Target = language_to
        request.SourceText = text
        request.ProjectId = 0
        request.UntranslatedText = config.math_code
        result = self.client.TextTranslate(request)
        return result.TargetText
