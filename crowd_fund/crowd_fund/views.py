from statistics import mean

from django.shortcuts import render

from projects.models import Project, FeaturedProject, ProjectCategory
from projects.projects.views import get_project_rates


def render_home(request):
    projects = list(Project.objects.all())
    top_rated = sorted(projects, key=lambda p: mean(get_project_rates(p)), reverse=True)
    latest = sorted(projects, key=lambda p: p.added_at, reverse=True)
    featured = FeaturedProject.objects.all()
    categories = ProjectCategory.objects.all()
    context = {
        'top_rated': top_rated[:5],
        'latest': latest[:5],
        'featured': featured[:5],
        'categories': categories,
    }
    # return render(request, 'projects/project_carousel.html', context)
    return render(request, 'home.html', context)
