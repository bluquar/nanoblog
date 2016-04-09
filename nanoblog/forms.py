from django import forms
from django.core.exceptions   import ObjectDoesNotExist

from django.contrib.auth.models import User
from django.core.validators import validate_email, RegexValidator
from models import BlogPost, Blogger, Comment

MAX_UPLOAD_SIZE = 2500000

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length = 40,
                                 validators = [validate_email])
    username   = forms.CharField(max_length = 20)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirm that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    def clean_username(self):
        # Confirms that the username is not already present in the User database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email):
            raise forms.ValidationError("An account with that email already exists")
        return email

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'materialize-textarea', 
                'placeholder': "What's on your mind?", 
                'rows': 4}
            ),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', 'post')
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'materialize-textarea', 
                'placeholder': "Leave a comment...", 
                'rows': 1}
            ),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Blogger
        exclude = ('user', 'following', 'profile_picture_url')
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Who are you?',
                'class': 'materialize-textarea'}),
        }
    profile_picture = forms.FileField(required=False)

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture:
            return None
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture
