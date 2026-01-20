from django.db import models
from django_prose_editor.fields import ProseEditorField
from django.conf import settings

class TermsAndConditionsModel(models.Model):
    content = ProseEditorField(
        extensions={
            # Core text formatting
            "Bold": True,
            "Italic": True,
            "Strike": True,
            "Underline": True,
            "HardBreak": True,

            # Structure
            "Heading": {
                "levels": [1, 2, 3,4,5,6]
            },
            "BulletList": True,
            "OrderedList": True,
            "ListItem": True,
            "Blockquote": True,

            # Advanced extensions
            "Link": {
                "enableTarget": True,
                "protocols": ["http", "https", "mailto"],
            },
            "Table": True,
            "TableRow": True,
            "TableHeader": True,
            "TableCell": True,

            # Editor capabilities
            "History": True,
            "HTML": True, 
            "Typographic": True,
        },
        sanitize=True 
    )
    
class PrivacyAndPolicyModel(models.Model):
    content = ProseEditorField(
        extensions={
            # Core text formatting
            "Bold": True,
            "Italic": True,
            "Strike": True,
            "Underline": True,
            "HardBreak": True,

            # Structure
            "Heading": {
                "levels": [1, 2, 3,4,5,6]
            },
            "BulletList": True,
            "OrderedList": True,
            "ListItem": True,
            "Blockquote": True,

            # Advanced extensions
            "Link": {
                "enableTarget": True,
                "protocols": ["http", "https", "mailto"],
            },
            "Table": True,
            "TableRow": True,
            "TableHeader": True,
            "TableCell": True,

            # Editor capabilities
            "History": True,
            "HTML": True, 
            "Typographic": True,
        },
        sanitize=True 
    )
    
    
class PlatformConfigModel(models.Model):
    platform_name = models.CharField(max_length=100,blank=True,null=True)
    contact_email = models.EmailField(null=True,blank=True)
    support_email = models.EmailField(null=True,blank=True)

    def __str__(self):
        return f"{self.platform_name}"
    
class AiAssistantConfigModel(models.Model):
    assistant_name = models.Model()
    ai_behaviour_settings = models.Model()

    def __str__(self):
        return f"{self.assistant_name}"