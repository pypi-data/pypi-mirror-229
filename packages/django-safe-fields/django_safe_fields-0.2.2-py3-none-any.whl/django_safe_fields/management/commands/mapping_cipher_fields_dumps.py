import json
from django.apps import apps
from django.core.management.base import BaseCommand
from django_safe_fields.fields import SafeFieldMixinBase


class Command(BaseCommand):
    help = "Dump All Mapping Cipher Fields"

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--name", help="Dump mapping cipher fields to the variable..."
        )

    def handle(self, *args, **options):
        name = options.get("name", None)
        infos = {}
        for app_label, models in apps.all_models.items():
            for model_name, model in models.items():
                for field in model._meta.fields:
                    if isinstance(field, SafeFieldMixinBase):
                        cipher = getattr(field, "cipher")
                        if cipher:
                            cipher_instance = getattr(cipher, "cipher_instance", None)
                            if cipher_instance and hasattr(cipher_instance, "dumps"):
                                cipher_seeds = cipher_instance.dumps()
                                infos[str(field)] = cipher_seeds
        text = json.dumps(infos, indent=4, ensure_ascii=True, sort_keys=True)
        if name:
            print(name, "=", text)
        else:
            print(text)
