============
Django Tsugi
============

This is the emerging Tsugi library for Django - https://www.tsugi.org

https://pypi.org/project/django-tsugi/

Quick start
-----------

1.  Install

        pip install django-tsugi

2. Add "django_tsugi" to your INSTALLED_APPS setting like this::

        INSTALLED_APPS = [
            ...
            'django_tsugi',
        ]

3. Add a line to your application's `urls.py` file to handle launches and
   tell Tsugi which view to redirect to after the launch is successful.

        from . import views
        from django_tsugi.views import LaunchView
    
        urlpatterns = [
            path('', views.GradeView.as_view(), name='grade' ),
            path('launch', LaunchView.as_view(), {'success_url' : 'grade'} ),
        ]

4. Add the TsugiMixin to your class based view and it will define
   the `request.tsugi` variable with the user, context, and link
   information.

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

Releasing to pypy.org
---------------------

    python3 setup.py sdist

The artifacts reside in `dist`. To install locally:

    pip install --user dist/django-tsugi-0.1.tar.gz

Or

    pip3 install dist/django-tsugi-0.1.tar.gz

To uninstall

    pip uninstall django-tsugi

To Upload

    pip3 install twine

    twine upload dist/*

References
----------

[1] How to write reusable apps - https://docs.djangoproject.com/en/2.2/intro/reusable-apps/

[2] Tutorial on Packaging and Distributing Projects - https://packaging.python.org/tutorials/packaging-projects/

[3] https://pypi.org/ - https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives
