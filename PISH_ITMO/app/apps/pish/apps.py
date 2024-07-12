from django.apps import AppConfig


class PishConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.apps.pish"

    def ready(self) -> None:
        # Without this import, admin panel will not include this app
        from app.apps.pish.web import admin  # noqa: F401 (unused-import)
