from werkzeug.routing import Map, Rule


class Blueprint():
    def __init__(self, name, url_prefix,converter = None):
        super().__init__()
        self.name = name
        self.url_prefix = url_prefix
        self.view_functions = dict()
        self.url_map = Map(converters=converter)

    def route(self, rule, **options):
        def decorator(view_func):
            endpoint = options.pop("endpoint", view_func.__name__)
            url = self.url_prefix + rule
            self.add_url_route(url, methods=options.pop("methods", None), **options)(view_func)
            return view_func

        return decorator

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

