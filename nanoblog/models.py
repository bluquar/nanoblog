from django.db import models
from django import forms

from django.contrib.auth.models import User

class BlogPost(models.Model):
    text = models.CharField(max_length=160)
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.text

class Blogger(models.Model):
	""" Additional data linked to a User. Has a one-to-one relationship with a User. """
	user = models.OneToOneField(User)
	following = models.ManyToManyField(User, related_name='followers')
	bio = models.CharField(max_length=430, null=True)
	age = models.PositiveIntegerField(null=True)
	profile_picture_url = models.CharField(null=True, max_length=256)

class Comment(models.Model):
	text = models.CharField(max_length=160)
	user = models.ForeignKey(User)
	post = models.ForeignKey(BlogPost)
	datetime = models.DateTimeField(auto_now_add=True)
	