from import_export import resources
from .models import Terms

class TermsResource(resources.ModelResource):
    class Meta:
        model = Terms