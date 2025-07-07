from django.shortcuts import render, HttpResponse, redirect
from . forms import *
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
# Create your views here.
def blog_home(request):
    return render(request, 'blogging/want_to_create.html')
    
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_home')  # Redirect to success page after saving
    else:
        form = BlogsForm()
    
    return render(request, 'blogging/blog.html', {'form': form})
def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def blog_list(request):
    if not request.user.is_superuser:
        # return redirect('/admin/login/') 
        return redirect(reverse('admin:login'))
    blogs = Blogs.objects.filter(status=False)  # Fetch unapproved blogs
    return render(request, 'blogging/blog_list.html', {'blogs': blogs})

@user_passes_test(is_superuser)
def approve_blog(request, blog_id):
    """Approve a blog by setting status=True"""
    blog = get_object_or_404(Blogs, blog_id=blog_id)
    blog.status = True  # Mark as approved
    blog.save()
    return redirect('blog_list')  # Redirect back to the list

def blog_detail(request, blog_id):
    blog = Blogs.objects.get(blog_id=blog_id)  # Get the specific blog
    return render(request, 'blogging/blog_detail.html', {'blog': blog})
