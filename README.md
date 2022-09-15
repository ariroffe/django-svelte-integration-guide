# Django + Svelte Integration Guide

This guide will walk you through creating a Django and Svelte project (without SvelteKit), serving the Svelte files directly from Django.

It is recommended that you follow the instructions along instead of cloning this repo.

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

## Acknowledgements

