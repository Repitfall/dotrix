from django.contrib import admin
import api.models as models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username']
