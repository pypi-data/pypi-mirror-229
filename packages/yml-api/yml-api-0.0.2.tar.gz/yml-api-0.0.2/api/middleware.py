import json
import sys
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from api.actions import ACTIONS

VIEW = '/view/'
ADD = '/add/'
EDIT = '/edit/'
DELETE = '/delete/'
LOGIN = '/login/'
LOGOUT = '/logout/'


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE, PATCH";

        # Code to be executed for each request/response after
        # the view is called.

        return response


class AppMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_X_CSRFTOKEN' not in request.META or 'test' in sys.argv:
            stack = request.session.get('stack')
            if stack is None:
                stack = []
                request.session['stack'] = stack
            if request.path not in stack:
                stack.append(request.path)
            else:
                 for path in stack[stack.index(request.path)+1:]:
                     stack.remove(path)
            request.session.save()
            request.csrf_processing_done = True
            if request.path == '/api/v1/':
                if request.user.is_authenticated:
                    return HttpResponseRedirect('/api/v1/user/')
                else:
                    return HttpResponseRedirect('/api/v1/login/')
            elif request.path == '/api/v1/user/' and not request.user.is_authenticated:
                return HttpResponseRedirect('/api/v1/login/')
            elif request.path.endswith(ADD):
                pass
            elif request.path.endswith(EDIT):
                if request.method == 'POST':
                    request.method = 'PUT'
            elif request.path.endswith(DELETE):
                if request.method == 'POST':
                    request.method = 'DELETE'
            elif request.path.endswith(LOGIN):
                request.path_info = '/api/v1/token/'
            elif request.path.endswith(LOGOUT):
                logout(request)
                return HttpResponseRedirect('/api/v1/login/')

            response = self.get_response(request)
            # print(response.content, response.headers.get('Content-Type'), response.status_code)
            if response.status_code in [403, 500]:
                messages = {403: 'Permissão negada', 500: 'Ocorreu um erro no servidor.'}
                context = dict(status_message=messages[response.status_code])
                response = render(request, 'app.html', context=context)
            else:
                content_type = response.headers.get('Content-Type')
                if content_type and 'text/html' in content_type:
                    return HttpResponse(response.content or '')
                elif 'choices_field' in request.GET:
                    return HttpResponse(response.content)
                elif 'on_change' in request.GET:
                    return HttpResponse(response.content)
                else:
                    data = json.loads(response.content) if response.content else {}
                    if isinstance(data, dict):
                        if request.method in ['POST', 'PUT', 'DELETE'] and response.status_code in [200, 201, 204] and request.method != 'GET':
                            if 'token' in data:
                                login(request, Token.objects.get(key=data['token']).user)
                                url = '/api/v1/user/'
                                data.clear()
                            elif 'redirect' in data:
                                url = data['redirect']
                                data.clear()
                            else:
                                url = stack[-2] if len(stack) > 1 else stack[-1]
                            if data:
                                context = dict(data=data, status_code=response.status_code)
                                response = render(request, 'app.html', context=context)
                            else:
                                data = dict(
                                    redirect=response.headers.get('USER_REDIRECT', url),
                                    message=response.headers.get('USER_MESSAGE'),
                                    task=response.headers.get('USER_TASK')
                                )
                                response = JsonResponse(data)
                        else:
                            if request.method.upper() == 'GET':
                                context = dict(data=data, status_code=response.status_code)
                                response = render(request, 'app.html', context=context)
                            else:
                                if response.status_code == 400:
                                    data = dict(errors=data)
                                response = JsonResponse(data)
                    else:
                        response = HttpResponse(data)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        else:
            response = self.get_response(request)
        return response