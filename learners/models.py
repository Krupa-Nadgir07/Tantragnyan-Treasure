from django.db import models
from datetime import timezone
from django.contrib.auth.models import User
# import datetime
from datetime import datetime
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password

PREPARING_FOR = (('Intern','Internship'),('Job','Full Time'))
# Create your models here.
class Learners(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    learner_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    email_id = models.CharField(unique=True, max_length=200)
    # password = models.TextField()
    date_of_birth = models.DateField()
    age = models.IntegerField(blank=True, null=True)
    preparing_for = models.CharField(choices=PREPARING_FOR, default='Job')
    in_study_group = models.BooleanField(default=False)
    learner_since = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'learners'

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            today = datetime.now(timezone.utc)
            self.age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

        super(Learners, self).save(*args, **kwargs)


class DomainsInterested(models.Model):
    main_pk = models.AutoField(primary_key=True)
    learner = models.ForeignKey(Learners, models.DO_NOTHING, to_field='learner_id')  # The composite primary key (learner_id, domain_name) found, that is not supported. The first column is selected.
    domain_name = models.TextField()

    class Meta:
        managed = True
        db_table = 'domains_interested'
        unique_together = (('learner', 'domain_name'),)

class CpPlatforms(models.Model):
    cp_id = models.AutoField(primary_key=True)
    cp_platform_name = models.CharField(max_length=50,unique=True)
    cp_url = models.TextField()
    # cp_logo_url = models.TextField(blank=True, null=True)
    cp_tot_no_of_quest = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'cp_platforms'

class LearnerCpAccCreds(models.Model):
    main_pk = models.AutoField(primary_key=True)
    learner = models.ForeignKey(Learners,on_delete=models.CASCADE,to_field='learner_id')  # The composite primary key (learner_id, cp_id) found, that is not supported. The first column is selected.
    cp = models.ForeignKey(CpPlatforms,on_delete=models.CASCADE)
    cp_platform_name = models.CharField(max_length=50)
    cp_username = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    progress = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # is_verified = models.BooleanField(blank=True, null=True)
    last_synced = models.DateTimeField(blank=True, null=True,default=now)

    class Meta:
        managed = True
        db_table = 'learner_cp_acc_creds'
        unique_together = (('learner', 'cp'),)

    def __str__(self):
        return f"{self.learner} - {self.cp} - {self.cp_username}"
    
    def update_last_synced(self):
        self.last_synced = now()
        self.save()

    def save(self, *args, **kwargs):
        # if self.password and not self.password.startswith('pbkdf2_'):
        #     self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Topics(models.Model):
    topic_id = models.AutoField(primary_key=True)
    topic_name = models.CharField(max_length=50)
    # created_at = models.DateTimeField()
    parent_topic = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'topics'
    
    def __str__(self):
        return self.topic_name

class StrongWeakTopics(models.Model):
    main_pk = models.AutoField(primary_key=True)
    learner = models.ForeignKey(Learners, models.DO_NOTHING)  # The composite primary key (learner_id, topic_id) found, that is not supported. The first column is selected.
    topic_name = models.CharField(default='Unknown')
    difficulty = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'strong_weak_topics'
        # unique_together = (('learner', 'topic'),)

class ProblemsCatalog(models.Model):
    problem_id = models.AutoField(primary_key=True)
    problem_name = models.TextField()
    platform = models.ForeignKey(CpPlatforms, models.DO_NOTHING)
    difficulty = models.TextField()
    problem_url = models.TextField()

    class Meta:
        managed = True
        db_table = 'problems_catalog'

class Problems(models.Model):
    main_pk = models.AutoField(primary_key=True)
    learner = models.ForeignKey(Learners, models.DO_NOTHING)  # The composite primary key (learner_id, problem_id) found, that is not supported. The first column is selected.
    problem = models.ForeignKey(ProblemsCatalog, models.DO_NOTHING)
    attempt_status = models.TextField()
    bookmarked_status = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'problems'
        unique_together = (('learner', 'problem'),)

GOAL_CHOICE = (('Daily','Daily'),('Weekly','Weekly'), ('Monthly','Monthly'))
class Goals(models.Model):
    goal_id = models.AutoField(primary_key=True)
    learner_id = models.ForeignKey(Learners, models.DO_NOTHING)
    goal_type = models.TextField(choices=GOAL_CHOICE, default='Daily')
    goal_description = models.TextField()
    goal_start = models.DateField()
    goal_end = models.DateField()
    goal_is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'goals'


class StudyGroup(models.Model):
    study_group_id = models.AutoField(primary_key=True)
    study_group_name = models.CharField(max_length=255)
    learners = models.ManyToManyField(Learners, related_name='study_groups')
    meet_link_url = models.URLField(max_length=200, null=True, blank=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    topics_focused_on = models.CharField(max_length=255, null=True,blank=True )
    meeting_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.study_group_name