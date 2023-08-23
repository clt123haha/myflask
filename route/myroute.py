import http.client
import json
from werkzeug import Request, Response
from werkzeug.routing import BaseConverter, Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest, NotFound
from werkzeug.serving import run_simple
from urllib.parse import urlencode
from NetWork import NetWork
from route.Blueprint import Blueprint



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

        if self.befor_handel is not None:
            for handel in self.befor_handel:
                handel()

        for middleware in self.Middleware:
            if hasattr(middleware, "first"):
                function = getattr(middleware, "first")
                function()

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

            # 获取查询字符串参数
            query_args = json.loads(request.data) if request.data else {}
            # 获取JSON数据
            json_data = json.loads(request.data) if request.data else {}

            # 合并参数字典，将args、query_args和json_data合并
            params = dict(args)
            params.update(query_args)
            params.update(json_data)

            # 将request对象作为第一个参数传递给视图函数
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
            if type(ex).__name__ in self.exp:
                func = self.exp.get(type(ex).__name__)
                result = func()
                json_data = json.dumps(result)
                response = Response(json_data, mimetype='application/json',status=500)
                return response(environ, start_response)
            else:
                response = Response('Internal Server Error', mimetype='application/json',status=500)
                return response(environ, start_response)


        if isinstance(result, str):
            response = Response(result, mimetype='text/plain')
        elif isinstance(result, dict) or isinstance(result, list):
            response = Response(json.dumps(result), mimetype='application/json')
        else:
            response = Response(result)

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


class MobileConverter(BaseConverter):
    def __init__(self, map):
        BaseConverter.__init__(self, map)
        self.regex = r'1[35678]\d{9}'

    def to_python(self, value):
        return '{}-{}-{}'.format(value[:3], value[3:7], value[7:12])

    def to_url(self, value):
        print(value)
        return value


mobile_converter = {'mobile': MobileConverter}
route = Route(mobile_converter)


@route.add_url_route('/')
def index(request, **kwargs):
    #raise AssertionError("这只是一个测试")
    print("url:/")
    net = NetWork(request)
    print(net.args.get("str"))
    query_str = request.args.get('str')

    generated_url = route.url_for("index", str=query_str)
    return f'str: {query_str}, Generated URL: {generated_url}'


#@route.add_url_route("/<username>")
#def hi(request, username):
    #generated_url = route.url_for("hi", username=username)
    #return {"name": username, "Generated URL": generated_url}


@route.add_url_route("/phone/<mobile:phoneNumber>")
def call(request, phoneNumber):
    generated_url = route.url_for("call", phoneNumber=phoneNumber)
    return f"call {phoneNumber}, Generated URL: {generated_url}"

@route.register_error_handler(404)
def handle_404_error():
    print("404 error occurred")



@route.register_error_handler("AssertionError")
def handle_AssertionError_error():
    print("123")
    return "123"


def begin():
    print("begin")
    return 1

def over():
    print("over")
    return 1

blueprint = Blueprint("example", "/example")


@blueprint.route("/")
def hello(request, **params):
    print("hello")
    return {"message":"hello!"}



route.register_blueprint(blueprint)

route.before_request(begin)

route.after_request(over)

for blp in route.blueprints:
    print(blp.url_map)

print(route.url_map)

run_simple('localhost', 5000, route.application)












