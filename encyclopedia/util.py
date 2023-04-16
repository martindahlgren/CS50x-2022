import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import markdown2
import bleach

def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content.encode('utf-8')))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def page_title_ok(title):
    """
    Check that the title can correspond to a valid file name
    """
    invalid_chars = re.search(r'[<>:"/\\|?*]', title)
    return not invalid_chars


def santitize_html(unclean_html):
    # Define a list of allowed HTML tags and attributes
    allowed_tags = ['ul', 'ol', 'li', 'p', 'pre', 'code',
                    'blockquote', 'h1', 'h2', 'h3', 'h4',
                    'h5', 'h6', 'hr', 'br', 'strong', 'em',
                    'a', 'img'
                    ]
    allowed_attrs = bleach.sanitizer.ALLOWED_ATTRIBUTES.copy()
    allowed_attrs.update({
        'ol': ['start'],
        'img': ['alt', 'title', 'width', 'height'] # Allow alt-text but not the actual image

    })

    return bleach.clean(unclean_html, tags=allowed_tags, attributes=allowed_attrs)


def markdown2html_safe(md):
    """
    Convert markdown to html, and sanitize the result
    """
    unclean_html = markdown2.markdown(md)
    clean_html = santitize_html(unclean_html)
    return clean_html
