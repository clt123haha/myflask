#这是一段flask框架搭建的代码
#这里主要是展示一下url、endpoint 、 view function之间的对应关系
#endpoint主要是运用在blueprint

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():  #视图函数
    return 'Index Page'

@app.route('/about')
def about():
    return 'About Page'

if __name__ == '__main__':
    print(app.url_map)
    print()
    print(app.view_functions)
    app.run()

