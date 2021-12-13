from django.contrib import admin
from django.urls import path, include

from .views import (
	welcome, 
	OrganizationCreateView, 
	UserOrganizationListView, 
	OrganizationDetailView,
	OrganizationUpdateView,
	OrganizationDeleteView,
	AddContributor,
	ContributorsListView,
	About,
	# Connect,
	collect,
	# auth,
	dashboard
	)

urlpatterns = [
    path('', welcome, name='landing_page'),
    path('organization/new/', OrganizationCreateView.as_view(), name='create-organization'),
    path('user/<str:username>/organizations', UserOrganizationListView.as_view(), name='user-organization'),
    path('organization/<int:pk>/', OrganizationDetailView.as_view(), name='organization-details'),
    path('organization/<int:pk>/update', OrganizationUpdateView.as_view(), name='organization-update'),
    path('organization/<int:pk>/delete', OrganizationDeleteView.as_view(), name='organization-delete'),
    path('organization/<int:pk>/add-contributor/', AddContributor.as_view(), name='add-contributor'),
	path('organization/<int:pk>/contributors/', ContributorsListView, name='contributors'),
    path('about/', About, name='about'),
    # path('connect/', Connect, name='connect'),
    path('dashboard/<int:pk>/', dashboard, name='dashboard'),
    path('collect/<int:pk>/', collect, name='collect'),
    # path('auth/<int:pk>/<str:auth_id>/', auth, name='auth')
]
