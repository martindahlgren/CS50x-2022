from django.shortcuts import render, redirect
from django.http import Http404

from django import forms

from . import util
import random

class EditEntryForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "header": "All Pages"
    })

def wikipage(request, title):
    print(title)
    print("\r\n")
    content_md = util.get_entry(title)
    if(content_md is not None):
        content = util.markdown2html_safe(content_md)
        return render(request, "encyclopedia/entry.html", {
            "entry_name": title,
            "entry_content": content
        })
    else:
        return render(request, "encyclopedia/missing.html", {
            "entry_name": title,
        })

def wikiedit(request, title):
    if request.method == "POST":
        if not util.page_title_ok(title):
            raise Exception("Why would an existing page have a bad title??")
        else:
            content = request.POST.get("content", "")
            util.save_entry(title, content)
            return redirect("wikipage", title=title)
    else:
        content_md = util.get_entry(title)
        if(content_md is not None):
            return render(request, "encyclopedia/edit.html", {
                "entry_name": title,
                "entry_content": content_md
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


def random_page(request):
    random_page = random.choice(util.list_entries())
    return redirect("wikipage", title=random_page)

def new(request):
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = EditEntryForm(request.POST)
        # Check if form data is valid (server-side)
        if form.is_valid():
            created_page_title = form.cleaned_data["title"]
            if not util.page_title_ok(created_page_title):
                return render(request, "encyclopedia/new.html", {
                        "error_text": "Illegal characters in title.",
                        "form": EditEntryForm(form.cleaned_data)
                    })
            elif util.get_entry(created_page_title):
                # If error, allow trying again
                return render(request, "encyclopedia/new.html", {
                            "error_text": "Page already exists.",
                            "form": EditEntryForm(form.cleaned_data)
                        })
            else:
                content = form.cleaned_data["content"]
                util.save_entry(created_page_title, content)
                return redirect("wikipage", title=created_page_title)
        else:
            return render(request, "encyclopedia/new.html", {
                            "error_text": "Data validation fail.",
                            "form": EditEntryForm()
            })
    else:
        return render(request, "encyclopedia/new.html", {
                    "form": EditEntryForm()
        })
