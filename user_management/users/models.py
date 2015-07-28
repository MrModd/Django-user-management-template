from django.db import models
from django.conf import settings

# Required for Token authentication:
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.
class ActivationLink(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
	link = models.CharField(max_length=50)
	
	def __unicode__(self):  # Python 3: def __str__(self):
		return 'Activation link for ' + str(self.user)

class PasswordResetLink(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
	link = models.CharField(max_length=50)
	
	def __unicode__(self):  # Python 3: def __str__(self):
		return 'Password reset link for ' + str(self.user)



# Token authentication
# After creating a new user call this function that create a new token for him.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
