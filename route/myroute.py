import json
from werkzeug import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest, NotFound
from route.response import CustomResponse


class Route:
    def __init__(self, converter=None):
        self.url_map = Map(converters=converter)
        self.view_functions = dict()
        self.view_args = dict()
        self.url_map.strict_slashes = True
        self.exp = {}
        self.befor_handel = []
        self.after_handel = []
        self.blueprints = []
        self.Middleware = []

    def add_url_route(self, route, **options):
        def decorator(view_func):
            endpoint = view_func.__name__
            options["endpoint"] = endpoint

            methods = options.pop("methods", None)
            if methods is None:
                methods = getattr(view_func, "methods", None) or ("GET",)
            methods = set(item.upper() for item in methods)

            rule = Rule(route, endpoint=endpoint, methods=methods)
            self.url_map.add(rule)

            self.view_functions[endpoint] = view_func

            return view_func

        return decorator

    def application(self, environ, start_response):

        request = Request(environ)
        urls = self.url_map.bind_to_environ(environ)

        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET').upper()

        endpoint = None
        view_func = None
        result = None

        print(path)

        try:
            try:
                endpoint, args = urls.match(path, method=method)
                view_func = self.view_functions.get(endpoint)
            except NotFound:
                pass

            # 如果第一次匹配失败，则尝试匹配蓝图的url_map
            if view_func is None:
                for blueprint in self.blueprints:
                    urls = blueprint.url_map.bind_to_environ(environ)
                    try:
                        endpoint, args = urls.match(path, method=method)
                        view_func = blueprint.view_functions.get(endpoint)  # 使用蓝图的view_functions
                        if view_func is not None:
                            break
                    except NotFound:
                        pass

            if view_func is None:
                try:
                    raise NotFound()
                finally:
                    response = Response(json.dumps({"code":404}), mimetype='application/json',status=404)
                    return response(environ, start_response)


            query_args = json.loads(request.data) if request.data else {}
            json_data = json.loads(request.data) if request.data else {}
            headers =json.loads(request.headers ) if request.data else {}
            files = json.loads(request.files) if request.data else {}
            cookies = json.loads(request.cookies) if request.data else {}




            params = dict(args)
            params.update(query_args)
            params.update(json_data)
            params.update(headers)
            params.update(files)
            params.update(cookies)


            # 将request对象作为第一个参数传递给视图函
            result = view_func(request, **params)
        except HTTPException as ex:
            code = ex.code
            if code in self.exp:  # Assuming ex should have 'code' attribute as it is now an HTTPException
                func =  self.exp.get(code)
                result = func()
                json_data = json.dumps(result)
                response = Response(json_data, mimetype='application/json',status=ex.code)
                return response(environ, start_response)

        except Exception as ex:
            print(type(ex).__name__)
            print(ex)
            if type(ex).__name__ in self.exp:
                func = self.exp.get(type(ex).__name__)
                result = func()
                json_data = json.dumps(result)
                response = Response(json_data, mimetype='application/json',status=500)
                return response(environ, start_response)
            else:
                response = Response('Internal Server Error', mimetype='application/json',status=500)
                return response(environ, start_response)

        if isinstance(result, CustomResponse) or isinstance(result, Response):
            return result(environ, start_response)
        result = CustomResponse(result, code=200)
        return result.get_response(environ, start_response)

        try:
            return response(environ, start_response)
        finally:
            if self.after_handel is not None:
                for handel in self.after_handel:
                    handel()
                for middleware in self.Middleware:
                    if hasattr(middleware, "after"):
                        function = getattr(middleware, "after")
                        function()

    def url_for(self, endpoint, **values):
        urls = self.url_map.bind('')
        url = urls.build(endpoint, values=values)

        return url

    def register_error_handler(self, error_type):
        def decorator(func):
            self.exp[error_type] = func
            return func  # return func unchanged

        return decorator

    def before_request(self, middleware_func):
        self.befor_handel.append(middleware_func)

    def after_request(self, middleware_func):
        (self.after_handel.append(middleware_func))


    def add_middleware(self, middleware):
        self.Middleware.append(middleware)

    def register_blueprint(self, blueprint):

        self.blueprints.append(blueprint)

    def apply_before_handlers(self,select = None):
        def decorator(view_func):
            def wrapper(*args, **kwargs):
                # 执行 before_request 中的函数
                if select is None:
                    for handler in self.befor_handel:
                        handler()
                    for middleware in self.Middleware:
                        if hasattr(middleware, "before"):
                            function = getattr(middleware, "before")
                            function()
                else:
                    for handler in self.befor_handel:
                         if handler.__name__ in select:
                            handler()
                    for middleware in self.Middleware:
                        if hasattr(middleware, "before") and middleware.__name__ in select:
                            function = getattr(middleware, "before")
                            function()

                return view_func(*args, **kwargs)

            # 使用 functools 的 wraps 装饰器来保留原始视图函数的属性
            import functools
            wrapped_view = functools.wraps(view_func)(wrapper)
            return wrapped_view

        return decorator

    def apply_after_handlers(self, select=None):
        def decorator(view_func):
            def wrapper(*args, **kwargs):
                # 调用原始视图函数
                result = view_func(*args, **kwargs)

                # 执行 after_request 中的函数
                if select is None:
                    for handler in self.after_handel:
                        handler()
                    for middleware in self.Middleware:
                        if hasattr(middleware, "after"):
                            function = getattr(middleware, "after")
                            function(result)
                else:
                    for handler in self.after_handel:
                        if handler.__name__ in select:
                            handler()
                    for middleware in self.Middleware:
                        if hasattr(middleware, "after") and middleware.__name__ in select:
                            function = getattr(middleware, "after")
                            function(result)

                return result

            # 使用 functools 的 wraps 装饰器来保留原始视图函数的属性
            import functools
            wrapped_view = functools.wraps(view_func)(wrapper)
            return wrapped_view

        return decorator














