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
import pandas as pd
from django.contrib import messages




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


# def Connect(request, pk):
# 	return render(request, 'organization/connect.html')


def collect(request, pk):
	code = list(request.GET.keys())
	code = str(code[0])
	url = "https://api.withmono.com/account/auth"
	payload = {"code": code }
	headers = {
	"Accept": "application/json",
	"mono-sec-key": 'test_sk_UJWRFMwbgJ8k2FJ8KMFw',
	"Content-Type": "application/json"
	}
	response = requests.request("POST", url, json=payload, headers=headers)
	auth_id = response.text
	organization = Organization.objects.get(pk=pk)
	organization.auth_id = auth_id
	organization.save()
	# context = { "id" : response.text }
	return redirect('dashboard', pk)

# def auth(request, pk, auth_id):
# 	organization = Organization.objects.get(pk=pk)
# 	if organization.auth_id == None:
# 		collect(request, pk)

	
	
# 	context = {
# 	"id": "successful"
# 	}
# 	return render (request, 'organization/collect.html', context)

def account_identity(request, pk, auth_id):
	url = f"https://api.withmono.com/accounts/{auth_id}/identity"
	headers = {
	"Accept": "application/json",
	"mono-sec-key": "test_sk_UJWRFMwbgJ8k2FJ8KMFw"
	}
	response = requests.request("GET", url, headers=headers)
	return response.text

def account_income(request, pk, auth_id):
	url = f"https://api.withmono.com/accounts/{auth_id}/income"
	headers = {
	"Accept": "application/json",
	"mono-sec-key": "sdssdsdsd",
	"Content-Type": "application/json"
	}
	response = requests.request("GET", url, headers=headers)
	return response.text

def account_information(request, pk, auth_id):
	auth_id = auth_id[0]
	url = f"https://api.withmono.com/accounts/{auth_id}"
	headers = {
	"Accept": "application/json",
	"mono-sec-key": "test_sk_UJWRFMwbgJ8k2FJ8KMFw"
	}
	response = requests.request("GET", url, headers=headers)
	return response.text

def total_amount_spent(data):
	data = pd.DataFrame(data)
	data['date'] = data['date'].str.slice(stop=10)
	data['date'] = pd.to_datetime(data['date'])
	date_grouped_data = data.groupby(pd.Grouper(key='date', freq='M')).sum()
	date_grouped_data.index = date_grouped_data.index.strftime('%B')
	date_grouped_data = date_grouped_data.drop(['balance'], axis=1)
	context = date_grouped_data.to_dict('split')

	return context

def total_credit_debit(data):
	data = pd.DataFrame(data)
	data['date'] = data['date'].str.slice(stop=10)
	data['date'] = pd.to_datetime(data['date'])

	group_date_1 = data.groupby(pd.Grouper(key='type')).sum()
	group_date_1 = group_date_1.drop(['balance'], axis=1 )
	context = group_date_1.to_dict('split')

	return context

def debit_credit(data):
	data = pd.DataFrame(data)
	data['date'] = data['date'].str.slice(stop=10)
	data['date'] = pd.to_datetime(data['date'])

	new_data = data.set_index(['amount','type'])
	new_data = new_data.drop(['balance', '_id', 'narration'], axis=1 )
	dict_data = new_data.to_dict('split')
	index = dict_data['index']
	date = dict_data['data']
	debit = []
	credit = []
	new_date = []
	for i in date:
		new_date.append(i[0].to_pydatetime().strftime("%m-%d-%Y, %H:%M:%S"))

	for i in index:
		if i[1] == 'debit':
			debit.append(i[0])
		else:
			credit.append(i[0])
	context = {
		"date" : new_date,
		"credit": credit,
		"debit": debit
	}
	return context


def dashboard(request, pk):

	organization = Organization.objects.get(pk=pk)
	if organization.auth_id == None:
		messages.success(request, 'Please Connect an Account to the Organisation')
		return redirect('organization-details', pk)

	auth_id = organization.auth_id
	auth_id = json.loads(auth_id)['id']

	url = f"https://api.withmono.com/accounts/{auth_id}/"
	statement_url = f"https://api.withmono.com/accounts/{auth_id}/statement?period=last6months"
	account_info_url = f"https://api.withmono.com/accounts/{auth_id}"

	headers = {
	"Accept": "application/json",
	"mono-sec-key": "test_sk_UJWRFMwbgJ8k2FJ8KMFw"
	}


	response = requests.request("GET", url, headers=headers)
	statement_response = requests.request("GET", statement_url, headers=headers)
	account_info = requests.request("GET", account_info_url, headers=headers)

	res = json.loads(response.text)
	account_info_res = json.loads(account_info.text).get('account')

	statement_res = json.loads(statement_response.text).get('data')
	monthly_total = total_amount_spent(statement_res)
	debit_credit_res = debit_credit(statement_res)


	context = { "account" : res,
				"statement" : statement_res,
				"monthly_total":monthly_total,
				"account_info" : account_info_res,
				"last_transaction" : statement_res[0],
				"debit_credit" :debit_credit_res,
				}


	return render(request, 'organization/collect.html', context )








def About(request):
	return render(request, 'organization/about.html', {'title': 'About'})
