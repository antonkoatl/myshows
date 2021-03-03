from django.views import generic

from myshows.utils.trivia_helper import get_new_question


class TriviaView(generic.TemplateView):
    template_name = "trivia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'trivia'

        if 'trivia' not in self.request.session:
            self.request.session['trivia'] = {'score': 0}

        mode = self.request.session['trivia'].get('mode', 'all')
        question = get_new_question(mode)

        context['mode'] = mode
        context['score'] = self.request.session['trivia']['score']
        context['question'] = question

        self.request.session['trivia']['mode'] = mode
        self.request.session['trivia']['question'] = question
        self.request.session.modified = True
        return context
