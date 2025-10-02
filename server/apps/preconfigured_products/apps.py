from django.apps import AppConfig


class PreconfiguredProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.preconfigured_products'

    def ready(self):
        import apps.preconfigured_products.signals
