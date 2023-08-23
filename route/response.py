import json

from werkzeug.wrappers import Response


class CustomResponse(Response):
    def __init__(self, data= None, status=200, headers=None, code=200, mimetype=None,isFile = False):
        self.code = code
        self.isFile = isFile
        if self.isFile:
            with open(data, "r") as file:
                data = file.read()
        if mimetype is None:
            if isinstance(data, str):
                mimetype = 'text/plain'
            elif isinstance(data, dict) or isinstance(data, list):
                data = json.dumps(data)
                mimetype = 'application/json'
            elif isinstance(data, bytes):
                mimetype = 'application/octet-stream'
            else:
                mimetype = 'application/octet-stream'
        super().__init__(data, status, headers, mimetype)

    def get_response(self, environ, start_response):
        return self(environ, start_response)


    def create_response(self):
        response = Response(self.data, self.status, self.headers, self.code, self.mimetype)
        return response.get_response


