from flask import Flask

'''
#以这一段为示例
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index page'

@app.route('/message/<mobile_number>')  #默认string（不包含/）
def send_message(mobile_number):
    return 'Message was sent to {}'.format(mobile_number)

if __name__ == '__main__':
    print(app.url_map)
    print(app.view_functions)
    app.run()

'''
#等效
from werkzeug.routing import Rule, Map
from werkzeug.serving import run_simple
from werkzeug.exceptions import HTTPException

rules = [
    Rule('/', endpoint='index'),
    Rule('/message/<mobile_number>', endpoint='mobile')
]
url_map = Map(rules)

def application(environ, start_response):
    #绑定
    urls = url_map.bind_to_environ(environ)
    try:
        endpoint, args = urls.match()
    except HTTPException as ex:
        return ex(environ, start_response)

    headers = [('Content-Type', 'text/plain')]
    start_response('200 OK', headers)

    body = 'Rule points to {} with arguments {}' \
        .format(endpoint, args).encode('utf-8')
    return [body]

if __name__ == "__main__":
    run_simple('localhost', 5000, application)
