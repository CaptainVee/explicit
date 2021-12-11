from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Organization
# from .forms import ContributorForm
from django.db.models import Q
import requests
from django.conf import settings
import json
from pymono import Mono




def welcome(request):
	'''this function is to redirect from login page to workspace list passing the username 
	of the logged in user as a parameter'''
	username = request.user.username
	if username == '':
		return render(request, 'organization/landing_page.html', {'title': 'Ace'})
	else:
		return redirect('user-organization', username)


class OrganizationCreateView(LoginRequiredMixin, CreateView):
	model = Organization
	fields = ['name', 'description', 'profile_pic', 'address']

	def form_valid(self, form):
		print(self.kwargs)
		form.instance.head = self.request.user
		return super().form_valid(form)

class UserOrganizationListView(ListView):
	model = Organization
	template_name = 'organization/organization_list.html'
	context_object_name = 'organizations'
	paginate_by = 5

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Organization.objects.filter(
			Q(head=user) |
			Q(contributors=user)
			)
		# return Organization.objects.filter(head=user).order_by('-updated_at')

class OrganizationDetailView(DetailView):
	model = Organization

class OrganizationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Organization
	fields = ['name', 'description', 'image']

	def form_valid(self, form):
		form.instance.head = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		user = self.request.user
		if user == post.head:
			return True
		return False

class OrganizationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Organization
	success_url = '/'

	def test_func(self):
		post = self.get_object()
		user = self.request.user
		if user == post.head:
			return True
		return False

class AddContributor(View):
	def get(self, request, pk, *args, **kwargs):
		form = ContributorForm()
		context = {
		'form':form,
		}
		return render(self.request, "organization/contributor_form.html", context)

	def post(self, request, pk, *args, **kwargs):
		organization =  get_object_or_404(Organization, pk=self.kwargs.get('pk'))
		form = ContributorForm(self.request.POST or None)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			contributor = get_object_or_404(User, email= email)
			organization.contributors.add(contributor)
			organization.save()
			return redirect("organization-details", pk)

def ContributorsListView(request, pk):
	organization = Organization.objects.get(pk=pk)
	contributors = organization.contributors.all()
	context = {
		'head': organization.head,
		'contributors':contributors,
		}
	return render(request, 'organization/contributors_list.html', context )


def Connect(request):
	return render(request, 'organization/connect.html')

def collect(request, code):
	code = code.strip()
	mono= Mono(code)
	(data,status) = mono.Auth()
	mono.SetUserId(data.get("id"))
	pp = mono.getAccount()

	context = {
	'ff':pp
	}
	return (request, 'organization/collect.html', context)


def About(request):
	return render(request, 'organization/about.html', {'title': 'About'})
