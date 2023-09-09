from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login

from djapy.decs import djapy_view, node_to_json_response
from djapy.decs.auth import djapy_login_required
from djapy.data.dec import field_required, input_required
from djapy.decs.wrappers import object_to_json_node
from .models import Todo


def todo_post(request):
    title = request.POST.get('title')
    will_be_completed_at = request.POST.get('will_be_completed_at')
    todo = Todo.objects.create(
        title=title,
        will_be_completed_at=will_be_completed_at
    )
    return todo


@csrf_exempt
@djapy_login_required
@djapy_view(['id', 'title', 'will_be_completed_at', 'created_at'], False)
def todo_view(request):
    return {
        'post': todo_post,
        'get': Todo.objects.all
    }


class LoginQuery:
    is_sign_in: bool
    password: str


class LoginData:
    username: str
    password: str


@csrf_exempt
@node_to_json_response
@object_to_json_node(['message'], exclude_null_fields=False)
@input_required(['password'], ['is_sign_in'])
def sign_up_or_register_for_session(request, data, query, *args, **kwargs):
    print(data.password, query.is_sign_in)
    return {
        'message': 'success'
    }
