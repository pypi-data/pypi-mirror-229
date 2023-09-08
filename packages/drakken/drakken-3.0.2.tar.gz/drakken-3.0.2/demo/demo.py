"""Demo application for Drakken web framework."""
from drakken.core import Drakken
from drakken.middleware import Middleware
import drakken.security as security
from drakken.template import render, read

import account

app = Drakken()
app.register_blueprint(account.bp)


class SimpleCustomMiddleware(Middleware):
    def process_request(self, request):
        print(f'Processing request: {request.url}')

    def process_response(self, request, response):
        print(f'Processing response: {request.url}')


app.add_middleware(SimpleCustomMiddleware)


@app.route('/query')
def query(request, response):
    token = security.create_session_token()
    cookie = security.create_session_cookie(token)
    response.set_cookie(**cookie)
    context = dict(
        title='Query page',
        page=request.path,
        query=request.query_string)
    response.text = render(request, 'main.html', context=context)


@app.route('/my-home-page/')
@app.route('/home/')
@app.route('/')
def home(request, response):
    response.text = 'Hello from the HOME page'


@app.route('/about-us/', name='about')
def about(request, response):
    response.text = 'We love Python!'


@app.route('/book/')
class BooksResource:
    # Class route handler: VERY easy to build RESTful API!
    def get(self, request, response):
        response.text = 'Books page'

    def post(self, request, response):
        response.text = 'Endpoint to create a book'


@app.route('/hello/{name}/')
def greeting(request, response, name):
    response.text = f'Hello, {name}'


@app.route('/tell/{age:d}')
def tell(request, response, age):
    response.text = f'Your age is {age}'


@app.route('/robots.txt')
def robot(request, response):
    response.text = read('robots.txt')


if __name__ == "__main__":
    app.runserver()

