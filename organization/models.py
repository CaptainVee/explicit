from django.db import models
from django.contrib.auth.models import User
from account.models import Profile
from django.urls import reverse
import datetime
from django.utils import timezone

# Create your models here.


class Organization(models.Model):
	CHOICES = (
		('profit', 'profit'),
		('non-profit', 'non-profit'),
		)

	name = models.CharField(max_length=150)
	description = models.TextField()
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(default=timezone.now)
	head = models.ForeignKey(User, on_delete= models.CASCADE)
	profile_pic = models.ImageField(default='come.jpg', null=True, blank=True)
	contributors = models.ManyToManyField(User, related_name='contributors', blank=True)
	address = models.CharField(max_length=150, blank=True, null= True)
	account_number  = models.CharField(max_length=15, blank=True, null=True)
	account_name    = models.CharField(max_length=100, blank=True, null=True)
	bank_name 		= models.CharField(max_length=100, blank=True, null=True)
	auth_id = models.CharField(max_length=100, blank=True, null=True)
	type = models.CharField(max_length=20, choices=CHOICES)


	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('dashboard', kwargs={'pk' : self.pk })

	def is_contributor(self):
		return self.contributors.all()


	# @property
	# def announcements(self):
	# 	return self.announcement_set.all().order_by('-updated_at')

