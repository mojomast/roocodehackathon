"""
Repository Manager Module

This module provides the RepoManager class that handles repository
cloning, authentication, and version control operations.
"""

import logging
import os
import subprocess
from typing import Optional, Dict
import urllib.parse


class RepoManager:
    """
    Manages repository operations including cloning, authentication, and cleanup.

    This class handles various repository types (Git, GitHub, GitLab, etc.)
    and provides secure authentication methods.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize RepoManager with configuration.

        Args:
            config (Optional[Dict]): Configuration including credentials, timeouts, etc.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.timeout = self.config.get('clone_timeout', 300)  # 5 minutes default
        self.git_command = self.config.get('git_command', 'git')
        self.temp_dir = self.config.get('temp_dir', '/tmp/repos')

        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)

    def clone_repo(self, repo_url: str, clone_path: Optional[str] = None) -> bool:
        """
        Clone a repository from the given URL.

        This method handles authentication, timeout management, and cleanup
        for repository cloning operations.

        Args:
            repo_url (str): URL of the repository to clone
            clone_path (Optional[str]): Path where to clone the repository.
                                       If None, uses a temporary directory.

        Returns:
            bool: True if cloning was successful, False otherwise
        """
        try:
            self.logger.info(f"Cloning repository: {repo_url}")

            # Determine clone path
            if clone_path is None:
                clone_path = self._generate_temp_path(repo_url)

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(clone_path), exist_ok=True)

            # Prepare authenticated URL if needed
            authenticated_url = self._prepare_authenticated_url(repo_url)

            # Execute git clone with timeout
            cmd = [
                self.git_command, 'clone',
                '--depth', '1',  # Shallow clone for faster operation
                authenticated_url,
                clone_path
            ]

            self.logger.debug(f"Executing command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False
            )

            if result.returncode == 0:
                self.logger.info(f"Successfully cloned repository to {clone_path}")
                return True
            else:
                self.logger.error(f"Failed to clone repository: {result.stderr}")
                # Clean up failed clone directory
                if os.path.exists(clone_path):
                    import shutil
                    shutil.rmtree(clone_path)
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Repository cloning timed out after {self.timeout}s")
            if clone_path and os.path.exists(clone_path):
                import shutil
                shutil.rmtree(clone_path)
            return False
        except Exception as e:
            self.logger.error(f"Error cloning repository: {e}")
            return False

    def _prepare_authenticated_url(self, url: str) -> str:
        """
        Prepare authenticated URL if credentials are configured.

        Args:
            url (str): Original repository URL

        Returns:
            str: URL with authentication credentials embedded
        """
        # TODO: Implement secure authentication methods
        # This should handle:
        # - Personal Access Tokens (GitHub/GitLab)
        # - SSH keys
        # - Environment variables
        # - Secure credential storage

        return url  # Return original URL for now

    def _generate_temp_path(self, repo_url: str) -> str:
        """
        Generate a temporary path for repository cloning.

        Args:
            repo_url (str): Repository URL to generate path for

        Returns:
            str: Temporary path for cloning
        """
        # Extract repository name from URL
        parsed = urllib.parse.urlparse(repo_url)
        repo_name = os.path.basename(parsed.path).replace('.git', '')

        import hashlib
        import time
        # Create unique hash based on URL and timestamp
        url_hash = hashlib.md5(f"{repo_url}-{time.time()}".encode()).hexdigest()[:8]

        return os.path.join(self.temp_dir, f"{repo_name}-{url_hash}")

    def cleanup_temp_repos(self, keep_last_n: int = 5) -> int:
        """
        Clean up old temporary repositories to save disk space.

        Args:
            keep_last_n (int): Number of most recent repos to keep

        Returns:
            int: Number of repositories cleaned up
        """
        try:
            if not os.path.exists(self.temp_dir):
                return 0

            # Get list of temp directories with modification times
            temp_repos = []
            for item in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, item)
                if os.path.isdir(item_path):
                    mtime = os.path.getmtime(item_path)
                    temp_repos.append((item_path, mtime))

            # Sort by modification time (newest first)
            temp_repos.sort(key=lambda x: x[1], reverse=True)

            # Remove older repositories
            cleaned_count = 0
            for repo_path, _ in temp_repos[keep_last_n:]:
                try:
                    import shutil
                    shutil.rmtree(repo_path)
                    cleaned_count += 1
                    self.logger.info(f"Cleaned up temp repository: {repo_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean up {repo_path}: {e}")

            self.logger.info(f"Cleaned up {cleaned_count} temporary repositories")
            return cleaned_count

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0

    def validate_repository(self, repo_path: str) -> Dict:
        """
        Validate that a cloned repository is usable.

        Args:
            repo_path (str): Path to cloned repository

        Returns:
            Dict: Validation results with status and details
        """
        try:
            if not os.path.exists(repo_path):
                return {
                    'valid': False,
                    'error': 'Repository path does not exist'
                }

            # Check if it's a git repository
            if not os.path.exists(os.path.join(repo_path, '.git')):
                return {
                    'valid': False,
                    'error': 'Not a git repository'
                }

            # Check for source files
            source_files = []
            for root, dirs, dirs[:] in os.walk(repo_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in os.listdir(root):
                    if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs')):
                        source_files.append(os.path.join(root, file))

            return {
                'valid': True,
                'source_files_count': len(source_files),
                'has_readme': os.path.exists(os.path.join(repo_path, 'README.md'))
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }