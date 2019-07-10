============
Django Tsugi
============

This is the emerging Tsugi library for Django - https://www.tsugi.org

https://pypi.org/project/django-tsugi/

Quick start
-----------

1.  Install

        pip install django-tsugi    # or pip3

2. Add "django_tsugi" to your INSTALLED_APPS and add the keyset url for your
   controlling server in `settings.py` like this::

        INSTALLED_APPS = [
            ...
            'django_tsugi',
        ]

        # To set up Tsugi
        TSUGI_KEYSET = "https://dev1.tsugicloud.org/tsugi/lti/keyset-ext";

3. Add a line to your application's `urls.py` file to handle launches and
   tell Tsugi which view to redirect to after the launch is successful::

        from . import views
        from django_tsugi.views import LaunchView

        urlpatterns = [
            path('', views.GradeView.as_view(), name='grade' ),
            path('launch', LaunchView.as_view(), {'success_url' : 'grade'} ),
        ]

4. Add the TsugiMixin to your class based view and it will define
   the `request.tsugi` variable with the user, context, and link
   information::

       from django.views import View
       from django_tsugi.mixins import TsugiMixin

       class GradeView(TsugiMixin, View):

        def get(self, request) :
            context = {'tsugi': request.tsugi}
            return render(request, 'grade/main.html', context)

       def post(self, request) :
            grade = float(request.POST.get('grade'))
            comment = request.POST.get('comment')

            retval = request.tsugi.result.gradeSend(grade, comment)
            context = {'tsugi': request.tsugi, 'retval' : retval}
            return render(request, 'grade/done.html', context)

Revising and testing locally
----------------------------

If you are running your Django tool locally and Tsugi locally, you
can use the following in `settings.py`::

    TSUGI_KEYSET = "http://localhost:8888/tsugi/lti/keyset-ext";

If you are working on a new version of this library with a django
tsugi app, you can release a new version locally with::

    python3 setup.py sdist

The artifacts reside in `dist`. To install locally::

    pip3 install --user dist/django-tsugi-*.tar.gz

Or::

    pip3 install dist/django-tsugi-*.tar.gz

Releasing to pypi.org
---------------------

This library is released to https://pypi.org/project/django-tsugi/

You need `twine` to push changes to pypi::

    pip3 install twine           # If needed
    pip install --upgrade twine  # If needed
    pip3 install twine==1.12.1   # If needed since later twines mess up

To release a whole new version, update the version in `setup.py` and then::

    rm dist/*

    python3 setup.py sdist

    twine check dist/*

    twine upload dist/*

You cannot upload the same version number twice.


References
----------

[1] How to write reusable apps - https://docs.djangoproject.com/en/2.2/intro/reusable-apps/

[2] Tutorial on Packaging and Distributing Projects - https://packaging.python.org/tutorials/packaging-projects/

[3] https://pypi.org/ - https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives

