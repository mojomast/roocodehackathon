import unittest
import os
from unittest.mock import patch, MagicMock
from worker.auth_providers import MockAuthProvider, RealAuthProvider

class TestMockAuthProvider(unittest.TestCase):
    """
    Tests for the MockAuthProvider class.
    """

    def setUp(self):
        self.provider = MockAuthProvider()
        self.url = "https://github.com/user/repo.git"

    def test_prepare_git_auth_config(self):
        """
        Verify that prepare_git_auth_config returns a mock configuration.
        """
        config = self.provider.prepare_git_auth_config(self.url)
        self.assertEqual(config['authenticated_url'], self.url)
        self.assertFalse(config['use_ssh'])
        self.assertFalse(config['use_token'])

    def test_get_access_token(self):
        """
        Verify that get_access_token returns a dummy token.
        """
        token = self.provider.get_access_token(self.url)
        self.assertEqual(token, "mock_token_string")

class TestRealAuthProvider(unittest.TestCase):
    """
    Tests for the RealAuthProvider class.
    """

    def setUp(self):
        self.provider = RealAuthProvider()
        self.github_url = "https://github.com/user/repo.git"
        self.gitlab_url = "https://gitlab.com/user/repo.git"
        self.bitbucket_url = "https://bitbucket.org/user/repo.git"
        self.generic_url = "https://example.com/user/repo.git"

    @patch.dict(os.environ, {"GITHUB_TOKEN": "github_test_token"})
    def test_get_access_token_github(self):
        """
        Test getting a GitHub token from an environment variable.
        """
        token = self.provider.get_access_token(self.github_url)
        self.assertEqual(token, "github_test_token")

    @patch.dict(os.environ, {"GITLAB_TOKEN": "gitlab_test_token"})
    def test_get_access_token_gitlab(self):
        """
        Test getting a GitLab token from an environment variable.
        """
        token = self.provider.get_access_token(self.gitlab_url)
        self.assertEqual(token, "gitlab_test_token")

    @patch.dict(os.environ, {"BITBUCKET_TOKEN": "bitbucket_test_token"})
    def test_get_access_token_bitbucket(self):
        """
        Test getting a Bitbucket token from an environment variable.
        """
        token = self.provider.get_access_token(self.bitbucket_url)
        self.assertEqual(token, "bitbucket_test_token")

    @patch.dict(os.environ, {"GIT_ACCESS_TOKEN": "generic_test_token"})
    def test_get_access_token_generic(self):
        """
        Test getting a generic token from an environment variable.
        """
        token = self.provider.get_access_token(self.generic_url)
        self.assertEqual(token, "generic_test_token")

    def test_get_access_token_no_token(self):
        """
        Test that no token is returned when none is set.
        """
        with patch.dict(os.environ, {}, clear=True):
            token = self.provider.get_access_token(self.github_url)
            self.assertIsNone(token)

    def test_prepare_git_auth_config_no_auth(self):
        """
        Test preparing config with no authentication methods.
        """
        with patch.dict(os.environ, {}, clear=True):
            config = self.provider.prepare_git_auth_config(self.github_url)
            self.assertEqual(config['authenticated_url'], self.github_url)
            self.assertFalse(config['use_ssh'])
            self.assertFalse(config['use_token'])

    @patch.dict(os.environ, {"GITHUB_TOKEN": "github_test_token"})
    def test_prepare_git_auth_config_with_token(self):
        """
        Test preparing config with a token from an environment variable.
        """
        config = self.provider.prepare_git_auth_config(self.github_url)
        self.assertIn("github_test_token@", config['authenticated_url'])
        self.assertTrue(config['use_token'])
        self.assertFalse(config['use_ssh'])

    @patch('os.path.exists', return_value=True)
    @patch.dict(os.environ, {"GIT_SSH_KEY_PATH": "/path/to/ssh_key"})
    def test_prepare_git_auth_config_with_ssh(self, mock_exists):
        """
        Test preparing config with an SSH key.
        """
        config = self.provider.prepare_git_auth_config(self.github_url)
        self.assertTrue(config['use_ssh'])
        self.assertEqual(config['ssh_key_path'], "/path/to/ssh_key")
        self.assertIn('GIT_SSH_COMMAND', config['env'])

    def test_embed_token_in_url(self):
        """
        Test embedding a token into a URL.
        """
        url = "https://github.com/user/repo.git"
        token = "my_secret_token"
        authenticated_url = self.provider._embed_token_in_url(url, token)
        self.assertEqual(authenticated_url, "https://my_secret_token@github.com/user/repo.git")

    def test_embed_token_in_url_with_port(self):
        """
        Test embedding a token into a URL that has a port.
        """
        url = "https://example.com:8080/user/repo.git"
        token = "my_secret_token"
        authenticated_url = self.provider._embed_token_in_url(url, token)
        self.assertEqual(authenticated_url, "https://my_secret_token@example.com:8080/user/repo.git")

    def test_embed_token_in_url_no_token(self):
        """
        Test that the URL is unchanged if no token is provided.
        """
        url = "https://github.com/user/repo.git"
        authenticated_url = self.provider._embed_token_in_url(url, "")
        self.assertEqual(authenticated_url, url)

if __name__ == '__main__':
    unittest.main()