from django.contrib import admin
from .models import *
from .forms import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'profile_picture','date_of_birth','location','user_type')
    search_fields = ('user__username',)
    form = UserProfileForm

    def user(self, obj):
        return obj.user.username
    


admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Grade)
