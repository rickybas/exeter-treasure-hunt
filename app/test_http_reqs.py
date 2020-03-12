import argparse
import json
import sys
import unittest
from getpass import getpass

from flask_testing import TestCase

from exeter_treasure_hunt import app

admin_password = None

class HTTPTest(TestCase):

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

    # static pages -----------------------------------------------------------------------------------------------------

    def test_landing_page(self):
        response = self.client.get("/landing-page")

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('landing_page.html')

    def test_gdpr_policy_page(self):
        response = self.client.get("/gdpr-policy")

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('gdpr_policy.html')

    def test_about_page(self):
        response = self.client.get("/about")

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('about.html')

    # Player auth pages ------------------------------------------------------------------------------------------------

    def test_index_page_without_session(self):
        response = self.client.get('/', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('landing_page.html')

    def test_index_page_with_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/')

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('index.html')

    def test_login_page_get(self):
        response = self.client.get('/login')

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_login_page_post_login_successful(self):
        response = self.client.post('/login', follow_redirects=True,
                                    data = dict(username="admin", password=admin_password, consent="consent"))

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('index.html')

    def test_login_page_post_login_unsuccessful(self):
        response = self.client.post('/login', follow_redirects=True,
                                    data = dict(username="admin", password="blah", consent="consent"))

        self.assertEqual(response.status_code, 401)
        self.assert_template_used('login.html')

        response = self.client.post('/login', follow_redirects=True,
                                    data = dict(username="blah", password="blah", consent="consent"))

        self.assertEqual(response.status_code, 401)
        self.assert_template_used('login.html')

    def test_card_page_with_session(self):
        # user doesn't own card
        with open('app/db/cards.json', 'r') as f:
            cards_dict = json.load(f)

        locations = []
        for card in cards_dict:
            locations.append(card['location'])

        for location in locations:
            with app.test_client() as c:
                with c.session_transaction() as sess:
                    sess['loggedin'] = True
                    sess['username'] = "admin"
                    sess['password'] = admin_password

                response = c.get('/card/' + location)

            self.assertEqual(response.status_code, 200)

        # location name not found
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/card/' + "randomlocationname")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'location not found')

    def test_help_requests_page_without_session(self):
        response = self.client.get('/my-help-requests', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_help_requests_page_with_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/my-help-requests')

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('my_help_requests.html')

    def test_add_help_request_without_session(self):
        response = self.client.get('/add-help-request', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_add_help_request_with_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/add-help-request')

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('add_help_request.html')

        # post with description
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.post('/add-help-request',
                              data = dict(description="blah"), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('my_help_requests.html')

        # post without description
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.post('/add-help-request',
                              data = dict())

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('add_help_request.html')

    # AJAX -------------------------------------------------------------------------------------------------------------

    def test_scores_view_without_session(self):
        response = self.client.get('/scores', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_scores_view_with_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/scores')

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('scores.html')

    def test_map_view_without_session(self):
        response = self.client.get('/map', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_map_view_with_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/map')

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('map.html')

    def test_cards_view_without_session(self):
        response = self.client.get('/cards', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_cards_view_with_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/cards')

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('cards.html')

    def test_loadcards_without_session(self):
        response = self.client.get('/loadcards', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_loadcards_with_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/loadcards')

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual("", response.data)

    def test_is_answer_correct_without_session(self):
        response = self.client.post('/is-answer-correct', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')

    def test_is_answer_correct_with_session(self):
        with open('app/db/cards.json', 'r') as f:
            cards_dict = json.load(f)

        # correct answers
        for card in cards_dict:
            with app.test_client() as c:
                with c.session_transaction() as sess:
                    sess['loggedin'] = True
                    sess['username'] = "admin"
                    sess['password'] = admin_password

                response = c.post('/is-answer-correct', data = dict(location=card['location'], answer=card['correctAnswer']))

            self.assertEqual(response.status_code, 200)
            self.assertTrue(b'Correct' in response.data or response.data == b'YOU HAVE WON')

        # location not found
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.post('/is-answer-correct', data = dict(location="Library", answer="b"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'location not found', response.data)

        # answer incorrect
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.post('/is-answer-correct', data = dict(location="The Library", answer="a"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'Incorrect', response.data)

        # answer already done
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.post('/is-answer-correct', data = dict(location="The Library", answer="b"))
            response = c.post('/is-answer-correct', data = dict(location="The Library", answer="b"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'Correct but already won card', response.data)

    # # IN PROGRESS
    # # def test_open_help_request_page_without_session(self):
    # #     response = self.client.get('/open-help-request/0', follow_redirects=True)
    # #
    # #     self.assertEqual(response.status_code, 200)
    # #     self.assert_template_used('login.html')
    # #
    # # def test_open_help_request_page_with_session(self):
    # #     # no help reqs
    # #     with app.test_client() as c:
    # #         with c.session_transaction() as sess:
    # #             sess['loggedin'] = True
    # #             sess['username'] = "admin"
    # #             sess['password'] = admin_password
    # #
    # #         response = c.get('/open-help-request/0', follow_redirects=True)
    # #
    # #     self.assertEqual(response.status_code, 404)
    # #     self.assertEqual( b'does not exist', response.data)
    # #
    # #     # a single help req
    # #     with app.test_client() as c:
    # #         with c.session_transaction() as sess:
    # #             sess['loggedin'] = True
    # #             sess['username'] = "admin"
    # #             sess['password'] = admin_password
    # #
    # #         response = c.post('/add-help-request',
    # #                           data = dict(description="blah"), follow_redirects=True)
    # #
    # #         response = c.get('/open-help-request/0', follow_redirects=True)
    # #
    # #     self.assertEqual(response.status_code, 200)
    # #     self.assert_template_used('my_help_requests.html')
    # #
    # #     # can't test admin user because dynamic password
    # #
    # # def test_close_help_request_page_without_session(self):
    # #     response = self.client.get('/close-help-request/0', follow_redirects=True)
    # #
    # #     self.assertEqual(response.status_code, 200)
    # #     self.assert_template_used('login.html')
    # #
    # # def test_close_help_request_page_with_session(self):
    # #     # regular user
    # #     with app.test_client() as c:
    # #         with c.session_transaction() as sess:
    # #             sess['loggedin'] = True
    # #             sess['username'] = "admin"
    # #             sess['password'] = admin_password
    # #
    # #         response = c.get('/close-help-requests/0', follow_redirects=True)
    # #
    # #     self.assertEqual(response.status_code, 200)
    # #     self.assert_template_used('my_help_requests.html')

    def test_admin_index_page_without_session(self):
        response = self.client.get('/admin-index', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('admin_login.html')

    def test_admin_index_page_with_session(self):
        pass
        # can't test admin because admin password is dynamically created

    def test_admin_map_page_without_session(self):
        response = self.client.get('/admin-index', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('admin_login.html')

    def test_admin_map_page_with_session(self):
        pass
        # can't test admin because admin password is dynamically created

    def test_admin_users_page_without_session(self):
        response = self.client.get('/admin-users', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('admin_login.html')

    def test_admin_users_page_with_session(self):
        pass
        # can't test admin because admin password is dynamically created

    def test_admin_help_requests_page_without_session(self):
        response = self.client.get('/admin-help-requests', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('admin_login.html')

    def test_admin_help_requests_page_with_session(self):
        pass
        # can't test admin because admin password is dynamically created

    def test_generate_report_page_without_session(self):
        response = self.client.get('/generate-report', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('admin_login.html')

    def test_generate_report_page_with_session(self):
        pass
        # can't test admin because admin password is dynamically created


    # Ending functions -------------------------------------------------------------------------------------------------

    def test_logout(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/logout', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('landing_page.html')

    def test_reset(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['loggedin'] = True
                sess['username'] = "admin"
                sess['password'] = admin_password

            response = c.get('/reset', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('index.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dbhost", type=str,
                        help="mysql host name e.g db or localhost", required=False, default="localhost")
    parser.add_argument("-u", "--dbuser", type=str,
                        help="mysql username, ie root", required=False, default="root")
    parser.add_argument("-p", "--dbpassword", type=str,
                        help="root password for db", required=False, default="")
    parser.add_argument("-n", "--dbname", type=str,
                        help="mysql database name, ie ETH_DATABASE", required=False, default="ETH_DATABASE")
    parser.add_argument("-t", "--port", type=str,
                        help="mysql port", required=False, default="3306")
    parser.add_argument("-q", "--adminpass", type=str,
                        help="admin password for db", required=False, default="")

    args = parser.parse_args()

    # Database config
    app.config['MYSQL_HOST'] = args.dbhost
    app.config['MYSQL_PASSWORD'] = args.dbpassword
    app.config['MYSQL_PORT'] = int(args.port)
    app.config['MYSQL_USER'] = args.dbuser
    app.config['MYSQL_DB'] = args.dbname

    # if user hasn't entered a password in command line
    if args.dbpassword == "":
        password = getpass("Enter root@" + args.dbhost + " password: ")
        app.config['MYSQL_PASSWORD'] = password
    else:
        app.config['MYSQL_PASSWORD'] = args.dbpassword

    # if user hasn't entered a password in command line
    if args.adminpass == "":
        admin_password = getpass("Enter admin password: ").encode('utf-8')
    else:
        admin_password = args.adminpass.encode('utf-8')

    unittest.main(argv=[sys.argv[0]])
