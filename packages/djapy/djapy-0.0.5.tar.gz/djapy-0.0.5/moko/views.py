from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from djapy.decs import djapy_view, node_to_json_response
from djapy.decs.auth import djapy_login_required
from djapy.data.dec import field_required, input_required
from djapy.decs.wrappers import object_to_json_node
from .models import Todo


@djapy_login_required
@input_required(['title'])
def todo_post(request, data, query, _data, *args, **kwargs):
    will_be_completed_at = request.POST.get('will_be_completed_at')
    todo = Todo.objects.create(
        title=data.title,
        will_be_completed_at=will_be_completed_at
    )
    return todo


@djapy_login_required
@input_required([], queries=[])
def todo_get(request, data, query, *args, **kwargs):
    return Todo.objects.all()


@csrf_exempt
@djapy_login_required
@djapy_view(['id', 'title', 'will_be_completed_at', 'created_at'], True)
def todo_view(request):
    return {
        'post': todo_post,
        'patch': todo_post,
        'get': todo_get
    }


@csrf_exempt
@node_to_json_response
@object_to_json_node(['session_key', 'is_authenticated', 'get_expiry_age'], exclude_null_fields=False)
@input_required(['username', 'password'])
def login_for_session(request, data, query, *args, **kwargs):
    print(data.username, data.password)
    user = authenticate(username=data.username, password=data.password)
    if user:
        login(request, user)
    return {
        'session_key': request.session.session_key,
        'is_authenticated': user.is_authenticated if user else False,
        'get_expiry_age': request.session.get_expiry_age
    }
