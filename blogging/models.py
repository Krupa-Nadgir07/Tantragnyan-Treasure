from django.db import models
from learners.models import Topics
# from django_ckeditor_5.fields import CKEditor5Field
from tinymce.models import HTMLField
# Create your models here.

class Blogs(models.Model):
    blog_id = models.AutoField(primary_key=True)
    blog_author = models.CharField(max_length=50)
    blog_created_at = models.DateTimeField(auto_now_add=True)
    blog_title = models.CharField(max_length=50)
    blog_topic = models.ForeignKey(Topics, models.DO_NOTHING)
    blog_url = models.URLField(default='link')
    status = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    review_status = models.BooleanField(default=False)
    description = models.TextField(default='Describe')
    content = HTMLField()

    class Meta:
        managed = True
        db_table = 'blogs'
