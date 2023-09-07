import signal

from club404 import GetConfig
from club404.config import PrintConfig
from club404.router import WebRouter
from club404.templates import TemplateRouter


class MappedDict(dict):
    # Bind to the parent context and map the getters , setters and delete functions
    def __init__(self, ctx, getter=None, setter=None, delete=None):
        def not_bound(prop):
            message = 'Mapped dictionary property "%s" not implemented on %s.'
            raise Exception(message % (prop, type(self)))

        self._ctx = ctx
        self._get = getter if getter else lambda ctx: not_bound('getter')
        self._set = setter if setter else lambda ctx: not_bound('setter')
        self._del = delete if delete else lambda ctx: not_bound('delete')

    # Implement all dictionary methods
    def __getitem__(self, key): return self._get(self._ctx, key)
    def __setitem__(self, key, value): return self._set(self._ctx, key, value)
    def __delitem__(self, key): return self._del(self._ctx, key)
    def __iter__(self): return self._ctx.__dict__.__iter__(self)
    def __len__(self): return self._ctx.__dict__.__len__(self)
    def __contains__(self, x): return self._ctx.__dict__.__contains__(x)


class AbstractServer(TemplateRouter):
    app = None
    config = None

    def __init__(self, prefix='', config=None, app=None):
        config = config if config else GetConfig()
        super().__init__(prefix, base=config.templates, routes=config.routes)
        self.config = config
        self.app = app

    def start(self):
        raise Exception('Not implemented: BaseServer.start()')

    def register(self, router):
        # Get the raw list of routes, eg: routes[VERB][path] = func(req, resp)
        routes = router._routes() if isinstance(router, WebRouter) else router

        # Update our internal routes
        for verb in routes:
            # Create verb entry if not exist
            for sub_path in routes[verb]:
                # Register the route in this we
                route = self.prefix + sub_path
                action = routes[verb][sub_path]
                self.route(verb, route)(action)

    def route(self, verb, route):
        raise Exception('Not implemented: BaseServer.route(verb, route)')

    def static(self, path):
        raise Exception('Not implemented: BaseServer.static(path)')

    def onStart(self):
        signal.signal(signal.SIGINT, self.onExit)

        # Print server header with config details
        PrintConfig(self.config)

    def onExit(self, signum, frame): return exit(1)

    def discover(self, path="./routes"):
        print(' - Auto discovering routes in: %s' % path)
