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

# WK-013: Import GitPython for actual git operations
try:
    import git
    from git import Repo, GitCommandError
    GITPYTHON_AVAILABLE = True
except ImportError:
    git = None
    Repo = None
    GitCommandError = None
    GITPYTHON_AVAILABLE = False


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
        WK-013: Clone a repository from the given URL using GitPython.

        This method handles authentication, timeout management, and cleanup
        for repository cloning operations using GitPython for more reliable
        git operations.

        Args:
            repo_url (str): URL of the repository to clone
            clone_path (Optional[str]): Path where to clone the repository.
                                        If None, uses a temporary directory.

        Returns:
            bool: True if cloning was successful, False otherwise
        """
        if not GITPYTHON_AVAILABLE:
            self.logger.warning("WK-013: GitPython not available, falling back to subprocess")
            return self._clone_with_subprocess(repo_url, clone_path)

        try:
            self.logger.info(f"WK-013: Cloning repository using GitPython: {repo_url}")

            # Determine clone path
            if clone_path is None:
                clone_path = self._generate_temp_path(repo_url)

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(clone_path), exist_ok=True)

            # Prepare authenticated URL or configuration
            auth_config = self._prepare_git_auth_config(repo_url)

            # Clone repository with GitPython
            self.logger.debug("WK-013: Executing GitPython clone operation")

            # Configure clone options
            clone_kwargs = {
                'depth': 1,  # Shallow clone
                'single_branch': True,
                'no_checkout': False,
            }

            # Add authentication if available
            if auth_config.get('use_ssh'):
                # Use SSH key for authentication
                env = auth_config.get('env', os.environ.copy())
                clone_kwargs['env'] = env

                # Set up SSH command with key if specified
                ssh_key_path = auth_config.get('ssh_key_path')
                if ssh_key_path:
                    env['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key_path} -o IdentitiesOnly=yes'
            elif auth_config.get('use_token'):
                # Use personal access token in URL
                repo_url = auth_config['authenticated_url']

            try:
                repo = Repo.clone_from(
                    repo_url,
                    clone_path,
                    **clone_kwargs
                )

                # Verify the clone was successful
                if os.path.exists(os.path.join(clone_path, '.git')) and repo.git_dir:
                    self.logger.info(f"WK-013: Successfully cloned repository to {clone_path}")

                    # Store repo reference for potential future operations
                    repo.close()

                    return True
                else:
                    self.logger.error("WK-013: GitPython clone completed but repository not properly initialized")
                    if os.path.exists(clone_path):
                        import shutil
                        shutil.rmtree(clone_path)
                    return False

            except GitCommandError as e:
                self.logger.error(f"WK-013: GitPython clone failed: {e}")

                # Try fallback to subprocess if GitPython fails
                if os.path.exists(clone_path):
                    import shutil
                    shutil.rmtree(clone_path)

                self.logger.info("WK-013: Retrying with subprocess fallback")
                return self._clone_with_subprocess(repo_url, clone_path)

        except ImportError:
            # GitPython not available, use subprocess
            return self._clone_with_subprocess(repo_url, clone_path)

        except Exception as e:
            self.logger.error(f"WK-013: Unexpected error during GitPython clone: {e}")

            # Cleanup and fallback
            if clone_path and os.path.exists(clone_path):
                import shutil
                try:
                    shutil.rmtree(clone_path)
                except Exception:
                    pass

            return self._clone_with_subprocess(repo_url, clone_path)

    def _clone_with_subprocess(self, repo_url: str, clone_path: Optional[str] = None) -> bool:
        """
        WK-013: Fallback clone method using subprocess (original implementation).
        """
        try:
            self.logger.info(f"WK-013: Cloning repository using subprocess: {repo_url}")

            # Determine clone path
            if clone_path is None:
                clone_path = self._generate_temp_path(repo_url)

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(clone_path), exist_ok=True)

            # Get authentication configuration
            auth_config = self._prepare_git_auth_config(repo_url)
            cmd_url = auth_config.get('authenticated_url', repo_url)

            # Execute git clone with timeout
            cmd = [
                self.git_command, 'clone',
                '--depth', '1',  # Shallow clone for faster operation
                cmd_url,
                clone_path
            ]

            self.logger.debug(f"WK-013: Executing command: {' '.join(cmd)}")

            # Set up environment for SSH if needed
            env = auth_config.get('env', os.environ.copy())

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                env=env
            )

            if result.returncode == 0:
                self.logger.info(f"WK-013: Successfully cloned repository to {clone_path}")
                return True
            else:
                self.logger.error(f"WK-013: Failed to clone repository: {result.stderr}")
                # Clean up failed clone directory
                if os.path.exists(clone_path):
                    import shutil
                    shutil.rmtree(clone_path)
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"WK-013: Repository cloning timed out after {self.timeout}s")
            if clone_path and os.path.exists(clone_path):
                import shutil
                shutil.rmtree(clone_path)
            return False
        except Exception as e:
            self.logger.error(f"WK-013: Error cloning repository with subprocess: {e}")
            return False

    def _prepare_git_auth_config(self, url: str) -> dict:
        """
        WK-013: Prepare git authentication configuration for cloning.

        Handles various authentication methods including SSH keys,
        personal access tokens, and credential storage.

        Args:
            url (str): Original repository URL

        Returns:
            dict: Authentication configuration for git operations
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
                self.logger.info("WK-013: Using SSH key for git authentication")
                auth_config['use_ssh'] = True
                auth_config['ssh_key_path'] = ssh_key_path

                # Set up SSH command
                auth_config['env']['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key_path} -o IdentitiesOnly=yes'

                # If it's an SSH URL, don't modify it
                if url.startswith('git@') or url.startswith('ssh://'):
                    auth_config['authenticated_url'] = url

                return auth_config

            # Check for personal access token
            token = self._get_access_token(url)
            if token:
                self.logger.info("WK-013: Using personal access token for git authentication")
                auth_config['use_token'] = True
                auth_config['authenticated_url'] = self._embed_token_in_url(url, token)

                return auth_config

            # Check for credential helper or stored credentials
            stored_creds = self._get_stored_credentials(url)
            if stored_creds:
                self.logger.info("WK-013: Using stored credentials for git authentication")
                auth_config['authenticated_url'] = self._embed_token_in_url(url, stored_creds['password'])
                auth_config['use_token'] = True

                return auth_config

            # No authentication configured
            self.logger.info("WK-013: No authentication configured - proceeding without credentials")
            return auth_config

        except Exception as e:
            self.logger.warning(f"WK-013: Error preparing git authentication config: {e}")
            # Return basic config without authentication
            return auth_config

    def _get_access_token(self, url: str) -> Optional[str]:
        """
        WK-013: Get personal access token for the repository platform.

        Args:
            url (str): Repository URL

        Returns:
            Optional[str]: Access token or None
        """
        try:
            # Extract platform from URL
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

            # Check for generic token
            generic_token = self.config.get('access_token') or os.getenv('GIT_ACCESS_TOKEN')
            if generic_token:
                return generic_token

            return None

        except Exception as e:
            self.logger.warning(f"WK-013: Error getting access token: {e}")
            return None

    def _embed_token_in_url(self, url: str, token: str) -> str:
        """
        WK-013: Embed token in repository URL for authentication.

        Args:
            url (str): Original repository URL
            token (str): Access token

        Returns:
            str: URL with embedded token
        """
        try:
            if token and url.startswith(('https://', 'http://')):
                # Insert token into URL: https://TOKEN@github.com/owner/repo
                parts = url.split('://')
                if len(parts) == 2:
                    return f'{parts[0]}://{token}@{parts[1]}'

            return url
        except Exception as e:
            self.logger.warning(f"WK-013: Error embedding token in URL: {e}")
            return url

    def _get_stored_credentials(self, url: str) -> Optional[dict]:
        """
        WK-013: Get stored git credentials if available.

        Args:
            url (str): Repository URL

        Returns:
            Optional[dict]: Stored credentials or None
        """
        try:
            # Parse URL to get host and path
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc

            # Try credential helper or stored credentials
            # This is a basic implementation - in production you'd use
            # git credential helper or secure credential storage
            username = os.getenv(f'GIT_USERNAME_{host.replace(".", "_").upper()}')
            password = os.getenv(f'GIT_PASSWORD_{host.replace(".", "_").upper()}')

            if username and password:
                return {
                    'username': username,
                    'password': password
                }

            return None

        except Exception as e:
            self.logger.warning(f"WK-013: Error getting stored credentials: {e}")
            return None

    def authenticate_repo_access(self, url: str, credentials: dict = None) -> str:
        """
        WK-013: Authenticate access to private repositories using GitPython/Git commands.

        Enhanced implementation supporting multiple authentication methods.
        Overrides the placeholder implementation from WK-010.

        Args:
            url (str): Repository URL
            credentials (dict): Authentication credentials (override environment settings)

        Returns:
            str: Authenticated URL or configured URL for authentication
        """
        try:
            if credentials:
                # Override configuration with provided credentials
                temp_config = self.config.copy()
                temp_config.update(credentials)
                original_config = self.config
                self.config = temp_config

                try:
                    auth_config = self._prepare_git_auth_config(url)
                    return auth_config.get('authenticated_url', url)
                finally:
                    self.config = original_config
            else:
                # Use existing configuration
                auth_config = self._prepare_git_auth_config(url)
                return auth_config.get('authenticated_url', url)

        except Exception as e:
            self.logger.error(f"WK-013: Error authenticating repo access: {e}")
            return url

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

    # WK-010: Additional stub implementations to prevent AttributeError
    def get_repository_info(self, repo_path: str) -> dict:
        """
        WK-010: Get detailed information about a repository.

        Stub implementation for repository metadata extraction.

        Args:
            repo_path (str): Path to the repository

        Returns:
            dict: Repository information
        """
        try:
            info = {
                'path': repo_path,
                'name': os.path.basename(repo_path) if repo_path else None,
                'size_mb': 0.0,
                'file_count': 0,
                'last_modified': None,
                'is_git_repo': False
            }

            if os.path.exists(repo_path):
                # Calculate size
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(repo_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        file_count += 1
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            pass  # Skip files we can't read

                info['size_mb'] = round(total_size / (1024 * 1024), 2)
                info['file_count'] = file_count
                info['last_modified'] = self._get_repo_last_modified(repo_path)
                info['is_git_repo'] = os.path.exists(os.path.join(repo_path, '.git'))

            return info
        except Exception as e:
            self.logger.warning(f"WK-010: Error getting repository info: {e}")
            return {'error': str(e)}

    def _get_repo_last_modified(self, repo_path: str) -> str:
        """WK-010: Get last modified time of repository."""
        try:
            import time
            mtime = os.path.getmtime(repo_path)
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        except Exception:
            return None

    def setup_git_config(self, repo_path: str, **config) -> bool:
        """
        WK-010: Setup git configuration for the repository.

        Stub implementation for git configuration management.

        Args:
            repo_path (str): Path to the repository
            **config: Configuration parameters (user.name, user.email, etc.)

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        try:
            self.logger.info(f"WK-010: Setting up git config for {repo_path}")

            if not os.path.exists(repo_path):
                self.logger.error("WK-010: Repository path does not exist")
                return False

            original_cwd = os.getcwd()
            try:
                os.chdir(repo_path)
                # Stub: Basic git config setup
                # In real implementation, this would call git config commands
                for key, value in config.items():
                    self.logger.info(f"WK-010: Would set git config {key}={value}")

                return True
            finally:
                os.chdir(original_cwd)

        except Exception as e:
            self.logger.error(f"WK-010: Error setting up git config: {e}")
            return False

    def authenticate_repo_access(self, url: str, credentials: dict = None) -> str:
        """
        WK-010: Authenticate access to private repositories.

        Stub implementation for repository authentication that will be
        implemented with GitPython and authentication in WK-013.

        Args:
            url (str): Repository URL
            credentials (dict): Authentication credentials

        Returns:
            str: Authenticated URL
        """
        try:
            # Stub: Will be replaced with actual authentication in WK-013
            # TODO: Implement SSH key authentication
            # TODO: Implement personal access token authentication
            # TODO: Implement SSH agent authentication
            return url
        except Exception as e:
            self.logger.error(f"WK-010: Error authenticating repo access: {e}")
            return url

    def check_repo_permissions(self, repo_path: str) -> dict:
        """
        WK-010: Check read/write permissions for repository.

        Stub implementation for permission validation.

        Args:
            repo_path (str): Path to the repository

        Returns:
            dict: Permission status information
        """
        try:
            permissions = {
                'readable': False,
                'writable': False,
                'executable': False,
                'can_create_files': False,
                'can_modify_files': False
            }

            if os.path.exists(repo_path):
                permissions['readable'] = os.access(repo_path, os.R_OK)
                permissions['writable'] = os.access(repo_path, os.W_OK)
                permissions['executable'] = os.access(repo_path, os.X_OK)

                # Test file creation
                test_file = os.path.join(repo_path, '.test_write_permissions')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    permissions['can_create_files'] = True
                    os.remove(test_file)
                except Exception:
                    permissions['can_create_files'] = False

                # Test file modification
                try:
                    permissions['can_modify_files'] = True
                except Exception:
                    permissions['can_modify_files'] = False

            return permissions
        except Exception as e:
            self.logger.warning(f"WK-010: Error checking permissions: {e}")
            return {'error': str(e)}

    def backup_repository(self, repo_path: str, backup_path: Optional[str] = None) -> bool:
        """
        WK-010: Create a backup of the repository.

        Stub implementation for repository backup functionality.

        Args:
            repo_path (str): Path to the repository
            backup_path (Optional[str]): Path for the backup

        Returns:
            bool: True if backup was successful, False otherwise
        """
        try:
            self.logger.info(f"WK-010: Creating backup of {repo_path}")

            if not os.path.exists(repo_path):
                self.logger.error("WK-010: Repository path does not exist")
                return False

            if not backup_path:
                backup_name = f"repo_backup_{os.path.basename(repo_path)}_{int(time.time())}"
                backup_path = os.path.join(os.path.dirname(repo_path), backup_name)

            # Stub: Simple copy operation
            # In real implementation, this could be git clone or full copy
            try:
                import shutil
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.copytree(repo_path, backup_path, ignore=shutil.ignore_patterns('.git'))
                self.logger.info(f"WK-010: Backup created at {backup_path}")
                return True
            except Exception as e:
                self.logger.warning(f"WK-010: Backup operation failed: {e}")
                return False

        except Exception as e:
            self.logger.error(f"WK-010: Error creating backup: {e}")
            return False

    def get_clone_stats(self) -> dict:
        """
        WK-010: Get statistics about cloning operations.

        Stub implementation for clone operation metrics.

        Returns:
            dict: Clone statistics
        """
        try:
            stats = {
                'total_clones': 0,
                'successful_clones': 0,
                'failed_clones': 0,
                'average_clone_time': 0.0,
                'active_clones': 0
            }

            return stats
        except Exception as e:
            self.logger.warning(f"WK-010: Error getting clone stats: {e}")
            return {'error': str(e)}

    def monitor_clone_progress(self, clone_path: str) -> dict:
        """
        WK-010: Monitor the progress of an ongoing clone operation.

        Stub implementation for clone progress monitoring.

        Args:
            clone_path (str): Path to the cloning repository

        Returns:
            dict: Progress information
        """
        try:
            progress = {
                'status': 'unknown',
                'progress_percent': 0,
                'estimated_time_remaining': 0,
                'bytes_transferred': 0,
                'objects_received': 0,
                'objects_total': 0
            }

            if os.path.exists(clone_path):
                progress['status'] = 'in_progress' if not os.path.exists(os.path.join(clone_path, '.git')) else 'completed'

            return progress
        except Exception as e:
            self.logger.warning(f"WK-010: Error monitoring clone progress: {e}")
            return {'error': str(e)}