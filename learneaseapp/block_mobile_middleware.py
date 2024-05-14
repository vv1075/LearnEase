from django.http import HttpResponseForbidden

class BlockMobileMiddleware:
    def init(self, get_response):
        self.get_response = get_response

    def call(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'Mobile' in user_agent or 'Android' in user_agent:
            return HttpResponseForbidden("Access from mobile devices is not allowed.")
        return self.get_response(request)