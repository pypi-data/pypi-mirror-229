from django.conf import settings
from django.urls import path, include
from rest_framework_nested import routers
import importlib

from .utils import camel_to_snake

router = routers.SimpleRouter()
autocomplete_router = routers.SimpleRouter()
nested_routers = {}

modules = []
autocomplete_modules = []
for app in settings.DRF_REACT_BY_SCHEMA['APPS']:
    modules.append(f"{app}.viewsets")
    autocomplete_modules.append(f"{app}.autocomplete_viewsets")
modules.append('drf_react_by_schema.viewsets')
autocomplete_modules.append('drf_react_by_schema.autocomplete_viewsets')


def register_viewsets_routers(modules):
    global router
    global nested_routers
    # Main routes:
    for module_str in modules:
        module = importlib.import_module(module_str)
        for viewset_name, viewset in module.__dict__.items():
            if isinstance(viewset, type):
                for parent in viewset.mro():
                    if 'ViewSet' in parent.__name__:
                        name = camel_to_snake(viewset_name, 'ViewSet')
                        router.register(f"{name}", viewset, basename=name)
                        break
    # Nested routes:
    for module_str in modules:
        try:
            module = importlib.import_module(module_str)
            for item in module.__nested_viewsets__:
                if not isinstance(item, str):
                    key = item[0]
                    ViewSet = getattr(module, item[1])
                    name = camel_to_snake(
                        ViewSet.__name__, 'ViewSet').removeprefix(f"{key}_related_")
                    if not key in nested_routers:
                        nested_routers[key] = routers.NestedSimpleRouter(
                            router,
                            key,
                            lookup=key
                        )
                    nested_routers[key].register(
                        f"{name}", ViewSet, basename=f"{key}-{name}")
        except:
            pass  # There are no nested viewsets diefined in module


def register_autocomplete_viewsets_routers(modules):
    global autocomplete_router
    # Autocomplete routes:
    for module_str in modules:
        module = importlib.import_module(module_str)
        for viewset_name, viewset in module.__dict__.items():
            if isinstance(viewset, type):
                for parent in viewset.mro():
                    if 'ViewSet' in parent.__name__:
                        name = camel_to_snake(viewset_name, 'ViewSet')
                        autocomplete_router.register(
                            f"{name}", viewset, basename=name)
                        break


#################

register_viewsets_routers(modules)
register_autocomplete_viewsets_routers(autocomplete_modules)

#################

urlpatterns = [
    path('api/', include(router.urls)),
    path('autocomplete/', include(autocomplete_router.urls)),
]

#################

for nested_router in nested_routers.values():
    urlpatterns.append(
        path('api/', include(nested_router.urls)),
    )
