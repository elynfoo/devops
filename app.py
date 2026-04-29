from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from aboutme_app import app as appA
from flaskb_app import app as appB
from myportfolio import app as appC
from ecommerce_app import app as appD

application = DispatcherMiddleware(appA, {
    '/flaskwebsite': appB,
    '/me': appC,
    '/ecommerce': appD
})

if __name__ == "__main__":
    run_simple('127.0.0.1', 5000, application, use_debugger=True, use_reloader=True)
