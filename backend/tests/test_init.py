from app import create_app


class TestAppInitialization:
    def test_create_app_returns_app(self):
        app = create_app()
        assert app is not None
        # Verify that at least one known blueprint is registered (e.g. "upload")
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'upload' in blueprint_names
