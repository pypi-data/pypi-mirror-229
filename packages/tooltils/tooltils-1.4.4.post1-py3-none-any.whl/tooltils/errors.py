"""Package specific exceptions"""

class TooltilsError(Exception):
    """Base class for tooltils specific errors"""

class ShellCodeError(TooltilsError):
    """Shell command returned non-zero exit code"""

    def __init__(self, code: int=-1, 
                 message: str=''):
        self.code:    int = code
        self.message: str = message
    
    def __str__(self):
        if self.message:
            return self.message
        elif self.code:
            return f'Shell command returned non-zero exit code {self.code}'
        else:
            return 'Shell command returned non-zero exit code'

class ShellTimeoutExpired(TooltilsError):
    """Shell command timed out"""
    
    def __init__(self, message: str=''):
        self.message: str = message
    
    def __str__(self):
        if self.message:
            return self.message

        return 'Shell command timed out'

class ShellCommandError(TooltilsError):
    """Shell command exited while in process"""

    def __init__(self, message: str=''):
        self.message: str = message
    
    def __str__(self):
        if self.message:
            return self.message

        return 'Shell command exited while in process'

class ShellCommandNotFound(TooltilsError):
    """Unable to locate shell command or program"""

    def __init__(self, message: str=''):
        self.message: str = message
    
    def __str__(self):
        if self.message:
            return self.message

        return 'Unable to locate shell command or program'

class ConnectionError(TooltilsError):
    """Connection to URL failed"""

    def __init__(self, message: str=''):
        self.message: str = message
    
    def __str__(self):
        if self.message:
            return self.message

        return 'Connection to URL failed'

class ConnectionTimeoutExpired(TooltilsError):
    """Request read timeout expired"""

    def __init__(self, message: str=''):
        self.message: str = message
    
    def __str__(self):
        if self.message:
            return self.message

        return 'Request read timeout expired'

class StatusCodeError(TooltilsError):
    """Status code of URL response is not 200"""

    _status_codes: dict[int, str] = {
        100: 'Continue',
        101: 'Switching Protocols',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        307: 'Temporary Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Content-Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request URL Too Long',
        415: 'Unsupported Media Type',
        416: 'Requested Range Not Satisfiable',
        417: 'Expectation Failed',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
    }
    
    def __init__(self, 
                 code: int=0, 
                 reason: str=''):
        self.code:   int = code
        self.reason: str = reason

    def __str__(self):
        if self.reason:
            try:
                code = {v: k for (k, v) in self.status_codes.items(
                        )}[self.reason]

                return '{} {}'.format(code, self.reason)
            except KeyError:
                pass
        elif self.code:
            return '{} {}'.format(self.code, self.status_codes[self.code])
        elif self.code and self.reason:
            return '{} {}'.format(self.code, self.reason)
        
        return 'URL response returned non 200s status code'

    @property
    def status_codes(self):
        """List of valid HTTP response status codes (100-505)"""

        return self._status_codes

    @status_codes.setter
    def status_codes(self, value):
        raise AttributeError('Status_codes is a constant value ' +
                             'and may not be changed')

class UnicodeDecodeError(TooltilsError):
    """Unable to decode text input"""

    def __init__(self, message: str=''):
        self.message: str = message
    
    def __str__(self):
        if self.message:
            return self.message

        return 'Unable to decode text input'

