from django.db import IntegrityError
from django.http import HttpResponse


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, IntegrityError):
            return HttpResponse(b'Conflict', content_type='Application/json', status=409)

        return
