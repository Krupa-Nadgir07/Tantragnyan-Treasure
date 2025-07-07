from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Learners)
admin.site.register(DomainsInterested)
admin.site.register(CpPlatforms)
admin.site.register(LearnerCpAccCreds)
admin.site.register(Topics)
admin.site.register(StrongWeakTopics)