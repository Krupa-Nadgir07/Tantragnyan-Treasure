from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.contrib import messages
from .forms import *
from django.utils.timezone import now
from .models import *
from blogging.models import *
from .utils import *
from selenium.common.exceptions import TimeoutException
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
# Create your views here.
client = MongoClient('mongodb+srv://krupanadgir:WUIVqUtKFK0cr5Rw@cluster0.9rvrx.mongodb.net/')
db = client['CP_Prep_Sys']
collection = db['Study Group']

def sign_in(request):
    form = SignInForm()
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username_or_email, password=password)
            print(f"Authenticating user: {username_or_email} with password: {password}")

            if user is None:
                messages.error(request, "Invalid username, email, or password.")
                return render(request, 'learners/sign_in.html', {'form': form})

            login(request, user)
            try:
                if '@' in username_or_email:
                    Learners.objects.get(email_id=username_or_email)
                else:
                    Learners.objects.get(user_name=username_or_email)
                return redirect('dashboard')
            except:
                messages.error(request, "Learner record not found.")  # Very rare case
                return redirect('sign_in')

    return render(request, 'learners/sign_in.html', {'form': form})

def sign_up(request):
    learner_form = LearnerForm()

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        learner_form = LearnerForm(request.POST)

        if user_form.is_valid() and learner_form.is_valid():
            username = user_form.cleaned_data['username']
            email = learner_form.cleaned_data['email_id']
            if User.objects.filter(username=username).exists():
                return HttpResponse(f"Username '{username}' is already taken.", status=400)

            if User.objects.filter(email=email).exists():
                return HttpResponse(f"An account with email '{email}' already exists.", status=400)

            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.email = email
            user.save()

            learner = learner_form.save(commit=False)
            learner.user_name = user
            learner.save()

            user = authenticate(username=user.username, password=user_form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('cp_account_info')
    
    else:
        user_form = UserRegistrationForm()
        learner_form = LearnerForm()
        
    context = {'user_form': user_form,
               'learner_form': learner_form}
    return render(request,'learners/sign_up.html', context)

def cp_acc_info(request):
    cp_form1 = CPAccountsForm(request.POST, prefix='leetcode')
    # cp_form2 = CPAccountsForm(request.POST, prefix='codechef')
    cp_form2 = CPAccountsForm(request.POST, prefix='codeforces')
    cp_form3 = CPAccountsForm(request.POST, prefix='hackerearth')
    
    if cp_form1.is_valid() and cp_form3.is_valid() and cp_form2.is_valid():

        try:
            learner_instance = Learners.objects.get(user_name=request.user)
        except Learners.DoesNotExist:
            return HttpResponse("Learner instance not found.", status=404)

        for form, platform_name in zip(
                [cp_form1, cp_form2,cp_form3],
                ['Leetcode','Codeforces','Hackerearth']
            ):
                cp_account = form.save(commit=False)
                cp_account.learner = learner_instance  
                cp_account.cp_platform_name = platform_name  
                cp_account.last_synced = now() 

                try:
                    # cp_instance = CpPlatforms.objects.get(cp_platform_name=platform_name)
                    cp_instance = CpPlatforms.objects.filter(cp_platform_name__iexact=platform_name).first()
                except CpPlatforms.DoesNotExist:
                    return HttpResponse(f"Platform '{platform_name}' does not exist.", status=404)
                
                cp_account.cp = cp_instance
                cp_account.progress = 0.00

                try:
                    cp_account.save()
                except IntegrityError:
                    return HttpResponse("This platform account already exists for the learner.", status=400)

        return redirect('domain_interested')
    
    context = {'cp_form1':cp_form1,'cp_form3':cp_form2,'cp_form4':cp_form3}
    
    return render(request,'learners/cp_account_info.html', context)

def domain_interested(request):
    if request.method == "POST":
        try:
            learner_instance = Learners.objects.get(user_name=request.user)
        except Learners.DoesNotExist:
            return HttpResponse("Learner instance not found.", status=404)
        
        items = request.POST.getlist('items[]')
        for item in items:
            DomainsInterested.objects.create(domain_name=item, learner_id=learner_instance.learner_id)

        return redirect('dashboard')
    
    domains = Topics.objects.filter(parent_topic__isnull=True)
    
    return render(request, 'learners/domain_interested.html',{'domains': domains})


def strong_weak_topics(request):
    if request.method == "POST":
        try:
            learner_instance = Learners.objects.get(user_name=request.user)
        except Learners.DoesNotExist:
            return HttpResponse("Learner instance not found.", status=404)
        
        parent_topics = Topics.objects.filter(parent_topic__isnull=True)
        for topic in parent_topics:
            rating = request.POST.get(f'topic_{topic.topic_id}')
            StrongWeakTopics.objects.create(topic_name=topic.topic_name, \
                                            learner_id=learner_instance.learner_id,\
                                            difficulty=rating)

        return redirect('dashboard')
    parent_topics = Topics.objects.filter(parent_topic__isnull=True)
    return render(request, 'learners/strong_weak_topics.html',{'parent_topics': parent_topics})


@login_required
def dashboard(request):
    learner = request.user
    # print(learner)
    learner_instance = Learners.objects.get(user_name=learner)
    learner_cps = LearnerCpAccCreds.objects.filter(learner_id=learner_instance)
    cp_instances = CpPlatforms.objects.all()
    lc_instance = CpPlatforms.objects.get(cp_platform_name='Leetcode')
    cf_instance = CpPlatforms.objects.get(cp_platform_name='Codeforces')
    he_instance = CpPlatforms.objects.get(cp_platform_name='Hackerearth')
    problems_solved = {}
    for instance in cp_instances:
        progress = LearnerCpAccCreds.objects.get(learner_id=learner_instance,cp=instance.cp_id).progress
        tot_quest = instance.cp_tot_no_of_quest
        quest_solved = tot_quest
        if quest_solved == 0:
            quest_solved = 1
        problems_solved[instance.cp_platform_name]=progress
    learner_domains = DomainsInterested.objects.filter(learner=learner_instance)
    return render(request, 'learners/dashboard.html',{'learner_instance':learner_instance,\
                    'cp_instances':cp_instances,'learner_domains':learner_domains,'learner_cps':learner_cps,\
                        'problems_solved':problems_solved,'lc_instance':lc_instance,\
                        'cf_instance':cf_instance,'he_instance':he_instance})

@login_required
def solved(request):
    learner = request.user
    # print(learner)
    learner_instance = Learners.objects.get(user_name=learner)
    print(learner_instance)
    # learner_cp_creds = LearnerCpAccCreds.objects.get(learner=learner_instance)
    # print(learner_cp_creds)

    platform_problems = {}
    # overall_progress = {}

    platforms = ['Leetcode', 'Codeforces', 'Hackerearth']
    for platform in platforms:
        try:
            platform_instance = CpPlatforms.objects.filter(cp_platform_name=platform).first()
            learner_cp_creds_instance = LearnerCpAccCreds.objects.get(learner=learner_instance, cp_platform_name=platform_instance.cp_platform_name)
            print(platform_instance.cp_platform_name)
            print(learner_cp_creds_instance.learner)
            # Fetch problems from the database
            if platform_instance and learner_cp_creds_instance:
                # Fetch problems for this learner from Problems model
                # problems = ProblemsCatalog.objects.filter(learner=learner_instance, problem=platform_instance).select_related('problem')
                problems = Problems.objects.filter(learner=learner_instance, problem__platform=platform_instance, attempt_status='solved').select_related('problem__platform')
                platform_problems[platform] = [
                    {
                        'problem_id':prob.problem.problem_id,
                        'problem_name': prob.problem.problem_name,
                        'difficulty': prob.problem.difficulty,
                        'problem_url': prob.problem.problem_url,
                        'attempt_status': prob.attempt_status,
                        'bookmarked_status':prob.bookmarked_status
                    } for prob in problems
                ]
                # overall_progress[platform] = learner_cp_creds_instance.progress
            else:
                # platform_instance = CpPlatforms.objects.filter(cp_platform_name=platform).first()
                # platform_problems[platform] = Problems.objects.filter(learner=learner_instance, problem__platform=platform_instance, attempt_status='Attempted').select_related('problem__platform')
                # overall_progress[platform] = 0.00
                platform_problems[platform] = []

        except CpPlatforms.DoesNotExist:
            platform_problems[platform] = []
            # overall_progress[platform] = 0.00

    if request.method == 'POST':
        # print(request.POST)
        problem_id = request.POST.get('problem_id')
        # print(problem_id)
        learner_fetch = request.user
        # print(learner_fetch)
        learner_id = Learners.objects.filter(user_name=learner_fetch).first()
        # print(learner_id)
        problem_instance = get_object_or_404(
            Problems,
            problem_id=problem_id,
            learner_id=learner_id
        )
        # bookmarked_status = 'bookmarked_status' in request.POST
        problem_instance.bookmarked_status = not problem_instance.bookmarked_status
        problem_instance.save()
        return redirect('solved')

    return render(request, 'learners/solved.html', {
        'learner': learner_instance,
        'platform_problems': platform_problems,
        # 'overall_progress': overall_progress,
    })

@login_required
def attempted(request):
    learner = request.user
    # print(learner)
    learner_instance = Learners.objects.get(user_name=learner)
    # print(learner_instance)
    # learner_cp_creds = LearnerCpAccCreds.objects.get(learner=learner_instance)
    # print(learner_cp_creds)

    platform_problems = {}
    # overall_progress = {}


    platforms = ['Leetcode', 'Codeforces', 'Hackerearth']
    for platform in platforms:
        try:
            platform_instance = CpPlatforms.objects.filter(cp_platform_name=platform).first()
            learner_cp_creds_instance = LearnerCpAccCreds.objects.get(learner=learner_instance, cp_platform_name=platform_instance.cp_platform_name)
            # print(platform_instance.cp_platform_name)
            # print(learner_cp_creds_instance.learner)
            # Fetch problems from the database
            if platform_instance and learner_cp_creds_instance:
                # Fetch problems for this learner from Problems model
                # problems = ProblemsCatalog.objects.filter(learner=learner_instance, problem=platform_instance).select_related('problem')
                problems = Problems.objects.filter(learner=learner_instance, problem__platform=platform_instance, attempt_status='attempted').select_related('problem__platform')
                platform_problems[platform] = [
                    {
                        'problem_id':prob.problem.problem_id,
                        'problem_name': prob.problem.problem_name,
                        'difficulty': prob.problem.difficulty,
                        'problem_url': prob.problem.problem_url,
                        'attempt_status': prob.attempt_status,
                        'bookmarked_status':prob.bookmarked_status
                    } for prob in problems
                ]
                # overall_progress[platform] = learner_cp_creds_instance.progress
            else:
                # platform_instance = CpPlatforms.objects.filter(cp_platform_name=platform).first()
                # platform_problems[platform] = Problems.objects.filter(learner=learner_instance, problem__platform=platform_instance, attempt_status='Attempted').select_related('problem__platform')
                # overall_progress[platform] = 0.00
                platform_problems[platform] = []

        except CpPlatforms.DoesNotExist:
            platform_problems[platform] = []
            # overall_progress[platform] = 0.00

    if request.method == 'POST':
        # print(request.POST)
        problem_id = request.POST.get('problem_id')
        # print(problem_id)
        learner_fetch = request.user
        # print(learner_fetch)
        learner_id = Learners.objects.filter(user_name=learner_fetch).first()
        # print(learner_id)
        problem_instance = get_object_or_404(
            Problems,
            problem_id=problem_id,
            learner_id=learner_id
        )
        print(request.POST)
        # bookmarked_status = 'bookmarked_status' in request.POST
        # problem_instance.bookmarked_status = bookmarked_status
        problem_instance.bookmarked_status = not problem_instance.bookmarked_status
        problem_instance.save()
        return redirect('attempted')

    return render(request, 'learners/attempted.html', {
        'learner': learner_instance,
        'platform_problems': platform_problems,
        # 'overall_progress': overall_progress,
    })

@login_required
def sync_cp_account(request, platform, status):
    # platform_name = platform.lower()
    if request.method == "POST":
        try:
            learner = request.user
            learner_2 = Learners.objects.filter(user_name=learner).first()  # filter Learner by username

            # Fetch learner's platform credentials using learner_id
            learner_cp_creds = LearnerCpAccCreds.objects.filter(learner=learner_2, cp_platform_name=platform).first()

            if not learner_cp_creds:
                return JsonResponse({"error": f"No credentials found for {platform}."}, status=400)
            
            platform_instance = CpPlatforms.objects.filter(cp_platform_name=platform).first()

            fetch_problems_function = globals().get(f"fetch_{platform.lower()}_{status}_problems")
            overall_progress = globals().get(f"fetch_{platform.lower()}_progress")
            if overall_progress and platform.lower() != 'hackerearth':
                overall_progress(learner_cp_creds.cp_username, learner_2)
                print("Leetcode working")
                print("overall_progress:", overall_progress)
            if fetch_problems_function:
                fetch_problems_function(
                    learner_cp_creds.cp_username,
                    learner_cp_creds.password,
                    learner_2
                )
                # return JsonResponse({"success": f"Synced {platform} successfully!"})
                return redirect('solved' if status == 'solved' else 'attempted')
            else:
                return JsonResponse({"error": f"No fetch function found for {platform}."}, status=400)
        except CpPlatforms.DoesNotExist:
            return JsonResponse({"error": f"Platform {platform} does not exist."}, status=400)
        except Learners.DoesNotExist:
            return JsonResponse({"error": f"Learner {learner.user_name} not found."}, status=404)
        except TimeoutException:
            return JsonResponse({"error": f"Syncing {platform} timed out."}, status=500)
        except Exception as e:
            # return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
            print(e)
            return redirect('solved' if status == 'solved' else 'attempted')

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def bookmarks(request):
    learner = request.user
    # print(learner)
    learner_instance = Learners.objects.get(user_name=learner)
    # print(learner_instance)
    # learner_cp_creds = LearnerCpAccCreds.objects.get(learner=learner_instance)
    # print(learner_cp_creds)

    platform_problems = {}
    # overall_progress = {}


    platforms = ['Leetcode', 'Codeforces', 'Hackerearth']
    for platform in platforms:
        try:
            platform_instance = CpPlatforms.objects.filter(cp_platform_name=platform).first()
            print(platform_instance)
            learner_cp_creds_instance = LearnerCpAccCreds.objects.get(learner=learner_instance, cp_platform_name=platform_instance.cp_platform_name)
            # print(platform_instance.cp_platform_name)
            # print(learner_cp_creds_instance.learner)
            # Fetch problems from the database
            if platform_instance and learner_cp_creds_instance:
                # Fetch problems for this learner from Problems model
                # problems = ProblemsCatalog.objects.filter(learner=learner_instance, problem=platform_instance).select_related('problem')
                problems = Problems.objects.filter(learner=learner_instance, problem__platform=platform_instance, attempt_status__in=['attempted', 'solved']).select_related('problem__platform')
                platform_problems[platform] = [
                    {
                        'problem_id':prob.problem.problem_id,
                        'problem_name': prob.problem.problem_name,
                        'difficulty': prob.problem.difficulty,
                        'problem_url': prob.problem.problem_url,
                        'attempt_status': prob.attempt_status,
                        'bookmarked_status':prob.bookmarked_status
                    } for prob in problems if prob.bookmarked_status == True
                ]
                # overall_progress[platform] = learner_cp_creds_instance.progress
            else:
                # platform_instance = CpPlatforms.objects.filter(cp_platform_name=platform).first()
                # platform_problems[platform] = Problems.objects.filter(learner=learner_instance, problem__platform=platform_instance, attempt_status='Attempted').select_related('problem__platform')
                # overall_progress[platform] = 0.00
                platform_problems[platform] = []

        except CpPlatforms.DoesNotExist:
            platform_problems[platform] = []
            # overall_progress[platform] = 0.00
    print(platform_problems)
    return render(request, 'learners/bookmarks.html', {
        'learner': learner_instance,
        'platform_problems': platform_problems,
        # 'overall_progress': overall_progress,
    })

@login_required
def topics(request):
    learner = request.user
    print(learner)
    learner_instance = Learners.objects.get(user_name=learner)
    learner_domains = DomainsInterested.objects.filter(learner=learner_instance)
    domain_names = [domain.domain_name for domain in learner_domains]
    blog_items = Blogs.objects.filter(blog_topic__topic_name__in=domain_names)
    
    return render(request,'learners/domains.html', {'blog_items': blog_items,})

@login_required
def goals(request):
    if request.method == 'POST':
        learner_instance = Learners.objects.get(user_name=request.user)
        goal_id = request.POST.get('goal_id')
        goal = Goals.objects.get(goal_id=goal_id,learner_id=learner_instance.learner_id)
        goal.delete()
        messages.success(request, "Congratulations! You are one step forward towards achieving your dreams!")
        return redirect('goals')

    learner_instance = Learners.objects.get(user_name=request.user)
    goals = Goals.objects.filter(learner_id=learner_instance.learner_id, goal_is_active=True)
    if not goals:
        return render(request, 'learners/goals.html', {
        'learner': learner_instance,
        # 'goals_of_user': goals,
        # 'overall_progress': overall_progress,
    })
    return render(request, 'learners/goals.html', {
        'learner': learner_instance,
        'goals_of_user': goals,
        # 'overall_progress': overall_progress,
    })

def new_goal(request):
    if request.method == "POST":
        try:
            learner_instance = Learners.objects.get(user_name=request.user)
        except Learners.DoesNotExist:
            return HttpResponse("Learner instance not found.", status=404)
        
        goal_data = request.POST
        goal_type = goal_data['goal_type']
        goal_description = goal_data['goal_description']
        goal_start = datetime.strptime(goal_data['goal_start'], "%Y-%m-%d").date()
        if goal_type == 'Monthly':
            goal_end = goal_start + timedelta(days=30)
        elif goal_type == 'Weekly':
            goal_end = goal_start + timedelta(weeks=1)
        else:
            goal_end = datetime.strptime(goal_data['goal_end'], "%Y-%m-%d").date()

        # goal_is_active = True
        # learner = learner_instance

        Goals.objects.create(goal_type=goal_type,goal_description=goal_description,\
                             goal_start=goal_start,goal_end=goal_end,learner_id=learner_instance)
        return redirect('goals')
    else:
        return render(request,'learners/new_goal.html')

@login_required
def create_study_group(request):
    client = MongoClient('mongodb+srv://krupanadgir:WUIVqUtKFK0cr5Rw@cluster0.9rvrx.mongodb.net/')
    db = client['CP_Prep_Sys']
    collection = db['Study Group']

    learner = request.user
    learner_instance = Learners.objects.get(user_name=learner)
    learner_to_fetch = learner_instance.learner_id

    if learner_instance.in_study_group:
        return redirect('study_group')
    
    # query = {"learner_ids":learner_to_fetch}
    # study_group_of_learner = collection.find_one(query)

    # if study_group_of_learner:
    #     print(study_group_of_learner)
    #     return redirect('study_group')

    if request.method == 'POST':
        try:
            learner_instance = Learners.objects.get(user_name=request.user)
        except Learners.DoesNotExist:
            return HttpResponse("Learner instance not found.", status=404)
        
        # study_group_data = request.POST
        # topic = study_group_data['topics_focused_on']
        # strong_weak = study_group_data['strength_of_topic'][0]
        # print(topic)

        study_learners = cluster_learners(learner_instance)
        for learner in study_learners:
            print(learner)
            learner_instance = Learners.objects.get(learner_id=learner)
            learner_instance.in_study_group = True
            learner_instance.save()
        return redirect('study_group')

    return render(request, 'learners/create_study_group.html')

from datetime import datetime

from datetime import datetime
from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Learners

@login_required
def study_group(request):

    learner = request.user
    learner_instance = Learners.objects.get(user_name=learner)
    learner_to_fetch = learner_instance.learner_id
    query = {"learner_ids": learner_to_fetch}
    study_group_of_learner = collection.find_one(query)

    if study_group_of_learner:  # Ensure the group exists
        members = study_group_of_learner['learner_ids']
        member_names = []

        for member in members:
            member_instance = Learners.objects.get(learner_id=member)
            member_names.append(member_instance.user_name)

        group_messages = study_group_of_learner['messages']
        activities = study_group_of_learner['activities']
        meet_info = study_group_of_learner['meeting_info']
        member_count = study_group_of_learner['member_count']

        activities = [
        {key.replace("_", " "): value for key, value in activity.items()}
        for activity in activities
        ]
        meet_info = {key.replace("_", " "): value for key, value in meet_info.items()}

        if request.method == 'POST':
            # Handle message submission
            if 'message' in request.POST:
                message_content = request.POST['message']
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Prepare the message object
                new_message = {
                    "sender": learner_instance.user_name,
                    "message": message_content,
                    "timestamp": timestamp
                }

                # Update the messages in MongoDB
                collection.update_one(
                    {"learner_ids": learner_to_fetch},
                    {"$push": {"messages": new_message}}
                )

                # Reload the updated study group
                study_group_of_learner = collection.find_one(query)
                group_messages = study_group_of_learner['messages']

    return render(request, 'learners/study_group.html', {
        'member_names': member_names,
        'group_messages': group_messages,
        'activities': activities,
        'meet_info': meet_info,
        'member_count': member_count
    })

def schedule_meeting(request):
    client = MongoClient('mongodb+srv://krupanadgir:WUIVqUtKFK0cr5Rw@cluster0.9rvrx.mongodb.net/')
    db = client['CP_Prep_Sys']
    collection = db['Study Group']
    learner = request.user
    learner_instance = Learners.objects.get(user_name=learner)
    learner_to_fetch = learner_instance.learner_id

    # Handle the form for scheduling the meeting
    if request.method == 'POST':
        meeting_title = request.POST['meetingTitle']
        meeting_date = request.POST['meetingDate']
        meeting_time = request.POST['meetingTime']
        meeting_link = request.POST['meetingLink']

        # Update the meeting info in MongoDB
        updated_meeting_info = {
            "meeting_title": meeting_title,
            "meeting_date": meeting_date,
            "meeting_time": meeting_time,
            "meeting_link": meeting_link
        }

        result = collection.update_one(
            {"learner_ids": learner_to_fetch},
            {"$set": {"meeting_info": updated_meeting_info}}
        )

        print(f'Updated {result.modified_count} documents.')

        # Reload the updated study group
        study_group_of_learner = collection.find_one({"learner_ids": learner_to_fetch})
        group_messages = study_group_of_learner['messages']
        activities = study_group_of_learner['activities']
        meet_info = study_group_of_learner['meeting_info']
        member_count = study_group_of_learner['member_count']

        return redirect('study_group')  # Redirect to the study group page

    return render(request, 'learners/schedule_meeting.html')

def plan_activity(request):
    # Handle the form for planning the activity
    client = MongoClient('mongodb+srv://krupanadgir:WUIVqUtKFK0cr5Rw@cluster0.9rvrx.mongodb.net/')
    db = client['CP_Prep_Sys']
    collection = db['Study Group']
    learner = request.user
    learner_instance = Learners.objects.get(user_name=learner)
    learner_to_fetch = learner_instance.learner_id

    # Handle the form for scheduling the activity
    if request.method == 'POST':
        activity_title = request.POST['activityTitle']
        activity_description = request.POST['activityDescription']
        activity_date = request.POST['activityDate']
        activity_time = request.POST['activityTime']

        # Update the activity info in MongoDB
        updated_activity_info = {
            "activity_title": activity_title,
            "activity_description": activity_description,
            "activity_date": activity_date,
            "activity_time": activity_time
        }

        result = collection.update_one(
            {"learner_ids": learner_to_fetch},
            {"$push": {"activities": updated_activity_info}}
        )

        print(f'Updated {result.modified_count} documents.')

        # Reload the updated study group
        study_group_of_learner = collection.find_one({"learner_ids": learner_to_fetch})
        group_messages = study_group_of_learner['messages']
        activities = study_group_of_learner['activities']
        meet_info = study_group_of_learner['meeting_info']
        member_count = study_group_of_learner['member_count']

        return redirect('study_group')  # Redirect to the study group page

    return render(request, 'learners/plan_activity.html')

def my_domains(request):
    learner = request.user
    learner_instance = Learners.objects.get(user_name=learner)
    learner_domains = DomainsInterested.objects.filter(learner=learner_instance)
    topic_instances = []

    for item in learner_domains:
        topic_instance = Topics.objects.get(topic_name=item.domain_name)
        topic_instances.append(topic_instance)

    return render(request, 'learners/domains.html',{'topic_instances':topic_instances})