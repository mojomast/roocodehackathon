"""
Configuration Module

This module provides the Config class for centralized configuration
management in the documentation generation system.
"""

import os
from typing import Dict, Any, Optional
import logging


class Config:
    """
    Centralized configuration management for the documentation generation system.

    This class handles loading configuration from environment variables,
    configuration files, and provides default values for all settings.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize Config with values from environment or config file.

        Args:
            config_file (Optional[str]): Path to configuration file (future feature)
        """
        self.logger = logging.getLogger(__name__)
        self._config = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables and set defaults."""
        # Database configuration
        self._config['database_url'] = os.getenv('DATABASE_URL')

        # Celery configuration
        self._config['celery_broker_url'] = os.getenv(
            'CELERY_BROKER_URL',
            'redis://redis:6379/0'
        )
        self._config['celery_result_backend'] = os.getenv(
            'CELERY_RESULT_BACKEND',
            'redis://redis:6379/0'
        )

        # Repository management
        self._config['temp_dir'] = os.getenv('TEMP_DIR', '/tmp/repos')
        self._config['clone_timeout'] = int(os.getenv('CLONE_TIMEOUT', '300'))

        # AI/LLM configuration (placeholders for future AI integration)
        self._config['ai_model'] = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        self._config['ai_temperature'] = float(os.getenv('AI_TEMPERATURE', '0.1'))
        self._config['ai_max_tokens'] = int(os.getenv('AI_MAX_TOKENS', '2048'))

        # Logging configuration
        self._config['log_level'] = os.getenv('LOG_LEVEL', 'INFO').upper()
        self._config['log_file'] = os.getenv('LOG_FILE', 'worker.log')

        # Security configuration
        self._config['enable_auth'] = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'
        self._config['secret_key'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')

        # Performance configuration
        self._config['max_concurrent_jobs'] = int(os.getenv('MAX_CONCURRENT_JOBS', '3'))
        self._config['job_timeout'] = int(os.getenv('JOB_TIMEOUT', '3600'))  # 1 hour

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key (str): Configuration key
            default (Any): Default value if key not found

        Returns:
            Any: Configuration value or default
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key (str): Configuration key
            value (Any): Value to set
        """
        self._config[key] = value
        self.logger.debug(f"Configuration updated: {key} = {value}")

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dict[str, Any]: All configuration values
        """
        return self._config.copy()

    def validate_required(self) -> bool:
        """
        Validate that all required configuration is present.

        Returns:
            bool: True if all required config is present, False otherwise
        """
        required_keys = ['database_url']
        missing = []

        for key in required_keys:
            if not self.get(key):
                missing.append(key)

        if missing:
            self.logger.error(f"Missing required configuration: {', '.join(missing)}")
            return False

        return True

    def get_database_url(self) -> str:
        """Get database URL."""
        return self.get('database_url', '')

    def get_celery_config(self) -> Dict[str, str]:
        """Get Celery configuration."""
        return {
            'broker_url': self.get('celery_broker_url'),
            'result_backend': self.get('celery_result_backend')
        }

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'

    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'level': self.get('log_level'),
            'file': self.get('log_file'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }

    def get_ai_config(self) -> Dict[str, Any]:
        """WK-015: Get AI/LLM configuration."""
        return {
            'model': self.get('ai_model'),
            'temperature': self.get('ai_temperature'),
            'max_tokens': self.get('ai_max_tokens')
        }

    def get_security_config(self) -> Dict[str, Any]:
        """WK-015: Get security configuration."""
        return {
            'enable_auth': self.get('enable_auth'),
            'secret_key': self.get('secret_key')
        }

    def get_performance_config(self) -> Dict[str, Any]:
        """WK-015: Get performance configuration."""
        return {
            'max_concurrent_jobs': self.get('max_concurrent_jobs'),
            'job_timeout': self.get('job_timeout')
        }

    def get_repo_config(self) -> Dict[str, Any]:
        """WK-015: Get repository management configuration."""
        return {
            'temp_dir': self.get('temp_dir'),
            'clone_timeout': self.get('clone_timeout')
        }

    def reload(self) -> None:
        """Reload configuration from environment variables."""
        old_config = self._config.copy()
        self._load_config()

        # Log changes
        changes = []
        for key, new_value in self._config.items():
            old_value = old_config.get(key)
            if old_value != new_value:
                changes.append(f"{key}: {old_value} -> {new_value}")

        if changes:
            self.logger.info("Configuration reloaded with changes:")
            for change in changes:
                self.logger.info(f"  {change}")