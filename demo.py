from werkzeug import Response, run_simple
from werkzeug.routing import BaseConverter
from route import Blueprint, NetWork,Route



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
def begin():
    print("begin")


def over():
    print("over")

route.before_request(begin)
route.after_request(over)

@route.register_error_handler(404)
def handle_404_error():
    print("404 error occurred")

@route.register_error_handler("AssertionError")
def handle_AssertionError_error():
    print("123")
    return "123"

@route.add_url_route('/')
@route.apply_before_handlers()
@route.apply_after_handlers()
def index(request, **kwargs):
    print("url:/")
    net = NetWork(request)
    print(net.args.get("str"))
    query_str = request.args.get('str')

    generated_url = route.url_for("index", str=query_str)
    return f'str: {query_str}, Generated URL: {generated_url}'

@route.add_url_route('/error/AssertionError')
def AssertionError(request, **kwargs):
    raise AssertionError("这只是一个测试")


@route.add_url_route("/<username>")
def hi(request, username):
    generated_url = route.url_for("hi", username=username)
    return {"name": username, "Generated URL": generated_url}


@route.add_url_route("/phone/<mobile:phoneNumber>")
def call(request, phoneNumber):
    generated_url = route.url_for("call", phoneNumber=phoneNumber)
    return f"call {phoneNumber}, Generated URL: {generated_url}"


blueprint = Blueprint("example", "/example")


@blueprint.route("/one")
def one(request, **params):
    print("hello")

    return {"message":"hello!"}

@blueprint.route("/two")
def two(request, **params):
    response = Response("Hello, Custom MIME Type!", status=200, mimetype="text/plain")
    return response


route.register_blueprint(blueprint)

for blp in route.blueprints:
    print(blp.url_map)

print(route.url_map)

run_simple('localhost', 5000, route.application)