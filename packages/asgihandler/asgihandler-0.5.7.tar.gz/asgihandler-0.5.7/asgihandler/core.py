from .userCheck import userCheck

class ASGIHandler:
    def asgi_get_handler(scope):
        query_string = scope.get('headers')
        host = ''
        referer = ''
        operator = ''
        token = ''
        for i in query_string:
            if i[0].decode() == 'referer':
                referer = i[1].decode().split('/')[2]
                continue
            elif i[0].decode() == 'host':
                host = i[1].decode()
                continue
            elif i[0].decode() == 'operator':
                operator = i[1].decode()
                continue
            elif i[0].decode() == 'token':
                token = i[1].decode()
                continue
            else:
                continue
        if operator != '' and token != '':
            userCheck.get_auth_check(scope.get('server', ''), host, referer, operator, token, scope.get('method', ''), scope.get('path', ''), scope.get('raw_path', ''))