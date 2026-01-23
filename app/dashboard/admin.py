from django.contrib import admin
from .models import TermsAndConditionsModel,PrivacyAndPolicyModel,PlatformConfigModel,AiAssistantConfigModel
# Register your models here.
admin.site.register(TermsAndConditionsModel)
admin.site.register(PrivacyAndPolicyModel)
admin.site.register(PlatformConfigModel)
admin.site.register(AiAssistantConfigModel)
