from django.views.generic import RedirectView
from django.urls import reverse

def page_search(request):
    query = request.GET.get('q')
    url = reverse('page_detail', args=[query])
    return RedirectView(url)