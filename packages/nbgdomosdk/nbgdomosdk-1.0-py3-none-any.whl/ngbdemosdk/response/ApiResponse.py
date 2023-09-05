# coding:utf-8

class CommonResponse(object):
    def __init__(self, code, message, traceId, result, **kwargs):
        self.code = code
        self.message = message
        self.trace_id = traceId
        self.result = result
        self._kwargs = kwargs

    def get_code(self):
        return self.code

    def get_message(self):
        return self.message

    def get_trace_id(self):
        return self.trace_id

    def get_result(self):
        return self.result

    def is_succeed(self):
        return self.code == 0 and self.result is not None

    def __unicode__(self):
        return u"CommonResponse(code: {}, message: {}, traceId: {}, result: {})".format(
            self.code, self.message, self.trace_id, self.result).encode('utf-8')

    if str is bytes:
        __str__ = __unicode__
    else:
        def __str__(self):
            return "CommonResponse(code: {}, message: {}, traceId: {}, result: {})".format(
                self.code, self.message, self.trace_id, self.result)
