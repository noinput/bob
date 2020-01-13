# WSGI wrapper for bobweb
#from werkzeug.contrib.fixers import ProxyFix
from bobweb import app


if __name__ == '__main__':
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
