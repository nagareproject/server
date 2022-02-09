import os
from nagare import presentation


class {{cookiecutter.project_slug}}(object):
    pass


@presentation.render_for({{cookiecutter.project_slug}})
def render(self, h, *args):
    NAGARE = 'http://www.nagare.org/'
    NAGARE_DOC = NAGARE + 'doc/'

    this_file = __file__
    if this_file.endswith('.pyc'):
	this_file = __file__[:-1]

    models_file = os.path.join(os.path.dirname(__file__), 'models.py')

    h.head << h.head.title('Up and Running !')

    h.head.css_url('/static/nagare/application.css')
    h.head.css(
	'defaultapp',
	'''#main {
	       margin-left: 20px;
	       padding-bottom: 100px;
	       background: url(/static/nagare/img/sakura.jpg) no-repeat 123px 100%;
	}'''  # noqa: E501
    )

    with h.div(id='body'):
	h << h.a(
	    h.img(src='/static/nagare/img/logo.png'),
	    id='logo',
	    href=NAGARE, title='Nagare home'
	)

	with h.div(id='content'):
	    h << h.div('Congratulations!', id='title')

	    with h.div(id='main'):
		h << h.h1('Your application is running')

		h << 'You can now:'
		with h.ul:
		    with h.li:
			h << 'If your application uses a database, '
			h << 'add your database entities into '
			h << h.em(models_file)
		    with h.li:
			h << 'Add your application components into ',
			h << h.em(this_file)
			h << ' or create new files'

		h << h.em("Have fun!")

    with h.div(id='footer'):
	with h.table:
	    with h.tr:
		h << h.th('About Nagare')
		h << h.th('Community')
		h << h.th('Learn', class_='last')

	    with h.tr:
		with h.td:
		    with h.ul:
			h << h.li(h.a('Description', href=NAGARE_DOC+'description'))  # noqa: E501
			h << h.li(h.a('Features', href=NAGARE_DOC+'features'))  # noqa: E501
			h << h.li(h.a('License', href=NAGARE_DOC+'license'))  # noqa: E501

		with h.td:
		    with h.ul:
			h << h.li(h.a('Github repositories', href='http://github.com/nagareproject'))  # noqa: E501
			h << h.li(h.a('Mailing list', href='http://groups.google.com/group/nagare-users'))  # noqa: E501
			h << h.li(h.a('Bugs report', href='https://github.com/nagareproject/core/issues'))  # noqa: E501

		with h.td(class_='last'):
		    with h.ul:
			h << h.li(h.a('Documentation', href=NAGARE_DOC))  # noqa: E501
			h << h.li(h.a('Demonstrations portal', href=NAGARE+'portal'))  # noqa: E501
			h << h.li(h.a('Demonstrations', href=NAGARE+'demo'))  # noqa: E501
			h << h.li(h.a('Wiki Tutorial', href=NAGARE+'wiki'))  # noqa: E501

    return h.root


# ---------------------------------------------------------------

app = {{cookiecutter.project_slug}}

