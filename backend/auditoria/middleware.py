import threading

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = request.user if hasattr(request, 'user') else None
        _thread_locals.remote_addr = self._get_client_ip(request)
        _thread_locals.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        response = self.get_response(request)
        
        # Cleanup
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

def get_current_request_data():
    return {
        'user': getattr(_thread_locals, 'user', None),
        'ip': getattr(_thread_locals, 'remote_addr', None),
        'user_agent': getattr(_thread_locals, 'user_agent', None),
    }
