from django import forms
from registration.backends.default import DefaultBackend
from registration.forms import RegistrationForm
from captcha.fields import CaptchaField

class CaptchaRegistrationForm(RegistrationForm):
	captcha = CaptchaField()

class CaptchaRegistrationBackend(DefaultBackend):
	def get_form_class(self, request):
		return CaptchaRegistrationForm

class SettingsForm(forms.Form):
	show_on_rankings = forms.BooleanField(required = False)