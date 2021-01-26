from datetime import datetime

from django.template.response import TemplateResponse


class PageGenerationTimeMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        start_time = datetime.now()
        response = view_func(request, *view_args, **view_kwargs)

        if response and isinstance(response, TemplateResponse):
            response.context_data['page_generation_time'] = datetime.now() - start_time

        return response
