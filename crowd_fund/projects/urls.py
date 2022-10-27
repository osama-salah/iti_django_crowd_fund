from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from projects.projects.views import ProjectViewSet, DonationViewSet, donation_create, project_create, ProjectDelete, \
    project_update, comment_create, comment_report, rate_project, project_report

app_name = 'projects'

urlpatterns = [
    path('<pk>', ProjectViewSet.as_view({'get': 'retrieve'}), name='project'),
    path('report/<project_id>', project_report, name='project_report'),
    path('delete/<pk>', ProjectDelete.as_view(), name='project_delete'),
    path('deleted_msg/', TemplateView.as_view(template_name='projects/project_deleted_msg.html'),
         name='project_deleted_msg'),
    path('update/<pk>', project_update, name='project_update'),
    path('donation_create/<proj_id>/<proj_title>', donation_create, name='donation_create'),
    path('donate/', DonationViewSet.as_view({'post': 'create'}), name='donate'),
    path('project_create/', project_create, name='project_create'),
    path('comment/', comment_create, name='comment_create'),
    path('comment/report/<comment_id>', comment_report, name='comment_report'),
    path('reply/', comment_create, name='reply_create'),
    path('rate/', rate_project, name='rate_project'),
    path('', ProjectViewSet.as_view({'get': 'list'}), name='projects'),
]

router = SimpleRouter()
router.register('', ProjectViewSet, basename="projects")
urlpatterns.extend(router.urls)
