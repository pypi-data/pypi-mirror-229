from django.apps import apps
from django.core.management.base import BaseCommand
from django_safe_fields.fields import SafeFieldMixinBase


class Command(BaseCommand):
    help = "List All Safe Fields"

    def handle(self, *args, **options):
        for app_label, models in apps.all_models.items():
            for model_name, model in models.items():
                for field in model._meta.fields:
                    if isinstance(field, SafeFieldMixinBase):
                        print(
                            "{}\t{}\t{}".format(
                                field.__class__.__name__,
                                field.cipher.__class__.__name__,
                                field,
                            )
                        )
