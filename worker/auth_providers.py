"""
Authentication Provider Module

This module defines the interface for authentication providers and includes
implementations for real and mock authentication.
"""

import logging
import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Optional, Dict

class AuthProvider(ABC):
    """
    Abstract base class for authentication providers.
    """

    @abstractmethod
    def prepare_git_auth_config(self, url: str) -> dict:
        """
        Prepare git authentication configuration for cloning.
        """
        pass

    @abstractmethod
    def get_access_token(self, url: str) -> Optional[str]:
        """
        Get personal access token for the repository platform.
        """
        pass

class RealAuthProvider(AuthProvider):
    """
    Provides real authentication logic by fetching credentials from config or environment.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize RealAuthProvider with configuration.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

    def prepare_git_auth_config(self, url: str) -> dict:
        """
        Prepare git authentication configuration for cloning.

        Handles various authentication methods including SSH keys,
        personal access tokens, and credential storage.
        """
        auth_config = {
            'authenticated_url': url,
            'use_ssh': False,
            'use_token': False,
            'env': os.environ.copy()
        }

        try:
            # Check for SSH key configuration
            ssh_key_path = self.config.get('ssh_key_path') or os.getenv('GIT_SSH_KEY_PATH')
            if ssh_key_path and os.path.exists(ssh_key_path):
                self.logger.info("Using SSH key for git authentication")
                auth_config['use_ssh'] = True
                auth_config['ssh_key_path'] = ssh_key_path
                auth_config['env']['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key_path} -o IdentitiesOnly=yes'
                if url.startswith('git@') or url.startswith('ssh://'):
                    auth_config['authenticated_url'] = url
                return auth_config

            # Check for personal access token
            token = self.get_access_token(url)
            if token:
                self.logger.info("Using personal access token for git authentication")
                auth_config['use_token'] = True
                auth_config['authenticated_url'] = self._embed_token_in_url(url, token)
                return auth_config

            # Check for credential helper or stored credentials
            stored_creds = self._get_stored_credentials(url)
            if stored_creds:
                self.logger.info("Using stored credentials for git authentication")
                auth_config['authenticated_url'] = self._embed_token_in_url(url, stored_creds['password'])
                auth_config['use_token'] = True
                return auth_config

            self.logger.info("No authentication configured - proceeding without credentials")
            return auth_config

        except Exception as e:
            self.logger.warning(f"Error preparing git authentication config: {e}")
            return auth_config

    def get_access_token(self, url: str) -> Optional[str]:
        """
        Get personal access token for the repository platform.
        """
        try:
            if 'github.com' in url:
                token = self.config.get('github_token') or os.getenv('GITHUB_TOKEN')
                if token:
                    return token
            elif 'gitlab.com' in url:
                token = self.config.get('gitlab_token') or os.getenv('GITLAB_TOKEN')
                if token:
                    return token
            elif 'bitbucket.org' in url:
                token = self.config.get('bitbucket_token') or os.getenv('BITBUCKET_TOKEN')
                if token:
                    return token

            generic_token = self.config.get('access_token') or os.getenv('GIT_ACCESS_TOKEN')
            if generic_token:
                return generic_token

            return None
        except Exception as e:
            self.logger.warning(f"Error getting access token: {e}")
            return None

    def _embed_token_in_url(self, url: str, token: str) -> str:
        """
        Embed token in repository URL for authentication.
        """
        try:
            if not token or not url.startswith(('https://', 'http://')):
                return url

            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.username or parsed_url.password:
                self.logger.warning("URL already contains user info, not embedding new token.")
                return url

            netloc_with_token = f"{token}@{parsed_url.hostname}"
            if parsed_url.port:
                netloc_with_token += f":{parsed_url.port}"
            
            authenticated_url = parsed_url._replace(netloc=netloc_with_token).geturl()
            return authenticated_url
        except Exception as e:
            self.logger.warning(f"Error embedding token in URL: {e}")
            return url

    def _get_stored_credentials(self, url: str) -> Optional[dict]:
        """
        Get stored git credentials if available.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc
            username = os.getenv(f'GIT_USERNAME_{host.replace(".", "_").upper()}')
            password = os.getenv(f'GIT_PASSWORD_{host.replace(".", "_").upper()}')

            if username and password:
                return {'username': username, 'password': password}
            return None
        except Exception as e:
            self.logger.warning(f"Error getting stored credentials: {e}")
            return None

class MockAuthProvider(AuthProvider):
    """
    Mock authentication provider for testing purposes.
    """

    def prepare_git_auth_config(self, url: str) -> dict:
        """
        Returns a mock authentication configuration.
        """
        return {
            'authenticated_url': url,
            'use_ssh': False,
            'use_token': False,
            'env': os.environ.copy()
        }

    def get_access_token(self, url: str) -> Optional[str]:
        """
        Returns a dummy access token.
        """
        return "mock_token_string"