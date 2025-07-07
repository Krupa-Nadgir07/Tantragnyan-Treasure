from django.shortcuts import render, HttpResponse,  redirect
from learners.models import *
from blogging.models import *
from pymongo import MongoClient
client = MongoClient('mongodb+srv://krupanadgir:WUIVqUtKFK0cr5Rw@cluster0.9rvrx.mongodb.net/')
db = client['CP_Prep_Sys']
collection = db['Companies']

# Create your views here.
def home(requests):
    # return HttpResponse('Home Page!')
    if requests.method == 'POST':
        if 'learners' in requests.POST:
            return redirect('learners:sign_up')
        elif 'blogs' in requests.POST:
            return redirect('blogging:blog_home')

    return render(requests, 'home/home.html' )

def topics(requests):
    parent_topics = Topics.objects.filter(parent_topic__isnull=True)
    return render(requests, 'home/topics.html',{'parent_topics':parent_topics})

def topic_page(requests, pid):
    main_topic =Topics.objects.get(topic_id=pid)
    print(main_topic.topic_name)
    sub_topics = Topics.objects.filter(parent_topic_id=pid)
    topic_blogs = Blogs.objects.filter(blog_topic_id=main_topic, status=True)
    query = {main_topic.topic_name: {"$exists": True}} 
    document = collection.find_one(query)
    if document:
        array = document.get(main_topic.topic_name)
        print(array)
    else:
        array = None

    return render(requests, 'home/topic_page.html', {
            'main_topic': main_topic,
            'sub_topics': sub_topics,
            'topic_blogs': topic_blogs,
            'companies': array,
        })