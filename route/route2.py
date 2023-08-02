from flask import Flask
from werkzeug.routing import Map, Rule


app = Flask(__name__)

def index():
    return 'Index Page'

def about():
    return 'About Page'

#多对一
url_rules = [
    Rule('/', endpoint='index', methods=['GET']),
    Rule('/about', endpoint='about', methods=['GET']),
    Rule('/same',endpoint='about',methods=['GET'])
]

'''
- Map.add() ：  封装方法，调用 Rule.bind()
- Rule.bind() : 核心代码，提供 Map 与 Rule 绑定的实现

'''

#bind()
'''
    def bind(self, map: "Map", rebind: bool = False) -> None:
        """Bind the url to a map and create a regular expression based on
        the information from the rule itself and the defaults from the map.

        :internal:
        """
        if self.map is not None and not rebind:
            raise RuntimeError(f"url rule {self!r} already bound to map {self.map!r}")
        self.map = map
        if self.strict_slashes is None:
            self.strict_slashes = map.strict_slashes
        if self.merge_slashes is None:
            self.merge_slashes = map.merge_slashes
        if self.subdomain is None:
            self.subdomain = map.default_subdomain
        self.compile()
'''

map = Map(url_rules)

app.url_map = map

app.view_functions = {
    'index': index,
    'about': about
}

print(app.url_map)
print(app.view_functions)




#Rile初始
'''
def __init__(
    self,
    string,
    defaults=None,
    subdomain=None,
    methods=None,
    build_only=False,
    endpoint=None,
    strict_slashes=None,
    redirect_to=None,
    alias=False,
    host=None,
)
    if methods is not None:
        if isinstance(methods, str):
            raise TypeError("'methods' should be a list of strings.")
    
        methods = {x.upper() for x in methods}
    
        if "HEAD" not in methods and "GET" in methods:
            methods.add("HEAD")
    
        if websocket and methods - {"GET", "HEAD", "OPTIONS"}:
            raise ValueError(
                "WebSocket rules can only use 'GET', 'HEAD', and 'OPTIONS' methods."
            )
    
    self.methods = methods
'''
