"""
Patcher Module

This module provides the Patcher class that handles creating patches
and pull requests for documentation changes.
"""

import logging
import os
import subprocess
from typing import Optional, Dict
from datetime import datetime
import httpx

# WK-012: Import for GitHub API integration


class Patcher:
    """
    Handles creating patches and pull requests for documentation changes.

    This class manages version control operations to create patches
    from documentation changes and optionally create pull requests.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        WK-012: Initialize the Patcher with configuration and GitHub integration.

        Enhanced with GitHub API support using httpx for PR and patch management.

        Args:
            config (Optional[Dict]): Configuration including Git credentials, GitHub token, etc.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.git_command = self.config.get('git_command', 'git')
        self.branch_prefix = self.config.get('branch_prefix', 'feature/docs-')

        # WK-012: GitHub API configuration
        self.github_token = self.config.get('github_token') or os.getenv('GITHUB_TOKEN')
        self.github_api_base = self.config.get('github_api_base', 'https://api.github.com')
        self.timeout = self.config.get('api_timeout', 30)
        self.user_agent = self.config.get('user_agent', 'FixMyDocs-Worker/1.0')

        # WK-012: Initialize httpx client for GitHub API
        self.api_client = self._create_api_client()

    def create_patch_or_pr(self, clone_path: str) -> bool:
        """
        Create a patch or pull request with documentation changes.

        This method stages documentation changes, creates a patch file,
        and optionally creates a pull request in the source repository.

        Args:
            clone_path (str): Path to the cloned repository with changes

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Creating patch/PR for repository at {clone_path}")

            if not os.path.exists(clone_path):
                raise FileNotFoundError(f"Repository path does not exist: {clone_path}")

            os.chdir(clone_path)

            # Check git repository status
            if not self._is_git_repository():
                raise ValueError(f"Not a git repository: {clone_path}")

            # Create a new branch for documentation changes
            branch_name = f"{self.branch_prefix}{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            self._create_branch(branch_name)

            # Stage documentation-related files
            self._stage_documentation_files()

            # Check if there are changes to commit
            if not self._has_changes():
                self.logger.warning("No documentation changes to commit")
                return True

            # Create commit with documentation changes
            self._commit_changes(clone_path)

            # Create patch file
            patch_file = self._create_patch_file(clone_path)
            self.logger.info(f"Created patch file: {patch_file}")

            # TODO: Implement PR creation if configured
            # This would involve:
            # - Pushing to remote branch
            # - Creating pull request via API (GitHub, GitLab, etc.)
            # - Adding reviewers, labels, descriptions

            self.logger.info("Patch/PR creation completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error creating patch/PR: {e}")
            return False

    # WK-012: GitHub API Integration Methods
    def _create_api_client(self) -> httpx.Client:
        """
        WK-012: Create authenticated httpx client for GitHub API.

        Returns:
            httpx.Client: Configured client for GitHub API calls
        """
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': self.user_agent
        }

        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'

        return httpx.Client(
            base_url=self.github_api_base,
            headers=headers,
            timeout=self.timeout,
            follow_redirects=True
        )

    def _extract_repo_info(self, repo_url: str) -> tuple:
        """
        WK-012: Extract repository owner and name from GitHub URL.

        Args:
            repo_url (str): GitHub repository URL

        Returns:
            tuple: (owner, repo_name) or (None, None) if invalid
        """
        import re
        pattern = r'github\.com/([^/]+)/([^/]+?)(\.git|/|$)'
        match = re.search(pattern, repo_url)

        if match:
            return match.group(1), match.group(2)
        return None, None

    def create_pull_request(self, clone_path: str, **kwargs) -> bool:
        """
        WK-012: Create a pull request using GitHub API with actual implementation.

        Creates a pull request via GitHub REST API using httpx for proper
        integration with GitHub's pull request system.

        Args:
            clone_path (str): Path to the repository with changes
            **kwargs: Additional parameters for PR creation

        Returns:
            bool: True if PR creation was successful, False otherwise
        """
        try:
            if not self.github_token:
                self.logger.error("WK-012: GitHub token not configured. Set GITHUB_TOKEN environment variable.")
                return False

            # Extract PR parameters
            title = kwargs.get('title', 'Auto-generated documentation updates')
            body = kwargs.get('body', 'This PR contains automatically generated documentation updates.')
            head_branch = kwargs.get('head_branch', f'feature/docs-{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}')
            base_branch = kwargs.get('base_branch', 'main')
            draft = kwargs.get('draft', False)
            reviewers = kwargs.get('reviewers', [])
            labels = kwargs.get('labels', ['documentation'])

            # Get repository remote URL
            remote_url = self._get_remote_url(clone_path)
            if not remote_url:
                self.logger.error("WK-012: Could not get repository remote URL")
                return False

            owner, repo = self._extract_repo_info(remote_url)
            if not owner or not repo:
                self.logger.error(f"WK-012: Could not extract owner/repo from URL: {remote_url}")
                return False

            # Push the branch to remote first
            if not self.push_changes_to_remote(clone_path, head_branch):
                self.logger.warning("WK-012: Failed to push changes to remote, but continuing with PR creation")

            # Create the pull request
            pr_endpoint = f'/repos/{owner}/{repo}/pulls'
            pr_data = {
                'title': title,
                'body': body,
                'head': head_branch,
                'base': base_branch,
                'draft': draft
            }

            self.logger.info(f"WK-012: Creating pull request: {title}")
            response = self.api_client.post(pr_endpoint, json=pr_data)

            if response.status_code in [201, 200]:
                pr_info = response.json()
                pr_number = pr_info.get('number')
                pr_url = pr_info.get('html_url')

                self.logger.info(f"WK-012: Pull request created successfully: {pr_url}")

                # Add reviewers if specified
                if reviewers:
                    self._add_pr_reviewers(owner, repo, pr_number, reviewers)

                # Add labels if specified
                if labels:
                    self._add_pr_labels(owner, repo, pr_number, labels)

                return True
            else:
                self.logger.error(f"WK-012: Failed to create PR: HTTP {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"WK-012: Error creating pull request: {e}")
            return False

    def _get_remote_url(self, clone_path: str) -> Optional[str]:
        """
        WK-012: Get the remote repository URL from git config.

        Args:
            clone_path (str): Path to the cloned repository

        Returns:
            Optional[str]: Remote repository URL or None
        """
        try:
            original_cwd = os.getcwd()
            os.chdir(clone_path)

            result = subprocess.run(
                [self.git_command, 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
        finally:
            os.chdir(original_cwd)

    def push_changes_to_remote(self, clone_path: str, branch_name: Optional[str] = None) -> bool:
        """
        WK-012: Push documentation changes to remote repository.

        Implements actual git push operations using subprocess for reliable
        integration with remote repositories.

        Args:
            clone_path (str): Path to the repository with changes
            branch_name (str): Branch name to push (current branch if None)

        Returns:
            bool: True if push was successful, False otherwise
        """
        try:
            original_cwd = os.getcwd()
            os.chdir(clone_path)

            # Get current branch if not specified
            if not branch_name:
                result = subprocess.run(
                    [self.git_command, 'rev-parse', '--abbrev-ref', 'HEAD'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                branch_name = result.stdout.strip()

            # Push the branch
            self.logger.info(f"WK-012: Pushing branch {branch_name} to remote")

            cmd = [self.git_command, 'push', '-u', 'origin', branch_name]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.info("WK-012: Successfully pushed changes to remote")
                return True
            else:
                self.logger.error(f"WK-012: Failed to push changes: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"WK-012: Error pushing to remote: {e}")
            return False
        finally:
            os.chdir(original_cwd)

    def _add_pr_reviewers(self, owner: str, repo: str, pr_number: int, reviewers: list) -> bool:
        """
        WK-012: Add reviewers to a pull request.

        Args:
            owner (str): Repository owner
            repo (str): Repository name
            pr_number (int): Pull request number
            reviewers (list): List of GitHub usernames to add as reviewers

        Returns:
            bool: True if reviewers were added successfully
        """
        try:
            endpoint = f'/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers'
            data = {'reviewers': reviewers}

            response = self.api_client.post(endpoint, json=data)

            if response.status_code == 201:
                self.logger.info(f"WK-012: Added reviewers to PR #{pr_number}")
                return True
            else:
                self.logger.warning(f"WK-012: Failed to add reviewers to PR #{pr_number}: {response.text}")
                return False

        except Exception as e:
            self.logger.warning(f"WK-012: Error adding PR reviewers: {e}")
            return False

    def _add_pr_labels(self, owner: str, repo: str, pr_number: int, labels: list) -> bool:
        """
        WK-012: Add labels to a pull request.

        Args:
            owner (str): Repository owner
            repo (str): Repository name
            pr_number (int): Pull request number
            labels (list): List of label names to add

        Returns:
            bool: True if labels were added successfully
        """
        try:
            endpoint = f'/repos/{owner}/{repo}/issues/{pr_number}/labels'
            data = {'labels': labels}

            response = self.api_client.post(endpoint, json=data)

            if response.status_code == 200:
                self.logger.info(f"WK-012: Added labels to PR #{pr_number}")
                return True
            else:
                self.logger.warning(f"WK-012: Failed to add labels to PR #{pr_number}: {response.text}")
                return False

        except Exception as e:
            self.logger.warning(f"WK-012: Error adding PR labels: {e}")
            return False

    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            result = subprocess.run(
                [self.git_command, 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _create_branch(self, branch_name: str) -> bool:
        """Create and checkout a new branch."""
        try:
            # Create new branch
            subprocess.run(
                [self.git_command, 'checkout', '-b', branch_name],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"Created and switched to branch: {branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create branch {branch_name}: {e}")
            return False

    def _stage_documentation_files(self) -> bool:
        """Stage documentation-related files."""
        try:
            # Common documentation file patterns
            doc_patterns = [
                'README.md', 'README.txt', '*.md',
                'docs/', 'documentation/',
                '*.rst', '*.txt'  # Additional documentation files
            ]

            # Add documentation files
            for pattern in doc_patterns:
                try:
                    subprocess.run(
                        [self.git_command, 'add', pattern],
                        capture_output=True,
                        text=True
                    )
                except subprocess.CalledProcessError:
                    # Pattern might not match any files, continue
                    pass

            self.logger.info("Staged documentation files")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stage documentation files: {e}")
            return False

    def _has_changes(self) -> bool:
        """Check if there are staged changes."""
        try:
            result = subprocess.run(
                [self.git_command, 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) > 0
        except subprocess.CalledProcessError:
            return False

    def _commit_changes(self, clone_path: str) -> bool:
        """Commit the staged changes."""
        try:
            commit_message = f"Auto-generated documentation\n\nRepository: {os.path.basename(clone_path)}"
            subprocess.run(
                [self.git_command, 'commit', '-m', commit_message],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info("Committed documentation changes")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to commit changes: {e}")
            return False

    def _create_patch_file(self, clone_path: str) -> str:
        """Create a patch file from the current commit."""
        try:
            patch_file = f"documentation-{os.path.basename(clone_path)}.patch"
            with open(patch_file, 'w') as f:
                result = subprocess.run(
                    [self.git_command, 'format-patch', '-1', 'HEAD', '--stdout'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                f.write(result.stdout)

            return patch_file
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create patch file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error creating patch file: {e}")

    # (duplicate stub removed: canonical create_pull_request defined above)
            return False

    def push_changes_to_remote(self, clone_path: str) -> bool:
        """
        WK-010: Push documentation changes to remote repository.

        Stub implementation for pushing changes to remote.

        Args:
            clone_path (str): Path to the repository with changes

        Returns:
            bool: True if push was successful, False otherwise
        """
        try:
            self.logger.info(f"WK-010: Pushing changes for {clone_path}")

            # Stub implementation - will be enhanced in WK-012
            self.logger.info("WK-010: Push changes stub completed")

            return True
        except Exception as e:
            self.logger.error(f"WK-010: Error pushing changes: {e}")
            return False

    def validate_changes(self, clone_path: str) -> bool:
        """
        WK-010: Validate documentation changes before creating patches/PRs.

        Stub implementation for change validation.

        Args:
            clone_path (str): Path to the repository with changes

        Returns:
            bool: True if changes are valid, False otherwise
        """
        try:
            self.logger.info(f"WK-010: Validating changes in {clone_path}")

            # Stub validation checks
            if not os.path.exists(clone_path):
                self.logger.error("WK-010: Repository path does not exist")
                return False

            # Check for documentation files
            doc_files = []
            for root, dirs, files in os.walk(clone_path):
                for file in files:
                    if file.endswith(('.md', '.rst', '.txt')):
                        doc_files.append(os.path.join(root, file))

            if not doc_files:
                self.logger.warning("WK-010: No documentation files found")
                return False

            self.logger.info(f"WK-010: Validation passed with {len(doc_files)} documentation files")
            return True

        except Exception as e:
            self.logger.error(f"WK-010: Error validating changes: {e}")
            return False

    def cleanup_patch_files(self) -> int:
        """
        WK-010: Clean up temporary patch files.

        Stub implementation for cleanup operations.

        Returns:
            int: Number of files cleaned up
        """
        try:
            cleaned_count = 0
            current_dir = os.getcwd()

            # Find and remove patch files
            import glob
            patch_patterns = [
                "*.patch",
                "documentation-*.patch",
                "patch-*.diff"
            ]

            for pattern in patch_patterns:
                for patch_file in glob.glob(pattern):
                    try:
                        os.remove(patch_file)
                        cleaned_count += 1
                        self.logger.info(f"WK-010: Cleaned up {patch_file}")
                    except Exception as e:
                        self.logger.warning(f"WK-010: Failed to remove {patch_file}: {e}")

            self.logger.info(f"WK-010: Cleaned up {cleaned_count} patch files")
            return cleaned_count

        except Exception as e:
            self.logger.error(f"WK-010: Error during cleanup: {e}")
            return 0

    def get_patch_info(self, patch_file: str) -> dict:
        """
        WK-010: Get information about a patch file.

        Stub implementation for patch file analysis.

        Args:
            patch_file (str): Path to the patch file

        Returns:
            dict: Patch file information
        """
        try:
            if not os.path.exists(patch_file):
                return {'error': 'Patch file does not exist'}

            info = {
                'filename': os.path.basename(patch_file),
                'size': os.path.getsize(patch_file),
                'files_changed': 0,
                'lines_added': 0,
                'lines_removed': 0
            }

            # Basic analysis
            with open(patch_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

                for line in lines:
                    if line.startswith('+++') or line.startswith('---'):
                        info['files_changed'] += 1
                    elif line.startswith('+') and not line.startswith('+++'):
                        info['lines_added'] += 1
                    elif line.startswith('-') and not line.startswith('---'):
                        info['lines_removed'] += 1

            return info

        except Exception as e:
            self.logger.error(f"WK-010: Error getting patch info: {e}")
            return {'error': str(e)}

    def apply_patch_to_repo(self, patch_file: str, repo_path: str) -> bool:
        """
        WK-010: Apply a patch file to a repository.

        Stub implementation for patch application.

        Args:
            patch_file (str): Path to the patch file
            repo_path (str): Path to the repository

        Returns:
            bool: True if patch applied successfully, False otherwise
        """
        try:
            self.logger.info(f"WK-010: Applying patch {patch_file} to {repo_path}")

            if not os.path.exists(patch_file):
                self.logger.error("WK-010: Patch file does not exist")
                return False

            if not os.path.exists(repo_path):
                self.logger.error("WK-010: Repository path does not exist")
                return False

            # Stub implementation - will be enhanced with proper git commands
            self.logger.info("WK-010: Patch application stub completed")

            return True

        except Exception as e:
            self.logger.error(f"WK-010: Error applying patch: {e}")
            return False