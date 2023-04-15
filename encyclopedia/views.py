from django.shortcuts import render, redirect
from django.http import Http404
import markdown2
from django import forms

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea())

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

def new(request):
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = NewEntryForm(request.POST)
        # Check if form data is valid (server-side)
        if form.is_valid():
            created_page_title = form.cleaned_data["title"]
            if not util.page_title_ok(created_page_title):
                return render(request, "encyclopedia/new.html", {
                        "error_text": "Illegal characters in title.",
                        "form": NewEntryForm(form.cleaned_data)
                    })
            elif util.get_entry(created_page_title):
                # If error, allow trying again
                return render(request, "encyclopedia/new.html", {
                            "error_text": "Page already exists.",
                            "form": NewEntryForm(form.cleaned_data)
                        })
            else:
                content = form.cleaned_data["content"]
                print("\n\n")
                print(content)
                print("\n\n")
                util.save_entry(created_page_title, content)
                return redirect(f"wiki/{created_page_title}")
        else:
            return render(request, "encyclopedia/new.html", {
                            "error_text": "Data validation fail.",
                            "form": NewEntryForm()
            })

    return render(request, "encyclopedia/new.html", {
                "form": NewEntryForm()
    })
