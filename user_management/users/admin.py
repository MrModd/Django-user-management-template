from django.contrib import admin
from users import models

# Register your models here.

class ActivationLinkAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,			{'fields': ['user', 'link']}),
	]
	
	readonly_fields = ['user', 'link']
	
	list_display = ['pk', 'user', 'link']
	search_fields = ['pk', 'user', 'link']
	ordering = ['user']

admin.site.register(models.ActivationLink, ActivationLinkAdmin)



class PasswordResetLinkAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,			{'fields': ['user', 'link']}),
	]
	
	readonly_fields = ['user', 'link']
	
	list_display = ['pk', 'user', 'link']
	search_fields = ['pk', 'user', 'link']
	ordering = ['user']

admin.site.register(models.PasswordResetLink, PasswordResetLinkAdmin)
