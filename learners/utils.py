from django.utils.timezone import now
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
# from .models import Learners
import requests
from django.http import JsonResponse
from django.db import transaction
import requests
from pymongo import MongoClient
client = MongoClient('mongodb+srv://krupanadgir:WUIVqUtKFK0cr5Rw@cluster0.9rvrx.mongodb.net/')
# from .views import client
###################### Web Scraping Imports ######################
# from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import time
from seleniumbase import Driver

# Set up ChromeDriver
def chrome_driver():
    path = "C:/Users/krupa/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    service = Service(path)

################################################################## Leetcode ##################################################################
# GraphQL queries for progress and total number of questions data 
def get_total_leetcode_questions():
    url = "https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
    
    query = {
        "query": """
        query getAllQuestionsCount {
            allQuestionsCount {
                count
            }
        }
        """
    }

    response = requests.post(url, json=query, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        total_questions = data['data']['allQuestionsCount'][0]['count'] # 0th index gives total
        print(total_questions)
        # CpPlatforms.objects.get(cp_platform_name='Leetcode').update(cp_tot_no_of_quest=total_questions)
        CpPlatforms.objects.filter(cp_platform_name='Leetcode').update(cp_tot_no_of_quest=total_questions)
        return total_questions
    
def fetch_leetcode_progress(username, learner):
    url = f"https://leetcode.com/graphql"
    headers = {"Content-Type": "application/json"}
    query = {
        "query": """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
            }
        }
        """,
        "variables": {"username": username}
    }

    response = requests.post(url, json=query, headers=headers)
    data = response.json()

    # if "errors" in data:
    #     return f"Error: {data['errors'][0]['message']}"

    user_data = data['data']['matchedUser']
    submission_data = user_data['submitStats']['acSubmissionNum'][1:]

    total_solved = sum(diff['count'] for diff in submission_data)
    print(total_solved)
    # leetcode_platform, _ = CpPlatforms.objects.get_or_create(cp_platform_name='Leetcode')

    LearnerCpAccCreds.objects.filter(
        learner=learner,
        cp_platform_name="Leetcode",
        # cp_id=leetcode_platform.cp_id,
    ).update(progress=total_solved)

# Webscraping

# For Solved questions
def fetch_leetcode_solved_problems(username, password,learner):
    # driver set up
    chrome_driver()
    driver = Driver(uc=True)
    leetcode_platform, _ = CpPlatforms.objects.get_or_create(cp_platform_name='Leetcode')
    time.sleep(5)
    # problems_data = {'solved': [], 'attempted': []}

    def fetch_problems(url, status):
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="truncate"]')))
        problems = driver.find_elements(By.XPATH, '//div[@class="truncate"]/a')
        time.sleep(5)

        fetched_problems = []
        for problem in problems:
            problem_name = problem.text
            problem_url = problem.get_attribute('href')
            row_element = problem.find_element(By.XPATH, './ancestor::div[@role="row"]')
            difficulty = row_element.find_element(By.XPATH,'.//span[contains(@class, "text-olive") or contains(@class, "text-yellow") or contains(@class, "text-pink")]').text
            # difficulty = 'Unknown'
            if problems.index(problem) == 0:
                continue
            time.sleep(1)
            # Save problem to database
            cleaned_problem_name = problem.text.split('. ', 1)[1]
            problem_catalog, _ = ProblemsCatalog.objects.get_or_create(
                problem_name=cleaned_problem_name,
                platform=leetcode_platform,
                problem_url=problem_url,
                difficulty=difficulty
            )

            Problems.objects.update_or_create(
                learner=learner,
                problem=problem_catalog,
                defaults={'attempt_status': status}
            )

            fetched_problems.append({
                'name': problem_name,
                'url': problem_url,
                'difficulty': difficulty,
                'status': status
            })

            # leet_code_progress += 1   

        # return fetched_problems

    try:
        # Login
        login_url = 'https://leetcode.com/accounts/login/'
        driver.uc_open_with_reconnect(login_url, 4)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="id_login"]')))
        driver.find_element(By.XPATH, '//*[@id="id_login"]').send_keys(username)
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(password)
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(Keys.RETURN)
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.url_contains("leetcode.com"))

        fetch_problems('https://leetcode.com/problemset/?status=AC&page=1', 'solved')
        # fetch_problems('https://leetcode.com/problemset/?status=TRIED&page=1', 'Attempted')

    finally:
        # fetch_leetcode_progress()
        driver.quit()


# For attempted Questions
def fetch_leetcode_attempted_problems(username, password, learner):
    chrome_driver()
    driver = Driver(uc=True)
    leetcode_platform, _ = CpPlatforms.objects.get_or_create(cp_platform_name='Leetcode')
    time.sleep(5)
    # problems_data = {'solved': [], 'attempted': []}

    def fetch_problems(url, status):
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="truncate"]')))
        problems = driver.find_elements(By.XPATH, '//div[@class="truncate"]/a')
        time.sleep(5)

        fetched_problems = []
        for problem in problems:
            problem_name = problem.text
            problem_url = problem.get_attribute('href')
            row_element = problem.find_element(By.XPATH, './ancestor::div[@role="row"]')
            difficulty = row_element.find_element(By.XPATH,'.//span[contains(@class, "text-olive") or contains(@class, "text-yellow") or contains(@class, "text-pink")]').text
            # difficulty = 'Unknown'
            if problems.index(problem) == 0:
                continue
            time.sleep(1)
            # Save problem to database
            cleaned_problem_name = problem.text.split('. ', 1)[1]
            problem_catalog, _ = ProblemsCatalog.objects.get_or_create(
                problem_name=cleaned_problem_name,
                platform=leetcode_platform,
                problem_url=problem_url,
                difficulty=difficulty
            )

            Problems.objects.update_or_create(
                learner=learner,
                problem=problem_catalog,
                defaults={'attempt_status': status}
            )

            fetched_problems.append({
                'name': problem_name,
                'url': problem_url,
                'difficulty': difficulty,
                'status': status
            })

            # leet_code_progress += 1   

        # return fetched_problems

    try:
        # Login
        login_url = 'https://leetcode.com/accounts/login/'
        driver.uc_open_with_reconnect(login_url, 4)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="id_login"]')))
        driver.find_element(By.XPATH, '//*[@id="id_login"]').send_keys(username)
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(password)
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(Keys.RETURN)
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.url_contains("leetcode.com"))

        # fetch_problems('https://leetcode.com/problemset/?status=AC&page=1', 'Solved')
        fetch_problems('https://leetcode.com/problemset/?status=TRIED&page=1', 'attempted')

    finally:
        driver.quit()

################################################################## Codeforces ##################################################################

# Classify Questions based on their ranking as CF is like that
def classify_difficulty(rating):
    if not isinstance(rating, int):
        return 'Unknown'
    if rating < 1200:
        return 'Easy'
    elif 1200 <= rating < 1700:
        return 'Medium'
    else:
        return 'Difficult'
    

# Get total number of Questions to calculate progress of user
def get_total_codeforces_questions():
    url = "https://codeforces.com/api/problemset.problems"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        total_problems = len(data['result']['problems'])
        CpPlatforms.objects.update(cp_tot_no_of_quest=total_problems,cp_platform_name='Codeforces')
        return total_problems
    else:
        return None  # Return None if there's an error


# Get total number of Questions solved by user to calculate progress of user
def fetch_codeforces_progress(username, learner):
    url = f"https://codeforces.com/api/user.status?handle={username}"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"Error: Unable to fetch user data for {username}"

    data = response.json()

    if data['status'] != 'OK':
        return f"Error: {data['comment']}"
    
    problems_info = data['result']
    total_solved = 0
    for problem in problems_info:
        if problem['verdict'] == 'OK':
            total_solved += 1

    total_problems = get_total_codeforces_questions()
    # print(total_problems)
    
    if total_problems is None:
        return "Error fetching total problems count from Codeforces"

    total_progress = {
        "username": username,
        "solved_problems_percentage": (total_solved / total_problems) * 100  # percentage calculation
    }

    # Update learner's progress in the database
    LearnerCpAccCreds.objects.filter(
    learner=learner,
    cp_platform_name="Codeforces").update(
    progress=total_problems)

    return total_problems


# One solo function called twice for attempted and solved
def fetch_codeforces_problems(username, learner, status_filter=None):
    user_status_url = f"https://codeforces.com/api/user.status?handle={username}"
    problemset_url = "https://codeforces.com/api/problemset.problems"
    user_status_response = requests.get(user_status_url)
    problemset_response = requests.get(problemset_url)

    if user_status_response.status_code != 200 or problemset_response.status_code != 200:
        return

    user_data = user_status_response.json()
    problems_data = problemset_response.json()

    if user_data['status'] != 'OK':
        return
    
    codeforces_platform, _ = CpPlatforms.objects.get_or_create(cp_platform_name='Codeforces')
    for problem in user_data['result']:
        verdict = problem.get('verdict', '')
        if status_filter == 'Solved' and verdict != 'OK':
            continue
        if status_filter == 'Attempted' and verdict == 'OK':
            continue
        
        rating = problem['problem'].get('rating', 'N/A')
        problem_info = {
            'url': f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['problem']['index']}",
            'name': problem['problem']['name'],
            'difficulty': classify_difficulty(rating if rating != 'N/A' else None),
            'status': 'solved' if verdict == 'OK' else 'attempted',
            'attempts': problem.get('attempts', 0)
        }

        problem_catalog, _ = ProblemsCatalog.objects.get_or_create(
            problem_name=problem_info['name'],
            platform=codeforces_platform,
            problem_url=problem_info['url'],
            difficulty=problem_info['difficulty']
        )

        Problems.objects.update_or_create(
            learner=learner,
            problem=problem_catalog,
            defaults={'attempt_status': problem_info['status']}
        )

def fetch_codeforces_solved_problems(username,password, learner):
    fetch_codeforces_problems(username, learner, status_filter='solved')

def fetch_codeforces_attempted_problems(username,password, learner):
    fetch_codeforces_problems(username, learner, status_filter='attempted')



################################################################## Hackerearth ##################################################################
# def fetch_hackerearth_progress(username, learner):

# One solo function called twice for attempted and solved
def fetch_hackerearth_problems(username, password, learner, status_type='solved'):
    # driver setup
    chrome_driver()
    driver = Driver(uc=True)
    hackerearth_platform, _ = CpPlatforms.objects.get_or_create(cp_platform_name='Hackerearth')
    
    try:
        # Login
        login_url = 'https://www.hackerearth.com/login/'
        driver.uc_open_with_reconnect(login_url, 4)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="id_login"]')))
        driver.find_element(By.XPATH, '//*[@id="id_login"]').send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.url_contains("https://www.hackerearth.com/challenges/"))
        time.sleep(10)


        #################### Progress Calculation ####################
        driver.get('https://www.hackerearth.com/practice/')
        container = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='stats-container card']"))
        )
        # print(len(container))
        numbers_container = container[0].find_elements(By.XPATH, ".//div[@class = 'numbers']")
        isolved = numbers_container[0].find_element(By.XPATH, ".//div[@class = 'count']")
        # print(isolved.text)
        numerator, denominator = isolved.text.split('/')
        numerator = int(numerator)
        denominator = int(denominator)

        CpPlatforms.objects.filter(cp_platform_name='Hackerearth').update(cp_tot_no_of_quest=denominator)
        LearnerCpAccCreds.objects.filter(
        learner=learner,
        cp_platform_name="Hackerearth").update(
        progress=numerator)


        #################### Questions Scraping ####################
        driver.get(f'https://www.hackerearth.com/practice/problems/?limit=100&offset=0&status={status_type}')

        dropdown_arrow = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "i.icon.ui-chevron-arrow-bottom")))
        dropdown_arrow.click()
        time.sleep(5)

        status_option = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"div.option[data-option='{status_type}']")))
        status_option.click()
        time.sleep(5)

        container = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='main-container grid-container']")))
        problems = container[0].find_elements(By.XPATH, ".//div[@class = 'table-row']")

        for problem in problems:
            problem_entity = problem.find_element(By.XPATH,".//div[@class = 'table-column title']/a")
            problem_name = problem_entity.text
            problem_url = problem_entity.get_attribute("href")
            difficulty_entity = problem.find_element(By.XPATH,".//div[@class = 'table-column difficulty']/span")
            difficulty = difficulty_entity.text

            problem_catalog, _ = ProblemsCatalog.objects.get_or_create(
                problem_name=problem_name,
                platform=hackerearth_platform,
                problem_url=problem_url,
                difficulty=difficulty
            )

            Problems.objects.update_or_create(
                learner=learner,
                problem=problem_catalog,
                defaults={'attempt_status': status_type}
            )
        

    finally:
        driver.quit()


def fetch_hackerearth_solved_problems(username, password, learner):
    fetch_hackerearth_problems(username, password, learner, status_type='solved')

def fetch_hackerearth_attempted_problems(username, password, learner):
    fetch_hackerearth_problems(username, password, learner, status_type='attempted')

###################################################################################################################################################

# Clustering

import numpy as np
from sklearn.preprocessing import StandardScaler
from learners.models import Learners
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from datetime import datetime

def get_learner_vector(learner):
    topic_vector = np.zeros(7)
    # topics = learner.topics.all() 

    all_topics = ['Algorithms', 'Data Structures', 'C++', 'Java', 'Python', \
                       'Databases', 'Artificial Intelligence'] 
    # Mapping Strength values of learners
    topic_mapping = {topic: idx for idx, topic in enumerate(all_topics)}
    domains_interested = DomainsInterested.objects.filter(learner=learner)
    for domain in domains_interested:
        if domain.domain_name in topic_mapping:
            topic_vector[topic_mapping[domain.domain_name]] = 1

    return topic_vector

def cluster_learners(creator):
    
    learners = Learners.objects.filter(in_study_group=False)
    learner_vectors = []
    learner_ids = []
    for learner in learners:
        learner_vector = get_learner_vector(learner)
        learner_vectors.append(learner_vector)
        learner_ids.append(learner.learner_id)

    learner_vectors = np.array(learner_vectors)
    scaler = StandardScaler()
    learner_vectors_scaled = scaler.fit_transform(learner_vectors)

    pca = PCA(n_components=2)  # Reduce to 2 dimensions for visualization or experimentation
    learner_vectors_pca = pca.fit_transform(learner_vectors_scaled)

    agg_clustering = AgglomerativeClustering(n_clusters=10, linkage='ward')
    cluster_labels = agg_clustering.fit_predict(learner_vectors_pca)

    creator_index = learner_ids.index(creator.learner_id)
    creator_cluster_label = cluster_labels[creator_index]
    learners_in_creator_cluster = [learner_ids[i] for i in range(len(learner_ids)) if cluster_labels[i] == creator_cluster_label]

    for learner in learners_in_creator_cluster:
        learner_instance = Learners.objects.get(learner_id = learner)
        learner_instance.in_study_group = True
    db = client['CP_Prep_Sys']
    collection = db['Study Group']
    
    study_group_data = {
        # 'stud_id': f"{topic}_best",
        # 'name': study_group_name,
        'learner_ids': learners_in_creator_cluster,
        'game_meet_url': '',
        'activities': [],
        'messages': [],
        'meeting_info':{},
        # 'topic_focused': topic,
        # 'creator_id': creator.learner_id,
        'member_count': len(learners_in_creator_cluster),
        'creation_timestamp': datetime.now()
    }

    collection.insert_one(study_group_data)
    return learners_in_creator_cluster