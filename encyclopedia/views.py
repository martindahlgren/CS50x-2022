from django.shortcuts import render
from django.http import Http404
import markdown2

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "header": "All Pages"
    })

def wikipage(request, title):
    content_md = util.get_entry(title)
    if(content_md is not None):
        content = markdown2.markdown(content_md)
        return render(request, "encyclopedia/entry.html", {
            "entry_name": title,
            "entry_content": content
        })
    else:
        return render(request, "encyclopedia/missing.html", {
            "entry_name": title,
        })

def search(request):
    search_term = request.GET.get('q', '')
    entries = util.list_entries()
    if search_term.lower() in (e.lower() for e in entries):
        return wikipage(request, search_term)
    else:
        matching_entries = filter(lambda e: search_term.lower() in e.lower(), entries)
        return render(request, "encyclopedia/index.html", {
            "entries": matching_entries,
            "header": "Search Results"

        })
