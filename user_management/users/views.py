from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

import django.contrib.auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework import permissions
import json

from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from users.models import ActivationLink, PasswordResetLink



def generateLink():
	chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
	return get_random_string(50, chars)



def sendRegistrationLink(request, user):
	subject = 'Activation link'
	from_email = 'No Reply <' + settings.EMAIL_HOST_USER + '>'
	
	link = generateLink()
	while ActivationLink.objects.filter(link=link).exists():
		link = generateLink()
	linkobj, created = ActivationLink.objects.get_or_create(user=user)
	linkobj.link = link
	linkobj.save()
	
	url = request.build_absolute_uri(reverse('users:activation'))
	url += '?key=' + link
	
	message = 'Dear ' + user.username + ',\n'
	message += 'thanks for your registration.\n'
	message += 'Please use next link in order to activate your account.\n'
	message += url + '\n'
	message += 'If you can\'t follow the link, just copy the url and paste it in the browser.\n\n'
	message += 'If you didn\'t requested a new account just ignore this email.'
	
	html_message = '<p>Dear ' + user.username + ',<br />'
	html_message += 'thanks for your registration.<br />'
	html_message += 'Please use next link in order to activate your account.<br />'
	html_message += '<a href="' + url + '">' + url + '</a><br />'
	html_message += 'If you can\'t follow the link, just copy the url and paste it in the browser.</p>'
	html_message += '<p>If you didn\'t requested a new account just ignore this email.</p>'
	
	mail = send_mail(subject, message, from_email, [user.email], fail_silently=settings.DEBUG, html_message=html_message)



def sendPasswordResetLink(request, user):
	subject = 'Password reset link'
	from_email = 'No Reply <' + settings.EMAIL_HOST_USER + '>'
	
	link = generateLink()
	while PasswordResetLink.objects.filter(link=link).exists():
		link = generateLink()
	linkobj, created = PasswordResetLink.objects.get_or_create(user=user)
	linkobj.link = link
	linkobj.save()
	
	url = request.build_absolute_uri(reverse('users:password'))
	url += '?key=' + link
	
	message = 'Dear ' + user.username + ',\n'
	message += 'you requested a password reset.\n'
	message += 'Please use next link in order to reactivate your account.\n'
	message += url + '\n'
	message += 'If you can\'t follow the link, just copy the url and paste it in the browser.'
	
	html_message = '<p>Dear ' + user.username + ',<br />'
	html_message += 'you requested a password reset.<br />'
	html_message += 'Please use next link in order to reactivate your account.<br />'
	html_message += '<a href="' + url + '">' + url + '</a><br />'
	html_message += 'If you can\'t follow the link, just copy the url and paste it in the browser.</p>'
	
	mail = send_mail(subject, message, from_email, [user.email], fail_silently=settings.DEBUG, html_message=html_message)



# Access control views

@login_required
def index(request):
	return render(request, 'users/home.html', {'user': request.user})



def register(request):
	if request.method == 'GET':
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		else:
			return render(request, 'users/register.html', {'page': '1'})
	
	if request.method == 'POST':
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		
		# Get new user credentials from POST
		newusername = request.POST['newusername']
		newpassword1 = request.POST['newpassword1']
		newpassword2 = request.POST['newpassword2']
		newemail = request.POST['newemail']
		newfirstname = request.POST['newfirstname']
		newlastname = request.POST['newlastname']
		
		# Check if passwords fields match
		if newpassword1 != newpassword2:
			content = {
						'username': newusername,
						'email': newemail,
						'firstname': newfirstname,
						'lastname': newlastname,
						'error_message': 'Passwords mismatch',
						'page': '1'
			}
			return render(request, 'users/register.html', content)
		
		# Check if user already exists
		newuser = get_user_model().objects.filter(username=newusername)
		if newuser:
			content = {
						'email': newemail,
						'firstname': newfirstname,
						'lastname': newlastname,
						'error_message': 'This user already exists',
						'page': '1'
			}
			return render(request, 'users/register.html', content)
		
		# Check if email already exists
		newuser = get_user_model().objects.filter(email=newemail)
		if newuser:
			content = {
						'username': newusername,
						'firstname': newfirstname,
						'lastname': newlastname,
						'error_message': 'This email is already taken',
						'page': '1'
			}
			return render(request, 'users/register.html', content)
		
		### Start user creation ###
		
		# Create new User in the system
		newuser = get_user_model().objects.create_user(newusername, newemail, newpassword1)
		newuser.first_name = newfirstname
		newuser.last_name = newlastname
		newuser.email = newemail
		newuser.is_staff = False
		newuser.is_superuser = False
		newuser.is_active = False
		newuser.save()
		
		# Send activation link by email
		sendRegistrationLink(request, newuser)
		
		return render(request, 'users/register.html', {'page': '2'})



def activation(request):
	if request.method == 'GET':
		key = request.GET.get('key', '')
		if key:
			activation = get_object_or_404(ActivationLink, link=key)
			user = activation.user
			user.is_active = True
			user.save()
			
			activation.delete()
			
			if request.user.is_authenticated():
				django.contrib.auth.logout(request)
			
			return render(request, 'users/login.html', {'confirm_message': 'Your account is now active'})
		
		if request.user.is_authenticated():
			# If user is authenticated, it is also active
			return HttpResponseRedirect(reverse('users:index'))
		else:
			return render(request, 'users/activation.html')
		
	if request.method == 'POST':
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		
		# Get user email from POST
		email = request.POST['email']
		
		# Find user object
		try:
			user = get_user_model().objects.get(email=email)
			if not user.is_active:
				sendRegistrationLink(request, user)
		except get_user_model().DoesNotExist:
			pass
		
		return render(request, 'users/activation.html', {'confirm_message': 'Email sent'})



def resetPassword(request):
	if request.method == 'GET':
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		
		return render(request, 'users/reset_password.html')
	
	if request.method == 'POST':
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		
		username = request.POST.get('username', '')
		email = request.POST.get('email', '')
		
		if not username and not email:
			return render(request, 'users/reset_password.html', {'error_message': 'Fill at least one field'})
		
		if username:
			try:
				user = get_user_model().objects.get(username=username)
			except get_user_model().DoesNotExist:
				pass
		else:
			try:
				user = get_user_model().objects.get(email=email)
			except get_user_model().DoesNotExist:
				pass
		
		if user:
			sendPasswordResetLink(request, user)
		
		return render(request, 'users/reset_password.html', {'confirm_message': 'Email sent'})
	



def changePassword(request):
	if request.method == 'GET':
		key = request.GET.get('key', '')
		
		if not key and request.user.is_authenticated():
			content = {
						'user': request.user,
						'username': request.user.username
			}
			return render(request, 'users/change_password.html', content)
		
		passwordReset = get_object_or_404(PasswordResetLink, link=key)
		user = passwordReset.user
		
		if request.user.is_authenticated():
			django.contrib.auth.logout(request)
		
		content = {
					'username': user.username,
					'key': key
		}
		return render(request, 'users/change_password.html', content)
		
	if request.method == 'POST':
		
		key = request.POST.get('key', '')
		
		if key and request.user.is_authenticated():
			django.contrib.auth.logout(request)
		
		if request.user.is_authenticated() or key:
			# Get fields from POST
			if request.user.is_authenticated():
				password = request.POST['password']
			newpassword1 = request.POST['newpassword1']
			newpassword2 = request.POST['newpassword2']
			
			# Check old password
			if request.user.is_authenticated():
				user = django.contrib.auth.authenticate(username=request.user.username, password=password)
				if user is None:
					content = {
								'user': request.user,
								'username': request.user.username,
								'error_message': 'Invalid password'
					}
					return render(request, 'users/change_password.html', content)
			else:
				passwordReset = get_object_or_404(PasswordResetLink, link=key)
				user = passwordReset.user
			
			# Check new password
			if newpassword1 != newpassword2:
				content = {
							'user': request.user,
							'username': request.user.username,
							'error_message': 'Passwords are different'
				}
				return render(request, 'users/change_password.html', content)
			
			# Update password
			if request.user.is_authenticated():
				django.contrib.auth.logout(request)
			else:
				passwordReset.delete()
			user.set_password(newpassword1)
			user.save()
			
			return render(request, 'users/login.html', {'confirm_message': 'Password changed'})
			
		else:
			raise Http404

@login_required
def delete(request):
	if request.method == 'GET':
		return render(request, 'users/delete.html', {'user': request.user})
	
	if request.method == 'POST':
		if request.user.is_superuser:
			return render(request, 'users/delete.html', {'user': request.user})
		
		password = request.POST['password']
		user = django.contrib.auth.authenticate(username=request.user.username, password=password)
		if user is None:
			content = {
						'user': request.user,
						'error_message': 'Invalid password'
			}
			return render(request, 'users/delete.html', content)
		
		django.contrib.auth.logout(request)
		
		# Delete user
		user.delete()
		
		return HttpResponseRedirect(reverse('users:index'))



@login_required
def update(request):
	if request.method == 'GET':
		content = {
					'user': request.user,
					'username': request.user.username,
					'email': request.user.email,
					'firstname': request.user.first_name,
					'lastname': request.user.last_name,
					'page': '2'
		}
		return render(request, 'users/update.html', content)
	
	if request.method == 'POST':
		email = request.POST['email']
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		
		if firstname != request.user.first_name:
			request.user.first_name = firstname
		if lastname != request.user.last_name:
			request.user.last_name = lastname
		if email and email != request.user.email:
			request.user.email = email
		
		request.user.save()
		
		content = {
					'user': request.user,
					'username': request.user.username,
					'email': request.user.email,
					'firstname': request.user.first_name,
					'lastname': request.user.last_name,
					'page': '2',
					'confirm_message': 'Updated!'
		}
		return render(request, 'users/update.html', content)



@login_required
def adminUpdate(request):
	if request.method == 'GET':
		
		# Only superuser can update other users
		if not request.user.is_superuser:
			return HttpResponseRedirect(reverse('users:index'))
		
		# Print a list of users
		userlist = get_user_model().objects.filter(is_superuser=False).values_list('username', flat=True).order_by('username')
		content = {
					'user': request.user,
					'userlist': userlist,
					'page': '1'
		}
		return render(request, 'users/admin_update.html', content)
	
	if request.method == 'POST':
		
		# Only superuser can update other users
		if not request.user.is_superuser:
			return HttpResponseRedirect(reverse('users:index'))
		
		# Get action
		action = request.POST['action']
		
		if action == 'next':
			
			# User has just been selected, show all his informations
			username = request.POST['users']
			
			try:
				user = get_user_model().objects.get(username=username)
			except get_user_model().DoesNotExist:
				# Wrong POST has been done! Return on the first page
				userlist = get_user_model().objects.filter(is_superuser=False).values_list('username', flat=True).order_by('username')
				
				content = {
							'user': request.user,
							'userlist': userlist,
							'page': '1',
							'error_message': 'Invalid user'
				}
				return render(request, 'users/admin_update.html', content)
			
			# Show new page
			content = {
						'user': request.user,
						'username': user.username,
						'email': user.email,
						'firstname': user.first_name,
						'lastname': user.last_name,
						'enabled': user.is_active,
						'page': '2'
			}
			return render(request, 'users/admin_update.html', content)
		
		else:
			
			# We are on page 2
			username = request.POST['username']
			email = request.POST['email']
			firstname = request.POST['firstname']
			lastname = request.POST['lastname']
			
			try:
				user = get_user_model().objects.get(username=username)
			except get_user_model().DoesNotExist:
				# Wrong POST has been done! Return on the first page
				userlist = get_user_model().objects.filter(is_superuser=False).values_list('username', flat=True).order_by('username')
				content = {
							'user': request.user,
							'userlist': userlist,
							'page': '1',
							'error_message': 'Invalid user'
				}
				return render(request, 'users/admin_update.html', content)
			
			if action == 'activate':
				user.is_active = True
				user.save()
				
				# Delete any activation link
				activation = ActivationLink.objects.filter(user=user)
				if activation:
					activation.delete()
				passwordReset = PasswordResetLink.objects.filter(user=user)
				if passwordReset:
					passwordReset.delete()
				
				# Remain on the same page and show a confirmation message
				content = {
							'user': request.user,
							'username': user.username,
							'email': user.email,
							'firstname': user.first_name,
							'lastname': user.last_name,
							'enabled': user.is_active,
							'page': '2',
							'confirm_message': 'Activated'
				}
				return render(request, 'users/admin_update.html', content)
			
			if action == 'delete':
				user.delete()
				
				# Return on the first page with a confirmation message
				userlist = get_user_model().objects.filter(is_superuser=False).values_list('username', flat=True).order_by('username')
				content = {
							'user': request.user,
							'userlist': userlist,
							'page': '1',
							'confirm_message': 'Account removed'
				}
				return render(request, 'users/admin_update.html', content)
			
			if action == 'update':
				if firstname != user.first_name:
					user.first_name = firstname
				if lastname != user.last_name:
					user.last_name = lastname
				if email and email != user.email:
					user.email = email
				
				user.save()
				
				# Remain on the same page and show a confirmation message
				content = {
							'user': request.user,
							'username': user.username,
							'email': user.email,
							'firstname': user.first_name,
							'lastname': user.last_name,
							'enabled': user.is_active,
							'page': '2',
							'confirm_message': 'Updated'
				}
				return render(request, 'users/admin_update.html', content)



# System wide views

def login(request):
	if request.method == 'GET':
		if request.user.is_authenticated():
			return HttpResponseRedirect(reverse('users:index'))
		else:
			nexturl = request.GET.get('next', '')
			return render(request, 'users/login.html', {'next': nexturl})
	
	elif request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		nexturl = request.POST.get('next', '')
		
		user = django.contrib.auth.authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				# Registered user
				
				# Delete any activation link
				activation = ActivationLink.objects.filter(user=user)
				if activation:
					activation.delete()
				
				passwordReset = PasswordResetLink.objects.filter(user=user)
				if passwordReset:
					passwordReset.delete()
				
				# Log user in
				django.contrib.auth.login(request, user)
				if nexturl:
					return HttpResponseRedirect(nexturl)
				else:
					return HttpResponseRedirect(reverse('users:index'))
					
			else:
				
				# Inactive user
				return render(request, 'users/login.html', {'error_message': 'Your account is inactive!'})
				
		else:
			
			# Invalid credential
			content = {
						'error_message': 'Invalid credentials!',
						'username': username
			}
			return render(request, 'users/login.html', content)



def logout(request):
	if request.user.is_authenticated():
		django.contrib.auth.logout(request)
		
	return render(request, 'users/logout.html')


# REST interface view
class tokenRenewREST(APIView):
	
	permission_classes = (permissions.IsAuthenticated,)
	# Disable browseable API renderer (just to make things similar to get-token API)
	renderer_classes = [JSONRenderer]
	
	def post(self, request, format=None):
		token, created =  Token.objects.get_or_create(user=request.user)
		
		if not created:
			token.delete()
			token = Token.objects.create(user=request.user)
		
		response_data = {'token': token.key}
		return HttpResponse(json.dumps(response_data), content_type="application/json")
