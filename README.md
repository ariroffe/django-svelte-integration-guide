# Django + Svelte Integration Guide

This guide will walk you through creating a Django and Svelte project (without SvelteKit), serving the Svelte files directly from Django.

It is recommended that you follow the instructions along instead of cloning this repo
(if you clone, make sure to modify the `SECRET_KEY`, check for newer versions of the packages, etc.).

This guide was heavily inspired by other online resources. See below for the credits.

It follows what I consider best practices as of september of 2022. It may need to be updated in the future. I may or may not do that.

Needless to say, this is what works for me personally. I am an academic, not a professional developer. I do not provide any guarantees that it has no flaws, nor that it will work for your particular purposes. So, use it at your own risk. Also, it may need to be modified further for use in a production environment.


## Dev setup

### 1. Create a directory and a python virtual environment, install Django

Open a terminal in the parent directory to your project's location and enter

```console
mkdir django_svelte
cd django_svelte
```

Call your project whatever you want, it doesn't have to be `django_svelte`.

There are many ways to create a virtual environment. Choose whichever you like. For instance:

- virtualenv
```console
python3 -m venv venv
source venv/bin/activate
pip install django
```

- Poetry
```
poetry init
poetry add django
```


### 2. Start your Django project

```console
django-admin startproject project .
```

I usually like to call the Django project config directory ``project``.
You can rename it if you have different preferences.

Also, notice the dot at the end of the command, I'm creating the project inside the
current working directory (which in my case is `django_svelte/`).

You can check that this worked correctly by running `python manage.py runserver` in your terminal. 
Then open your browser and navigate to `http://localhost:8000/`. 
You should see the default Django page.


### 3. Setup a Svelte template project

I'll create my Svelte project inside a `frontend/` directory. 
Again, change this if you wish.

```console
npm create vite@latest frontend -- --template svelte
cd frontend
npm install
cd ..
```

To check that the installation worked correctly, open another terminal,
navigate to `frontend/` and run `npm run dev`. After this, open your browser and
go to `http://localhost:5173/`. You should see the default Vite + Svelte page.

If you edit `frontend/src/App.svelte` you should see the changes immediately 
reflected in the browser (Vite's hot module reloading should be working).


### 4. Create a Django app

I will call my new app `spa`, you can call it whatever you like 
(`core` and `main` are other popular choices).

```console
python manage.py startapp spa
```

Remember to add `"spa"` (or whatever you called it) to `INSTALLED_APPS` inside 
`project/settings.py`.


### 5. Create a base template, view and url

Create a base template in ``spa/templates/frontend/base.html``. 
For now, it should only contain the following:

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Django + Svelte Integration</title>

  <script type="module" src="http://localhost:3000/@vite/client"></script>
</head>

<body>
  
  <div id="app"></div>
  
  <!-- Use the port that npm run dev runs in. Point the URL to your main.js file. -->
  <script type="module" src="http://localhost:5173/src/main.js"></script>

</body>

</html>
```

Change `spa/views.py` to the following:

```python
from django.views.generic import TemplateView

class SpaView(TemplateView):
    template_name = "frontend/base.html"
```

We also need to reference this view in `spa/urls.py` (create this file)

```python
from django.urls import path

from . import views

urlpatterns = [
    path('', views.SpaView.as_view(), name='spa'),
]
```

And include these urls in your global `project/urls.py` file:

```python
from django.contrib import admin
from django.urls import path, include  # <-- changed

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('spa.urls')),  # <-- new
]
```

Now open a terminal and run `npm run dev`. In a second terminal (*with the first one
still open*) run `python manage.py runserver`. In your browser, navigate to 
`http://localhost:8000/`. You should now be seeing Svelte's default page again. 
But, notice that you are now rendering it *from Django's development server*.

However, there is a problem. You are not seeing the Svelte and Vite logos. We'll fix
this in the next section.


### 6. Serving Svelte assets from Django in debug mode

If you look at your `runserver`'s terminal log, you'll see that there are two requests
that are returning a 404 response:

```console
[15/Sep/2022 22:23:29] "GET /vite.svg HTTP/1.1" 404 2261
[15/Sep/2022 22:23:29] "GET /src/assets/svelte.svg HTTP/1.1" 404 2300
```

This is because the file at `frontend/src/App.svelte` contains the following lines:

```sveltehtml
<script>
  import svelteLogo from './assets/svelte.svg'  // <-- here
  (...)
</script>

<main>
  <div>
    <a href="https://vitejs.dev" target="_blank"> 
      <img src="/vite.svg" class="logo" alt="Vite Logo" />  <!-- here -->
    </a>
    <a href="https://svelte.dev" target="_blank"> 
      <img src={svelteLogo} class="logo svelte" alt="Svelte Logo" />  <!-- here -->
    </a>
    (...)
  </div>
</main>
```

When the Django development server encounters (the compiled version of) these lines,
it generates requests to those URLs, which it obviously cannot find (since there are no
`assets` subdirectory and `vite.svg` file in your Django project's main directory).
To fix this, we'll do three things.

Firstly, to have a uniform way of importing assets from Svelte, move the `vite.svg` file
from `frontend/public` into `frontend/src/assets`, and add the import in `App.svelte`

```sveltehtml
<script>
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from './assets/vite.svg'  // <-- new
  (...)
</script>
<main>
  (...)
      <img src={viteLogo} class="logo" alt="Vite Logo" />  <!-- changed -->
  (...)
</main>>
```

Secondly, add the following line to the file located in `frontend/vite.config.js`

```javascript
// https://vitejs.dev/config/
export default defineConfig({
  base: "/static/",  // <-- new
  plugins: [svelte()]
})
```

The value needs to coincide with the setting for Django's `STATIC_URL`
(which is `static/` by default).

This tells Vite that the base public URL will be `/static/`.  I.e. Svelte will 
prepend `/static/` to you JS asset imports, your css `url()` calls, etc. If you run
both the Django and Svelte dev servers simultaneously again, you'll see that now
the 404 responses are to the following two requests:

```console
[15/Sep/2022 22:37:50] "GET /static/src/assets/svelte.svg HTTP/1.1" 404 1822
[15/Sep/2022 22:37:50] "GET /static/src/assets/vite.svg HTTP/1.1" 404 1816
```

Now, we can just tell Django to look for static files in the Svelte project directory. 
In your `project/settings.py` add the following two lines:

```python
# Point it to the directory where your Svelte project is located
VITE_APP_DIR = BASE_DIR.joinpath("frontend")
if DEBUG:
    STATICFILES_DIRS = [
        VITE_APP_DIR,
    ]
```

This is kind of a hack. You *do not* want to do this in production, hence why I added
the `if DEBUG:` clause (we'll also add an `else` clause later on, pointing to the compiled
files that `npm run build` generates).

Run both servers at the same time again and you should now see Svelte's default page
with the images rendered correctly and hot module reloading working, *all from Django's
development server*.


## Serving Svelte in production

There are a lot of things to do to make a Django project production ready.
**This guide will only cover the stuff related to Svelte.** Do not run your project
in production with *just these* changes.

The thing about Svelte is that it is actually *a compiler*. So, `npm run build` will
generate plain `.js` and `.css` files, that you can just import in your HTML, without 
needing to import any additional JavaScript libraries or run a JavaScript server. The 
challenge will be to tell Django where it can locate these files in order to serve them.

### 1. (Optional) Add Whitenoise to your Django project

Whitenoise is a package that allows your Python web apps to serve static files directly.
I find it comfortable because that means I don't have to deal with setting up Nginx in
my production environment (at least not for serving static files).

Install it with 

```console
pip install whitenoise
```


or

```console
poetry add whitenoise
```

Then, in your `project/settings.py` file add the following lines:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <-- new
    (...),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"  # <-- new
```

### 2. Configure Vite to generate a `manifest.json` file on build

In `frontend/vite.config.js` add the following line:

```javascript
// https://vitejs.dev/config/
export default defineConfig({
  build: { manifest: true },  // <-- new
  base: "/static/",
  plugins: [svelte()]
})
```

If you now open a terminal and run

```console
cd frontend
npm run build
```

You'll see that Vite generated a `dist/` folder (where your compiled files live). 
Notice that the files under `dist/assets/` contain hashes in their filenames (e.g.
`index.856f6096.js`).

Notice that there is also a file called `manifest.json`, that contains something 
like the following:

```json
{
  "src/assets/svelte.svg": {
    "file": "assets/svelte.a39f39b7.svg",
    "src": "src/assets/svelte.svg"
  },
  "src/assets/vite.svg": {
    "file": "assets/vite.4a748afd.svg",
    "src": "src/assets/vite.svg"
  },
  "index.html": {
    "file": "assets/index.856f6096.js",
    "src": "index.html",
    "isEntry": true,
    "css": [
      "assets/index.3635012e.css"
    ],
    "assets": [
      "assets/svelte.a39f39b7.svg",
      "assets/vite.4a748afd.svg"
    ]
  },
  "index.css": {
    "file": "assets/index.3635012e.css",
    "src": "index.css"
  }
}
```

As you can see, the manifest contains the dependencies of `index.html`, their locations 
and filenames. We'll use this to tell Django where to look for the files to
serve.


### 3. Changing Django's settings (again)

Change the following parts of the settings:

```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')  # <-- new

VITE_APP_DIR = BASE_DIR.joinpath("frontend")
if DEBUG:
    STATICFILES_DIRS = [
        VITE_APP_DIR,
    ]
else:  # <-- new
    # In production, all compiled files live in the dist/ folder
    STATICFILES_DIRS = [
        VITE_APP_DIR.joinpath("dist"),
    ]

# Needed for the 'debug' template tag to be available inside templates
# We'll use this in the next section, but might as well change it now
INTERNAL_IPS = ['127.0.0.1']  # <-- new
```

We're just telling Django to collect static files into `staticfiles/` and to
look for static files in the `frontend/dist` folder (which is where Vite compiles).


### 4. Modify the base template

Edit your `spa/templates/frontend/base.html` file in the follwing way:

```html
{% load render_svelte %}

<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Django + Svelte Integration</title>

  {% if debug %}
    <script type="module" src="http://localhost:3000/@vite/client"></script>
  {% endif %}
</head>

<body>

  <div id="app"></div>

  {% if debug %}
    <script type="module" src="http://localhost:5173/src/main.js"></script>
  {% else %}
    {% render_svelte %}
  {% endif %}

</body>

</html>
```

There are two changes. Firstly, in production, we do not need to call the Vite server.
Hence, the scripts pointing to `http://localhost:3000/@vite/client` and `http://localhost:5173`
are now inside `{% if debug %}` tags.

As said before, all we need to do is load to the appropriate `.js` and `.css` files.
As I showed, their locations are specified in the manifest, so we need to write a script
to read the manifest and insert the correct tags in the HTML. This is what the 
`{% render_svelte %}` tag does. We'll define it in the next section.


### 5. Creating a template tag to read the manifest

Inside your `spa` app create a `templatetags/` subdirectory, and a `render_svelte.py` 
inside it. It should have the following contents.

```python
import json
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


def load_json_from_dist(json_filename='manifest.json'):
    manifest_file_path = Path(str(settings.VITE_APP_DIR), 'dist', json_filename)
    if not manifest_file_path.exists():
        raise FileNotFoundError(
            f"Vite manifest file not found on path: {str(manifest_file_path)}"
        )
    else:
        with open(manifest_file_path, 'r') as manifest_file:
            try:
                manifest = json.load(manifest_file)
            except Exception:
                raise Exception(
                    f"Vite manifest file invalid. Maybe your {str(manifest_file_path)} file is empty?"
                )
            else:
                return manifest


@register.simple_tag
def render_svelte():
    """
    Template tag to render a vite bundle.
    Supposed to only be used in production.
    For development, see other files.
    """

    manifest = load_json_from_dist()

    # I'm not sure what this does, but I'll leave it just in case
    # Modified from https://gist.github.com/lucianoratamero/7fc9737d24229ea9219f0987272896a2
    imports_files = ""
    if "imports" in manifest["index.html"]:
        imports_files = "".join(
            [
                f'<script type="module" src="/static/{manifest[file]["file"]}"></script>'
                for file in manifest["index.html"]["imports"]
            ]
        )

    return mark_safe(
        f"""<link rel="stylesheet" type="text/css" href="/static/{manifest['index.html']['css'][0]}" />
        <script type="module" src="/static/{manifest['index.html']['file']}"></script>
        {imports_files}"""
    )
```

This basically defines two functions. The first merely opens the manifest file and
parses its contents (as a Python `dict`).

The important part of the second function is the return. It adds two
lines to the HTML wherever the `{% render_svelte %}` template tag is used.

The first is to a file located in `f"/static/{manifest['index.html']['css'][0]}"`. If
you look at the contents of the manifest file above, you'll see that this points to the
generated css file. The second line, similarly, points to the `index.[hash].js` file. 


### 6. (Optional) Serve with `gunicorn`

Install `gunicorn`:

```console
pip install gunicorn
```

or

```console
poetry add gunicorn
```

Build your Svelte project and collect static files from Django:

```console
cd frontend
npm run build
cd ..
python manage.py collectstatic
```

In your `settings.py`, set `DEBUG` to `False` and add the localhost to the `ALLOWED_HOSTS`:

```python
DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
```
(Note: you should probably do this with environment variables).

Run the following in your terminal:

```console
gunicorn project.wsgi
```

If you open a browser and navigate to `http://localhost:8000/` you should now see
your site.

## Acknowledgements

**Author:** [Ariel Jonathan Roffé](https://arielroffe.quest/)

**This guide was heavily inspired by:**

https://dev.to/besil/my-django-svelte-setup-for-fullstack-development-3an8

https://gist.github.com/lucianoratamero/7fc9737d24229ea9219f0987272896a2


