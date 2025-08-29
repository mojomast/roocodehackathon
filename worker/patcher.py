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


class Patcher:
    """
    Handles creating patches and pull requests for documentation changes.

    This class manages version control operations to create patches
    from documentation changes and optionally create pull requests.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Patcher with configuration.

        Args:
            config (Optional[Dict]): Configuration including Git credentials, etc.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.git_command = self.config.get('git_command', 'git')
        self.branch_prefix = self.config.get('branch_prefix', 'feature/docs-')

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