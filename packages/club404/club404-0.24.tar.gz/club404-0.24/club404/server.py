import importlib

from club404.servers.simple import SimpleServer


def AnyServer(prefix='', config=None, app=None, pref=None):
    server = None

    # Try and resolve a valid server instance
    server = server if server else tryFastAPIServer(prefix, config, app, pref)
    server = server if server else tryFlaskServer(prefix, config, app, pref)
    server = server if server else SimpleServer(prefix, config, app)

    if server:
        print('=' * 64)
        print(f'Starting {server.__class__.__name__}...')
        print('=' * 64)

    return server


def tryFastAPIServer(prefix='', config=None, app=None, pref=None):
    namespace = 'club404.servers.fastapi'
    classname = 'FastAPIServer'
    detect = hasType('FastAPI', app, pref) or (not app and not pref)
    constr = getClass(namespace, classname) if detect else None
    if constr:
        return constr(**{
            "prefix": prefix,
            "config": config,
            "app": app
        })
    return None


def tryFlaskServer(prefix='', config=None, app=None, pref=None):
    namespace = 'club404.servers.flask'
    classname = 'FlaskServer'
    detect = hasType('Flask', app, pref) or (not app and not pref)
    constr = getClass(namespace, classname) if detect else None
    if constr:
        return constr(**{
            "prefix": prefix,
            "config": config,
            "app": app
        })
    return None


def hasType(name, target, prefers=''):
    baseClasses = all_base_classes(target.__class__) + [prefers]
    return name in baseClasses


def getClass(module, classname):
    try:
        module = importlib.import_module(module)
        constr = getattr(module, classname, None)
        return constr
    except ImportError:
        return None


def all_base_classes(type):
    res = [type.__name__]
    for cls in (cls for cls in type.__bases__ if not cls.__name__ == "object"):
        res = res + all_base_classes(cls)
    return res
