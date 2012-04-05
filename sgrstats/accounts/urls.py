from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^settings/dynamic_signature/(?P<status>(enable|disable))', 'accounts.views.dynamic_signature', name = 'account_dynamic_signature'),
    url(r'^settings/signature_images/(?P<template_name>.+?)/', 'accounts.views.signature_image_details', name = 'account_signature_image_details'),
    url(r'^settings/signature_images/', 'accounts.views.signature_images', name = 'account_signature_images'),
     url(r'^link_account/(?P<account_id>\d+)/', 'accounts.views.link_account', name = 'account_link_account'),
    url(r'^unlink_account/', 'accounts.views.unlink_account', name = 'account_unlink_account'),
    url(r'^settings/link_account_form/', 'accounts.views.link_form', name = 'account_link_form'),
    url(r'^settings/update/', 'accounts.views.update_settings', name = 'account_settings_update'),
    url(r'^settings/', 'accounts.views.settings', name = 'account_settings'),
)
