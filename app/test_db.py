from flask_testing import TestCase

from exeter_treasure_hunt import app


class DBTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        # Default port is 5000
        app.config['LIVESERVER_PORT'] = 8943
        # Default timeout is 5 seconds
        app.config['LIVESERVER_TIMEOUT'] = 10

        return app

    def test_app_exists(self):
        self.assertIsNotNone(app)

    def test_app_in_test_mode(self):
        self.assertTrue(app.config['TESTING'])