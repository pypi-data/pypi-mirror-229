from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from djapy.decs import djapy_view, node_to_json_response
from djapy.decs.auth import djapy_login_required
from djapy.data.dec import field_required, input_required
from djapy.decs.wrappers import object_to_json_node
from djapy.parser.models_parser import models_get_data
from .models import Todo


@djapy_login_required
@input_required(['title'])
def todo_post(request, data, query, *args, **kwargs):
    will_be_completed_at = request.POST.get('will_be_completed_at')
    todo = Todo.objects.create(
        title=data.title,
        will_be_completed_at=will_be_completed_at
    )
    return todo


class Pagination:
    page: int
    page_size: int | str


def object_list_parser(object_list: QuerySet):
    return models_get_data(object_list, ["id", "title", "will_be_completed_at", "created_at"])


@djapy_login_required
@object_to_json_node(
    ['number', 'object_list', 'has_next', 'has_previous', 'previous_page_number', 'next_page_number'],
    {'object_list': (models_get_data, ["id", "title", "will_be_completed_at", "created_at"])},
    exclude_null_fields=True
)
@field_required
def todo_get(request, data: Pagination, *args, **kwargs):
    todos = Todo.objects.all()

    if type(data.page_size) == str:
        if data.page_size == 'all':
            todos = todos.all()
            return todos
        elif data.page_size.isdigit():
            data.page_size = int(data.page_size)
        else:
            data.page_size = 10

    paginator = Paginator(todos, data.page_size)  # Create paginator with todos and specify number of todos per page

    try:
        todos_pagination = paginator.page(data.page)
    except PageNotAnInteger:  # If page is not an integer, deliver first page
        todos_pagination = paginator.page(1)
    except EmptyPage:  # If page is out of range (e.g. 9999), deliver last page of results
        todos_pagination = paginator.page(paginator.num_pages)

    return todos_pagination


@csrf_exempt
@djapy_login_required
@djapy_view(['id', 'title', 'will_be_completed_at', 'created_at'], True)
def todo_view(request):
    return {
        'post': todo_post,
        'get': todo_get
    }


@csrf_exempt
@node_to_json_response
@object_to_json_node(['session_key', 'is_authenticated', 'get_expiry_age', 'csrf_token'], exclude_null_fields=False)
@input_required(['username', 'password'])
def login_for_session(request, data, *args, **kwargs):
    user = authenticate(username=data.username, password=data.password)
    if user:
        login(request, user)
    return JsonResponse({
        'session_key': request.session.session_key,
        'is_authenticated': user.is_authenticated if user else False,
        'expiry_age': request.session.get_expiry_age(),
        'csrf_token': request.COOKIES.get('csrftoken')
    })
