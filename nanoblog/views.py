import json

from django.shortcuts         import render, redirect, get_object_or_404
from django.template.loader   import render_to_string
from django.core.urlresolvers import reverse
from django.core.exceptions   import ObjectDoesNotExist
from django.http              import HttpResponse, Http404

# User authentication
from django.contrib.auth.models     import User
from django.contrib.auth            import login, authenticate
from django.contrib.auth.decorators import login_required

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

# Custom models and forms
from nanoblog.models import User, BlogPost, Blogger, Comment
from nanoblog.forms  import RegistrationForm, ProfileForm, BlogPostForm, CommentForm

# Amazon S3 file hosting
from nanoblog.s3 import s3_upload, s3_delete



def comments_for_posts(posts):
    """
    Given a sequence of BlogPost objects, get a list of dictionaries with the following components:
    - post: the original post
    - last_updated: a UTC string representing the time the post was made.
                    The most recent update on the whole stream can be found
                    by inspecting the last_updated field of the top post of the stream.
    - comments: A list of Comment objects on this post.
    """
    posts_and_comments = []
    for post in posts:
        group = {}
        group["post"] = post
        group["last_updated"] = str(post.datetime)
        group["comments"] = Comment.objects.filter(post=post).order_by('datetime')
        posts_and_comments.append(group)
    return posts_and_comments

def stream_html(request, template_name, blog_posts, context):
    """
    Check for GET["last_updated"]. If present, treat this as an incremental AJAX
    request and only return the HTML for new posts, which should be inserted at
    the top of the post list. If absent, treat this as a regular page GET and return
    the entire HTML page.

    This is used by global_stream, following, and user to render initial page loads
    and incremental updates.
    """
    if "last_updated" in request.GET:
        template_name = "nanoblog/blogposts.html"
        blog_posts = blog_posts.filter(datetime__gt=request.GET["last_updated"])

    context['posts_and_comments'] = comments_for_posts(blog_posts)
    return render(request, template_name, context)

@login_required
def global_stream(request, blog_post_form=None):
    """ View posts from all users.
    If kwarg blog_post_form is not None, it will be used instead of a blank
      BlogPostForm. This lets callers (`add`) set error fields for the form.
    """

    if blog_post_form is None:
        blog_post_form = BlogPostForm()

    # DB request for all blog posts in reverse chronological order.
    # If we were worried about scaling, we would set a limit here as well.
    blog_posts = BlogPost.objects.all().order_by('-datetime')

    context = {
        'blog_post_form': blog_post_form,
        'comment_form': CommentForm(),
    }
    return stream_html(request, 'nanoblog/global_stream.html', blog_posts, context)


@login_required
def following(request, blog_post_form=None):
    """ View all posts by users whom the logged in user follows.
    If kwarg blog_post_form is not None, it will be used instead of a blank
      BlogPostForm. This lets callers (`add`) set error fields for the form.
    """

    if blog_post_form is None:
        blog_post_form = BlogPostForm()

    # DB request for all posts, filtered by whether post's user (i.e., its author)
    # has a follower set (post.user.followers) that contains the logged in user.
    # To make sure this scales, we would need to (1) put a limit on the number of
    # results returned and (2) ensure there is an index on followers.
    blog_posts = BlogPost.objects.filter(user__followers__user=request.user).order_by('-datetime')

    context = {
        'blog_post_form': blog_post_form,
        'comment_form': CommentForm()
    }
    return stream_html(request, 'nanoblog/following_stream.html', blog_posts, context)


@login_required
def user(request, username=None, blog_post_form=None):
    """ View all posts by user with username `username`.
    If kwarg blog_post_form is not None, it will be used instead of a blank
      BlogPostForm. This lets callers (`add`) set error fields for the form.
    """

    if blog_post_form is None:
        blog_post_form = BlogPostForm()

    try:
        profile_user = User.objects.get(username=username)
    except ObjectDoesNotExist: # invalid username
        return redirect(reverse('home'))

    # DB request to get all posts from this user.
    blog_posts = BlogPost.objects.filter(user=profile_user).order_by('-datetime')

    context = {
        'profile_user': profile_user,
        'blog_post_form': blog_post_form,
        'comment_form': CommentForm()
    }

    if profile_user.username == request.user.username:
        # The logged in user is viewing their own page.
        return stream_html(request, 'nanoblog/own_user.html', blog_posts, context)
    else:
        # The logged in user is viewing another user's page.
        blogger = request.user.blogger
        following = blogger.following.filter(id=profile_user.id)
        # Determine whether profile_user is in the blogger's following set.
        context['following'] = bool(following)
        return stream_html(request, 'nanoblog/other_user.html', blog_posts, context)


@login_required
@transaction.atomic
def follow(request, username=None):
    """ Make the logged in user follow the user with username `username` """
    blogger = request.user.blogger
    try:
        profile_user = User.objects.get(username=username)
        blogger.following.add(profile_user)
        return redirect(reverse('user', kwargs={'username': username}))
    except ObjectDoesNotExist:
        # Trying to follow someone who doesn't exist
        return redirect(reverse('home'))


@login_required
@transaction.atomic
def unfollow(request, username=None):
    """ Make the logged in user unfollow the user with username `username` """
    blogger = request.user.blogger
    try:
        profile_user = User.objects.get(username=username)
        blogger.following.remove(profile_user)
        return redirect(reverse('user', kwargs={'username': username}))
    except ObjectDoesNotExist:
        # Trying to unfollow someone who doesn't exist
        return redirect(reverse('home'))


@login_required
@transaction.atomic
def add(request):
    """ Add a new blog post. The form validation is done by BlogPostForm.
    When done, dispatch to the calling stream view to render either a new,
    empty form, or the same form with error messages.
    """
    new_post = BlogPost(user=request.user)
    form = BlogPostForm(request.POST, instance=new_post)

    if form.is_valid():
        form.save()
        form = BlogPostForm()

    # Determine which view to re-render (with or without errors)
    redirect_name = request.POST.get('redirect', 'home')
    redirect_user = request.POST.get('redirect_user', None)
    if redirect_name == 'following':
        return following(request, blog_post_form=form)
    elif redirect_name == 'user' and redirect_user is not None:
        return user(request, username=redirect_user, blog_post_form=form)
    else:
        return global_stream(request, blog_post_form=form)

@login_required
@transaction.atomic
def add_comment(request):
    """ Add a new comment. Basic validation is done in this
    function: the fields are parsed out of the AJAX request's
    arrays and we make sure the fields are there. The rest of
    the validation is done by the CommentForm.

    If the comment is valid and successfully added to the database,
    its HTML representation is returned as a string in a JSON object
    to the client. Otherwise, the errors with the form are returned.
    """
    valid = True
    request_data = dict(request.POST)
    post_id = request_data.get('post', None)
    if ('post' in request_data) and ('text' in request_data):
        request_data['post'] = request_data['post'][0] # Ajax passes a singleton array
        request_data['text'] = request_data['text'][0]
    else:
        valid = False

    if valid:
        new_comment = Comment(user=request.user)
        form = CommentForm(request_data, instance=new_comment)
        valid = form.is_valid()
        
    if valid:
        form.save()
        comment_html = render_to_string("nanoblog/comment.html", {"comment": new_comment})
        response = {
            'success': True,
            'html': comment_html,
        }
    else:
        response = {
            'success': False,
            'errors': str(form.errors)
        }
    response_json = json.dumps(response)
    return HttpResponse(response_json, content_type='application/json')

@login_required
@transaction.atomic
def edit_profile(request):
    """ Either get the edit_profile page (GET request), or submit the ProfileForm
    (POST request) and redirect to the user's page.
    """
    context = {}
    blogger = request.user.blogger

    if request.method == 'GET':
        # Get the edit_profile page
        form = ProfileForm(instance=blogger)
        context['edit_profile_form'] = form
        return render(request, 'nanoblog/edit_profile.html', context)

    form = ProfileForm(request.POST, request.FILES, instance=blogger)
    if not form.is_valid():
        # Re-render the edit_profile page with error messages
        context['edit_profile_form'] = form
        return render(request, 'nanoblog/edit_profile.html', context)
    else:
        # Update the user's profile and redirect to their user stream.
        #url = s3_upload(create_form.cleaned_data['picture'], entry.id)
        #entry.picture_url = url
        #entry.save()
        #
        #
        profile_picture_url = s3_upload(form.cleaned_data['profile_picture'], blogger.id)
        blogger.profile_picture_url = profile_picture_url
        form.save()
        blogger.save()

        #profile_picture = form.cleaned_data['profile_picture']
        #if profile_picture and len(request.FILES):
        #    blogger.content_type = form.cleaned_data['profile_picture'].content_type
        #form.save()
        return redirect(reverse('user', kwargs={'username': request.user.username}))

@transaction.atomic
def register(request):
    """ Either get the register page or handle a RegistrationForm POST request. """
    context = {}

    if request.method == 'GET':
        # Get the register page
        context['registration_form'] = RegistrationForm()
        return render(request, 'nanoblog/register.html', context)

    form = RegistrationForm(request.POST)
    context['registration_form'] = form

    if not form.is_valid():
        return render(request, 'nanoblog/register.html', context)

    # The form is valid; create a new user
    new_user = User.objects.create_user(username=request.POST['username'],
                                        password=request.POST['password1'],
                                        email=request.POST['email'],
                                        first_name=request.POST['first_name'],
                                        last_name=request.POST['last_name'])

    new_user.is_active = False

    new_user.save()
    # Create a new blogger and link to the user
    new_blogger = Blogger(user=new_user)
    new_blogger.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = EMAIL_BODY_TEMPLATE % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

    print 'Sending mail to', new_user.email

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="cmbarker@andrew.cmu.edu",
              recipient_list=[new_user.email],
              fail_silently=False)

    context['email'] = form.cleaned_data['email']
    return render(request, 'nanoblog/needs-confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'nanoblog/confirmed.html', {})

def get_profile_pic(request, id):
    """ Get a user's profile picture. """
    blogger = get_object_or_404(Blogger, id=id)
    if not blogger.profile_picture:
        raise Http404
    return HttpResponse(blogger.profile_picture, content_type=blogger.content_type)


