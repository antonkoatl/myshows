from django.http import JsonResponse
from django.views import generic

from myshows.models.person import PersonRole
from myshows.models.show import Show
from myshows.utils.trivia_helper import get_new_question


def check_trivia(request):
    result = {}

    if 'answer' in request.POST:
        correct = request.session['trivia']['question']['correct_answer_num']
        answer = int(request.POST['answer'])

        if answer == correct:
            request.session['trivia']['score'] += 1
            result['result'] = True
        else:
            request.session['trivia']['score'] -= 1
            result['result'] = False

        result['score'] = request.session['trivia']['score']
        result['correct_answer'] = request.session['trivia']['question']['correct_answer_num']

        mode = request.session['trivia']['mode']
        new_question = get_new_question(mode)
        request.session['trivia']['question'] = new_question

        result['question'] = {
                'type':  new_question['type'],
                'image': new_question['image_url'],
                'variants': new_question['text_variants']
            }

        request.session.modified = True

    elif 'mode' in request.POST:
        mode = request.POST['mode']
        request.session['trivia']['mode'] = mode
        new_question = get_new_question(mode)
        request.session['trivia']['question'] = new_question

        result['question'] = {
            'type': new_question['type'],
            'image': new_question['image_url'],
            'variants': new_question['text_variants']
        }

        request.session.modified = True

    return JsonResponse(result, status=200)


class TestView(generic.TemplateView):
    template_name = 'test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actor_roles'] = Show.objects.get(pk=1).personrole_set.filter(role=PersonRole.RoleType.ACTOR)[:5]
        return context
