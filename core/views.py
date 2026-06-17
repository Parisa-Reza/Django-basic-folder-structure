from django.shortcuts import render
from core.forms import ProductSearchForm

"""
Views for the core app.
"""


def home(request):
    """
    Render the home template.
    """
    return render(request, 'home.html', {'search_form': ProductSearchForm()})
