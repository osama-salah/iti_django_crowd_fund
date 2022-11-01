import os
from itertools import count, chain
from statistics import mean, StatisticsError

from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DeleteView
from rest_framework import viewsets

from crowd_fund_app.models import CustomUser
from images.models import ProjectImage
from projects.models import Project, ProjectCategory, ProjectTag, Donation, ProjectComment, ProjectRate, CommentReply
from projects.serializers import ProjectSerializer, DonationSerializer


def reply_create(request):
    user = request.user
    comment_id = request.POST['comment_id']
    comment = ProjectComment.objects.get(pk=comment_id)
    CommentReply.objects.create(reply=request.POST['reply'], comment_id=comment, user_id=user)
    project_id = request.POST.get('project_id')
    return redirect(reverse('projects:project', args=(project_id, )))


class ReportAdapter(DefaultAccountAdapter):
    def get_email_confirmation_redirect_url(self, request):
        return HttpResponse('Your report was sent to site admins')


def comment_report(request, comment_id, reply_id=None):
    user = request.user
    if user.id is None:
        return HttpResponse("You must be logged in", status=400)

    comment = ProjectComment.objects.get(id=comment_id)
    reply = CommentReply.objects.get(id=reply_id) if reply_id else None

    project = Project.objects.get(id=comment.project_id.id)
    current_site = get_current_site(request)
    staff = CustomUser.objects.filter(is_staff=True)
    for admin_user in staff:
        email = admin_user.email
        path = reverse('projects:project', args=(comment.project_id.id,))
        url = build_absolute_uri(request, path)
        context = {
            'current_site': current_site,
            'username': user.username,
            'project_title': project.title,
            'comment_id': comment_id,
            'comment': comment,
            'reply_id': reply_id,
            'reply': reply,
            'url': url,
            'request': request,
        }
        adapter = ReportAdapter(request)
        template_prefix = 'comments/reply_report' if reply_id else 'comments/comment_report'
        adapter.send_mail(template_prefix, email, context)

    return render(request, 'comments/comment_reported.html',
                  context={'url': reverse('projects:project', args=(project.id,))})


def project_report(request, project_id):
    user = request.user
    if user.id is None:
        return HttpResponse("You must be logged in", status=400)

    project = Project.objects.get(id=project_id)
    current_site = get_current_site(request)
    staff = CustomUser.objects.filter(is_staff=True)
    for admin_user in staff:
        email = admin_user.email
        path = reverse('projects:project', args=(project_id,))
        url = build_absolute_uri(request, path)
        context = {
            'current_site': current_site,
            'username': user.username,
            'project_title': project.title,
            'url': url,
            'request': request,
        }
        adapter = ReportAdapter(request)
        adapter.send_mail('projects/project_report', email, context)

    return render(request, 'projects/project_reported.html',
                  context={'url': reverse('projects:project', args=(project.id,))})


def rate_project(request):
    project_id = request.POST['project_id']
    if int(request.POST['rate']) < 0 or int(request.POST['rate']) > 5:
        return redirect(reverse('projects:project', args=(project_id,)))
    user_id = request.user
    if user_id == Project.objects.get(id=project_id).id:
        print('own')
    try:
        project_rate = ProjectRate.objects.get(Q(user_id__id=request.user.id) & Q(project_id__id=project_id))
    except:
        project_rate = None

    if project_rate:
        project_rate.rate = request.POST['rate']
        project_rate.save()
    else:
        project = Project.objects.get(pk=project_id)
        ProjectRate.objects.create(rate=request.POST['rate'], project_id=project, user_id=user_id)
    user_rate = request.POST['rate']
    return redirect(reverse('projects:project', args=(project_id, )))


def comment_create(request):
    user_id = request.user
    project_id = request.POST['project_id']
    project = Project.objects.get(pk=project_id)
    ProjectComment.objects.create(comment=request.POST['comment'], project_id=project, user_id=user_id)
    return redirect(reverse('projects:project', args=(project_id, )))


class ProjectDelete(DeleteView):
    model = Project
    success_url = '/projects/deleted_msg/'

    def form_valid(self, form):
        for image in ProjectImage.objects.filter(project_id__id=self.object.id):
            image.delete()
        return super().form_valid(self.get_form())


def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        category_id = request.POST.get('category', None)
        tags = []
        if request.POST.get('tags'):
            for tag in request.POST.getlist('tags'):
                tags.append(ProjectTag.objects.get(id=tag))
        project.title = request.POST.get('title')
        project.details = request.POST.get('details')
        project.category = ProjectCategory.objects.get(id=category_id)
        project.total_target = request.POST.get('total_target')
        project.start_date = request.POST.get('start_date')
        project.end_date = request.POST.get('end_date')
        project.user_id = request.user
        project.tags.set(tags)
        images = request.FILES.getlist('images')
        if images:
            project.images.set([])
            for image in project.images.all():
                if image not in images:
                    image.delete()
            for image in images:
                ProjectImage.objects.create(image=image, project_id=project)
        project.save()
        return render(request, template_name="projects/project_updated_msg.html", context={'project_id': project.id})
    else:
        project_tag_ids = [tag_id['id'] for tag_id in project.tags.all().values('id')]
        str(project.start_date)
        return render(request, 'projects/project_update.html',
                      context={'categories': ProjectCategory.objects.all(),
                               'tags': ProjectTag.objects.all(),
                               'project': project,
                               'project_tag_ids': project_tag_ids,
                               'start_date': str(project.start_date),
                               'end_date': str(project.end_date)})


def project_create(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        tags = []
        if request.POST.get('tags'):
            for tag in request.POST.getlist('tags'):
                tags.append(ProjectTag.objects.get(id=tag))
        project = Project.objects.create(
            title=request.POST.get('title'),
            details=request.POST.get('details'),
            category=ProjectCategory.objects.get(id=category),
            total_target=request.POST.get('total_target'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            user_id=request.user,
        )
        project.tags.set(tags)
        images = request.FILES.getlist('images')
        for image in images:
            ProjectImage.objects.create(image=image, project_id=project)
        return render(request, template_name="projects/project_created_msg.html")
    else:
        return render(request, 'projects/project_create.html',
                      context={'categories': ProjectCategory.objects.all(),
                               'tags': ProjectTag.objects.all()})


def get_project_rates(project):
    rates = [r[0] for r in project.rates.values_list('rate')]
    return rates if rates else [0]


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    # permission_classes = [permissions.IsAuthenticated, OwnBookPermission]

    def get_queryset(self):
        # return Project.objects.filter(user_id__id=self.request.user.id)
        # print(self.request.query_params['category'])
        category = self.request.query_params.get('category', None)
        if category and category != "-1":
            response = Project.objects.filter(category=category)
        else:
            response = Project.objects.all()
        search_string = self.request.query_params.get('search_string', None)
        if search_string:
            search_by = self.request.query_params.get('search_by', None)
            if search_by == 'title':
                response = response.filter(title__icontains=search_string)
            elif search_by == 'tag':
                tags = ProjectTag.objects.filter(name__icontains=search_string)
                response = list(response.filter(tags__in=tags))
            else:
                tags = list(ProjectTag.objects.filter(name__icontains=search_string))
                response = set(chain(response.filter(title__icontains=search_string), response.filter(tags__in=tags)))
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request.data, args, kwargs)

        for project_data in response.data:
            rates = ProjectRate.objects.filter(id__in=project_data['rates']).values('rate').values('rate')
            rates = map(lambda x: x['rate'], rates)
            try:
                project_data['rate'] = mean(rates)
            except StatisticsError:
                project_data['rate'] = 0
            project_data['category'] = ProjectCategory.objects.get(pk=project_data['category'])
            project_data['tags'] = ProjectTag.objects.filter(id__in=project_data['tags']).values('name')
            project_data['icon_image'] = ProjectImage.objects.filter(project_id__id=project_data['id'])[0]
            project_data['user'] = CustomUser.objects.get(id=project_data['user_id'])
            project_data['comments'] = ProjectComment.objects.filter(project_id__id=project_data['id'])

        categories = ProjectCategory.objects.all()
        category_displayed = int(self.request.query_params.get('category', '-1'))

        return render(request, 'projects/project_list.html', {
            'response': sorted(response.data, key=lambda e: e['id']),
            'categories': categories,
            'category_displayed': category_displayed,
        })

    def retrieve(self, request, pk=None):
        response = super().retrieve(request, pk)
        rates = ProjectRate.objects.filter(id__in=response.data['rates']).values('rate').values('rate')
        rates = map(lambda x: x['rate'], rates)
        try:
            response.data['rate'] = mean(rates)
        except StatisticsError:
            response.data['rate'] = 0

        project_tags = ProjectTag.objects.filter(id__in=response.data['tags'])

        projects = Project.objects.all()
        similar_projects = []
        for p in projects:
            if p.id != response.data['id']:
                similar_projects.append({'project': p, 'score': len(list(t for t in p.tags.values('id') if t['id'] in list(project_tags.values_list('id', flat=True))))})

        similar_projects = sorted(similar_projects, key=lambda x: x['score'], reverse=True)
        response.data['similar'] = similar_projects[:min(5, len(similar_projects))]

        response.data['rate_items'] = ProjectRate.get_rate_titles()
        response.data['category'] = ProjectCategory.objects.get(pk=response.data['category'])
        response.data['images'] = [os.path.basename(image) for image in response.data['images']]
        response.data['tags'] = project_tags.values('name')
        response.data['user'] = CustomUser.objects.get(id=response.data['user_id'])
        response.data['comments'] = ProjectComment.objects.filter(project_id__id=pk)
        try:
            user_rate = ProjectRate.objects.get(Q(project_id__id=pk) & Q(user_id__id=request.user.id)).rate
        except:
            user_rate = -1
        response.data['user_rate'] = user_rate
        donations = Donation.objects.filter(project_id=response.data['id'])
        total_donations = sum(map(lambda d: d.amount, donations))
        response.data['percent_target'] = round(100.0 * total_donations / response.data['total_target'], 2)
        return render(request, 'projects/project_details.html', response.data)


def donation_create(request, proj_id, proj_title):
    return render(request, 'projects/donation_create.html',
                  context={'user': request.user, 'proj_id': proj_id, 'proj_title': proj_title})


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer

    # permission_classes = [permissions.IsAuthenticated, OwnBookPermission]

    def get_queryset(self):
        return Donation.objects.all()

    def list(self, request):
        response = super().list(request.data)

        for donation_data in response.data:
            donation_data['project_id'] = Project.objects.get(pk=donation_data['project_id'])
            donation_data['user_id'] = CustomUser.objects.get(pk=donation_data['user_id'])

        return render(request, 'projects/donation_list.html',
                      {'response': sorted(response.data, key=lambda e: e['id'])})

    def retrieve(self, request, pk=None):
        response = super().retrieve(request, pk)
        response.data['project_id'] = Project.objects.get(pk=response.data['project_id'])
        response.data['user_id'] = CustomUser.objects.get(pk=response.data['user_id'])
        return render(request, 'projects/donation_details.html', response.data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, args, kwargs)
        return render(request, 'projects/donation_created_msg.html', response.data)
