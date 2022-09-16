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
