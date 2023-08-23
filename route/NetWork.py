import json

from werkzeug import Request

class NetWork():
    def __init__(self,request):
        self.json = json.loads(request.data) if request.data else {}
        self.args = request.args
        self.headers = request.headers
        self.files = request.files
        self.cookies = request.cookies
        self.method = request.method
        self.path = request.path
        self.url = request.url