from drakken.core import Blueprint

bp = Blueprint(name='account', url_prefix='/account')


@bp.route('/create')
def create(request, response):
    response.text = 'This is the create account page.'


@bp.route('/login')
def login(request, response):
    response.text = 'This is the login page.'


@bp.route('/logout')
def logout(request, response):
    response.text = 'This is the logout page.'

