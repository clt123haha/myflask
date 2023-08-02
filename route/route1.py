from flask import Flask

app = Flask(__name__)

app.url_map.strict_slashes = True
#这里为False会自动进行重定向

def index():
    return 'Index Page'

def about():
    return 'About Page'

if __name__ == '__main__':
    #进行相关绑定
    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/about', 'about', about)
    print(app.url_map)
    print(app.view_functions)
    #进行打印后发现多了一个static，这个是定位static文件
    app.run()

#add_url_rule 核心代码
'''
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
	# 如果没有指定endpoint，则默认为view functon的函数名
	if endpoint is None:
	    endpoint = _endpoint_from_view_func(view_func)	
	# 将 endpoint 加入到 options(dict)
	options["endpoint"] = endpoint
	
	# methods: GET, HEAD, OPTIONS等
	methods = options.pop("methods", None)	
	# 从view function获取method，没有则为GET
	if methods is None:
        methods = getattr(view_func, "methods", None) or ("GET",)   
    # 将 methods改变为set类型
    methods = set(item.upper() for item in methods)
	
	# 将rule添加到url_map
	rule = self.url_rule_class(rule, methods=methods, **options)
    self.url_map.add(rule)
	
	# 添加view functions
	if view_func is not None:	   
	   self.view_functions[endpoint] = view_func

'''

'''
    @setupmethod
    def add_url_rule(
        self,
        rule: str,
        endpoint: t.Optional[str] = None,
        view_func: t.Optional[ft.RouteCallable] = None,
        provide_automatic_options: t.Optional[bool] = None,
        **options: t.Any,
    ) -> None:
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)  # type: ignore
        options["endpoint"] = endpoint
        methods = options.pop("methods", None)

        # if the methods are not given and the view_func object knows its
        # methods we can use that instead.  If neither exists, we go with
        # a tuple of only ``GET`` as default.
        if methods is None:
            methods = getattr(view_func, "methods", None) or ("GET",)
        if isinstance(methods, str):
            raise TypeError(
                "Allowed methods must be a list of strings, for"
                ' example: @app.route(..., methods=["POST"])'
            )
        methods = {item.upper() for item in methods}

        # Methods that should always be added
        required_methods = set(getattr(view_func, "required_methods", ()))

        # starting with Flask 0.8 the view_func object can disable and
        # force-enable the automatic options handling.
        if provide_automatic_options is None:
            provide_automatic_options = getattr(
                view_func, "provide_automatic_options", None
            )

        if provide_automatic_options is None:
            if "OPTIONS" not in methods:
                provide_automatic_options = True
                required_methods.add("OPTIONS")
            else:
                provide_automatic_options = False

        # Add the required methods now.
        methods |= required_methods

        rule = self.url_rule_class(rule, methods=methods, **options)
        rule.provide_automatic_options = provide_automatic_options  # type: ignore

        self.url_map.add(rule)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError(
                    "View function mapping is overwriting an existing"
                    f" endpoint function: {endpoint}"
                )
            self.view_functions[endpoint] = view_func

    @setupmethod
    def template_filter(
        self, name: t.Optional[str] = None
    ) -> t.Callable[[T_template_filter], T_template_filter]:
        """A decorator that is used to register custom template filter.
        You can specify a name for the filter, otherwise the function
        name will be used. Example::

          @app.template_filter()
          def reverse(s):
              return s[::-1]

        :param name: the optional name of the filter, otherwise the
                     function name will be used.
        """

        def decorator(f: T_template_filter) -> T_template_filter:
            self.add_template_filter(f, name=name)
            return f

        return decorator
'''
