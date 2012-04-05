import os
import fnmatch
import datetime

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse

from sgrstats.settings import SIGNATURE_IMAGES_PATH, SIGNATURE_IMAGES_URL

from django.contrib.auth.models import User
from sgrstats.stats.models import UserProfile
from sgrstats.stats.views import get_player_objectives

from forms import SettingsForm

from core.views import update_online_users

@login_required
@update_online_users
def settings(request):
	return render_to_response('accounts/settings.html', {}, context_instance = RequestContext(request))
 
@login_required 
def update_settings(request):
	if request.method == 'POST':
		form = SettingsForm(request.POST)
		
		if form.is_valid():
			show_on_rankings = form.cleaned_data['show_on_rankings']
			
			user = UserProfile.objects.get(user = request.user)
			if show_on_rankings:
				user.show_on_rankings = True
			else:
				user.show_on_rankings = False
			
			user.save()
			
			messages.add_message(request, messages.SUCCESS, 'Your profile has been successfully updated.')
		else:
			messages.add_message(request, messages.ERROR, message = 'Error occured when trying to update your settings.')
		
	return render_to_response('other/message.html', {}, context_instance = RequestContext(request))

@login_required
def link_account(request, account_id):
	player_stats = get_player_objectives(request, account_id)
	redirect_to = request.REQUEST.get('next', '')

	# Account with this ID doesn't exist
	if not player_stats:
		messages.add_message(request, messages.ERROR, 'Player with this ID does not exist!')
		
		return HttpResponseRedirect(reverse('account_settings'))
		
	user_profile = UserProfile.objects.get(user = request.user)
	user_profile.account_id = int(account_id)
	user_profile.save()
	
	if redirect_to:
		return HttpResponseRedirect(redirect_to)
	
	messages.add_message(request, messages.SUCCESS, 'Your website account <strong>%s</strong> has been successfully linked to a FireSky account with account id <strong>%s</strong>' % (request.user.username, account_id)) 
	return HttpResponseRedirect(reverse('account_settings'))

@login_required
def unlink_account(request):
	user_profile = UserProfile.objects.get(user = request.user)
	redirect_to = request.REQUEST.get('next', '')

	# No FireSky account is linked with this website account
	if not user_profile.account_id:
		messages.add_message(request, messages.ERROR, 'You have no FireSky account linked to this website account!')
		
		return HttpResponseRedirect(reverse('account_settings'))
	
	account_id = user_profile.account_id
	user_profile.account_id = None
	user_profile.save()
	
	if redirect_to:
		return HttpResponseRedirect(redirect_to)
	
	messages.add_message(request, messages.SUCCESS, 'FireSky account with account id <strong>%s</strong> has been successfully unlinked from your website account (<strong>%s</strong>)' % (account_id, request.user.username)) 
	return HttpResponseRedirect(reverse('account_settings'))

@login_required
def link_form(request):
	return render_to_response('accounts/link_account_form.html', {}, context_instance = RequestContext(request))

@login_required
@update_online_users
def signature_images(request):
	user = User.objects.get(pk = request.user.id)
	user_profile = UserProfile.objects.get(user = user)
	
	account_id = user_profile.account_id
	dynamic_signature_status = user_profile.dynamic_signature
	
	if not account_id or not dynamic_signature_status:
		messages.add_message(request, messages.ERROR, 'You have no FireSky account linked to your profile or signature image generation is disabled')
		
		return HttpResponseRedirect(reverse('account_settings'))
	
	available_templates = get_available_templates()
	if available_templates:
		available_signatures = get_available_signature_images_for_account_id(available_templates, account_id)
	else:
		available_signatures = None

	return render_to_response('accounts/signature_images.html', {'available_templates': available_templates, 'available_signatures': available_signatures, 'images_url': SIGNATURE_IMAGES_URL}, context_instance = RequestContext(request))

@login_required
@update_online_users
def signature_image_details(request, template_name):
	user = User.objects.get(pk = request.user.id)
	user_profile = UserProfile.objects.get(user = user)
	
	account_id = user_profile.account_id
	dynamic_signature_status = user_profile.dynamic_signature
	
	if not account_id or not dynamic_signature_status:
		raise Http404()
	
	available_templates = get_available_templates()
	available_templates_names = [os.path.split(template)[1] for template in  available_templates]
	
	if not template_name in available_templates_names:
		raise Http404()
	
	signature_exists = signature_image_exists(template_name, account_id)
	
	if not signature_exists:
		raise Http404()
	
	signature_path = get_signature_image_name_for_template_name_and_account_id(template_name, account_id)
	
	return render_to_response('accounts/signature_image_details.html',  {'template': template_name, 'signature_path': signature_path, 'images_url': SIGNATURE_IMAGES_URL}, context_instance = RequestContext(request))

@login_required
@update_online_users
def dynamic_signature(request, status = 'enable'):
	user = User.objects.get(pk = request.user.id)
	user_profile = UserProfile.objects.get(user = user)
	account_id = user.get_profile().account_id
	dynamic_signature = user.get_profile().dynamic_signature
	
	if status == 'enable':	
		if dynamic_signature == 1:
			messages.add_message(request, messages.ERROR, 'Dynamic signature image generation is not disabled!')
		else:
			user_profile.dynamic_signature = True
			messages.add_message(request, messages.SUCCESS, 'You have successfully enabled dynamic signature image generation.')
	elif status == 'disable':
		if dynamic_signature == 1:
			user_profile.dynamic_signature = False
			messages.add_message(request, messages.SUCCESS, 'You have successfully disabled dynamic signature image generation.')
		else:
			messages.add_message(request, messages.ERROR, 'Dynamic signature image generation is not enabled!')
	
	user_profile.save()
	
	return HttpResponseRedirect(reverse('account_settings'))

# helper functions
def get_available_templates():
	""" Returns available signature templates. """
	
	templates = [os.path.join(SIGNATURE_IMAGES_PATH, file) for file in os.listdir(SIGNATURE_IMAGES_PATH) if os.path.isdir(os.path.join(SIGNATURE_IMAGES_PATH, file))]
	
	return templates

def get_available_signature_images_for_account_id(available_templates, account_id):
	""" Returns all the available signature images for the given account id. """
	
	signature_list = []
	pattern = '%s*' % account_id
	for template in available_templates:
		for root, dirs, files in os.walk(template):
			
			signatures = fnmatch.filter(files, pattern)
			if signatures:
				template_title = os.path.split(template)
				template_path = os.path.join(template_title[1], signatures[0]).replace('\\', '/')
				signature_extension = os.path.splitext(template_path)[1]
				
				signature_list.append((template_title[1], template_path, signature_extension))
				
	return signature_list

def get_signature_image_name_for_template_name_and_account_id(template_name, account_id):
	""" Returns signature image url (template name + account id +  template extension). """

	pattern = '%s*' % account_id
	for root, dirs, files in os.walk(os.path.join(SIGNATURE_IMAGES_PATH, template_name)):
		
		signatures = fnmatch.filter(files, pattern)
		if signatures:
			template_path = os.path.join(template_name, signatures[0]).replace('\\', '/')
			
			return template_path
			
	return None
	
def signature_image_exists(template, account_id):
	""" Check if the signature image for a given template exists for specified account id. """

	pattern = '%s*' % account_id
	path = os.path.join(SIGNATURE_IMAGES_PATH, template)
	for root, dirs, files in os.walk(path):
		if fnmatch.filter(files, pattern):
			return True

		return False