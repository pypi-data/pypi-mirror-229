===================
DRF React By Schema
===================

This package, with the corresponding npm package with the same name, enables a django headless infrastructure for running with react very easily, directly from your models.

Quick start:
------------

1. Add "drf-react-by-schema" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'drf-react-by-schema',
    ]
    
2. Include the URL configuration in your project urls.py like this::

    urlpatterns = [
        ...
        path('', include('drf_react_by_schema.urls')),
    ]

3. Start the development server and visit http://127.0.0.1:8000/api/endpoints and you will see all endpoints available.

You can customize viewsets and serializers to annotate other attributes.

This package offers special fields for added control over metadata directly from model.

More documentation will come one day.