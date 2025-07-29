#!/usr/bin/env python3
"""
Pytest plugin for comprehensive test cleanup mechanisms.

This plugin provides automatic cleanup for test users, processes, and other
resources, ensuring clean state between tests and proper cleanup even when
tests fail unexpectedly.
"""

import pytest
import logging
import os
import signal
import psutil
from typing import Set, Dict, Any, Optional

from .user_manager import TestUserManager, create_test_user_manager


class CleanupPlugin:
    """
    Pytest plugin for managing test cleanup operations.
    
    Handles cleanup of:
    - Test users and database state
    - Running processes (pexpect, etc.)
    - Temporary files and resources
    - Environment variables
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_manager: Optional[TestUserManager] = None
        self.tracked_processes: Set[int] = set()
        self.temp_files: Set[str] = set()
        self.original_env: Dict[str, str] = {}
        self.cleanup_hooks = []
        
    def pytest_configure(self, config):
        """Configure the cleanup plugin."""
        # Initialize user manager for session-level cleanup
        try:
            self.user_manager = create_test_user_manager(environment="local")
            self.logger.info("Cleanup plugin configured successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize cleanup plugin: {e}")
    
    def pytest_sessionstart(self, session):
        """Session start - set up initial state tracking."""
        # Store original environment variables
        self.original_env = os.environ.copy()
        
        # Track initial processes to avoid killing system processes
        try:
            current_processes = set(p.pid for p in psutil.process_iter())
            self.logger.debug(f"Initial process count: {len(current_processes)}")
        except Exception as e:
            self.logger.warning(f"Failed to enumerate initial processes: {e}")
    
    def pytest_runtest_setup(self, item):
        """Before each test - prepare for tracking."""
        # Clear per-test tracking
        self.tracked_processes.clear()
        self.temp_files.clear()
        
        # Track processes started during test
        try:
            test_start_processes = set(p.pid for p in psutil.process_iter() 
                                     if 'python' in p.name().lower() or 'pexpect' in ' '.join(p.cmdline()))
            self.tracked_processes.update(test_start_processes)
        except Exception:
            pass
    
    def pytest_runtest_teardown(self, item, nextitem):
        """After each test - perform cleanup."""
        self._cleanup_test_processes()
        self._cleanup_temp_files()
        self._reset_environment_variables()
        
        # Run any registered cleanup hooks
        for hook in self.cleanup_hooks:
            try:
                hook()
            except Exception as e:
                self.logger.warning(f"Cleanup hook failed: {e}")
    
    def pytest_runtest_makereport(self, item, call):
        """Generate test report and handle failures."""
        if call.when == "call":
            # Test execution phase
            if call.excinfo is not None:
                # Test failed - perform emergency cleanup
                self.logger.warning(f"Test {item.name} failed, performing emergency cleanup")
                self._emergency_cleanup()
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Session end - perform final cleanup."""
        self._session_cleanup()
        
        if exitstatus != 0:
            self.logger.warning("Test session ended with errors, performing comprehensive cleanup")
            self._emergency_cleanup()
    
    def _cleanup_test_processes(self):
        """Clean up processes started during tests."""
        cleanup_count = 0
        
        try:
            current_processes = list(psutil.process_iter())
            
            for process in current_processes:
                try:
                    # Look for test-related processes
                    if (process.pid in self.tracked_processes or
                        self._is_test_process(process)):
                        
                        self.logger.debug(f"Terminating test process: {process.pid} ({process.name()})")
                        
                        # Try graceful termination first
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            # Force kill if graceful termination failed
                            process.kill()
                            process.wait(timeout=2)
                        
                        cleanup_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process already gone or inaccessible
                    continue
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup process {process.pid}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error during process cleanup: {e}")
        
        if cleanup_count > 0:
            self.logger.info(f"Cleaned up {cleanup_count} test processes")
    
    def _is_test_process(self, process) -> bool:
        """Determine if a process is test-related."""
        try:
            name = process.name().lower()
            cmdline = ' '.join(process.cmdline()).lower()
            
            # Check for test-related indicators
            test_indicators = [
                'pytest',
                'python -m pytest',
                'pexpect',
                'mathsfun',
                'main.py',
                'test_',
                'automation'
            ]
            
            return any(indicator in name or indicator in cmdline 
                      for indicator in test_indicators)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return False
    
    def _cleanup_temp_files(self):
        """Clean up temporary files created during tests."""
        cleanup_count = 0
        
        for file_path in self.temp_files.copy():
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path, ignore_errors=True)
                    cleanup_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
            
        self.temp_files.clear()
        
        if cleanup_count > 0:
            self.logger.debug(f"Cleaned up {cleanup_count} temporary files")
    
    def _reset_environment_variables(self):
        """Reset environment variables to original state."""
        # Remove test-specific environment variables
        test_env_vars = [
            'MATHSFUN_TEST_MODE',
            'PYTEST_CURRENT_TEST'
        ]
        
        for var in test_env_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Note: We don't restore all original env vars as some changes
        # might be intentional and persistent across tests
    
    def _emergency_cleanup(self):
        """Perform emergency cleanup after test failures."""
        self.logger.info("Performing emergency cleanup")
        
        # Aggressive process cleanup
        try:
            for process in psutil.process_iter():
                try:
                    if self._is_test_process(process):
                        self.logger.warning(f"Emergency kill: {process.pid} ({process.name()})")
                        process.kill()
                except Exception:
                    continue
        except Exception as e:
            self.logger.error(f"Emergency process cleanup failed: {e}")
        
        # User cleanup
        if self.user_manager:
            try:
                cleanup_count = self.user_manager.cleanup_session_users()
                if cleanup_count > 0:
                    self.logger.info(f"Emergency cleanup: removed {cleanup_count} test users")
            except Exception as e:
                self.logger.error(f"Emergency user cleanup failed: {e}")
    
    def _session_cleanup(self):
        """Perform session-level cleanup."""
        self.logger.info("Performing session cleanup")
        
        # Final user cleanup
        if self.user_manager:
            try:
                cleanup_count = self.user_manager.cleanup_session_users()
                if cleanup_count > 0:
                    self.logger.info(f"Session cleanup: removed {cleanup_count} test users")
            except Exception as e:
                self.logger.error(f"Session user cleanup failed: {e}")
        
        # Final process cleanup
        self._cleanup_test_processes()
    
    def register_cleanup_hook(self, cleanup_func):
        """Register a custom cleanup function."""
        self.cleanup_hooks.append(cleanup_func)
    
    def track_temp_file(self, file_path: str):
        """Track a temporary file for cleanup."""
        self.temp_files.add(file_path)
    
    def track_process(self, pid: int):
        """Track a process for cleanup."""
        self.tracked_processes.add(pid)


# Global plugin instance
cleanup_plugin = CleanupPlugin()


def pytest_configure(config):
    """Configure pytest with the cleanup plugin."""
    cleanup_plugin.pytest_configure(config)


def pytest_sessionstart(session):
    """Session start hook."""
    cleanup_plugin.pytest_sessionstart(session)


def pytest_runtest_setup(item):
    """Test setup hook."""
    cleanup_plugin.pytest_runtest_setup(item)


def pytest_runtest_teardown(item, nextitem):
    """Test teardown hook."""
    cleanup_plugin.pytest_runtest_teardown(item, nextitem)


def pytest_runtest_makereport(item, call):
    """Test report hook."""
    cleanup_plugin.pytest_runtest_makereport(item, call)


def pytest_sessionfinish(session, exitstatus):
    """Session finish hook."""
    cleanup_plugin.pytest_sessionfinish(session, exitstatus)


# Utility functions for tests to use
def register_cleanup_hook(cleanup_func):
    """Register a custom cleanup hook for the current test session."""
    cleanup_plugin.register_cleanup_hook(cleanup_func)


def track_temp_file(file_path: str):
    """Track a temporary file for automatic cleanup."""
    cleanup_plugin.track_temp_file(file_path)


def track_process(pid: int):
    """Track a process for automatic cleanup."""
    cleanup_plugin.track_process(pid)


@pytest.fixture(scope="function")
def cleanup_tracker():
    """
    Fixture providing access to cleanup tracking functionality.
    
    Returns:
        Object with methods to track resources for cleanup
    """
    class CleanupTracker:
        def track_file(self, file_path: str):
            track_temp_file(file_path)
        
        def track_process(self, pid: int):
            track_process(pid)
        
        def register_hook(self, cleanup_func):
            register_cleanup_hook(cleanup_func)
    
    return CleanupTracker()


@pytest.fixture(scope="session", autouse=True)
def enable_comprehensive_cleanup():
    """
    Session-scoped fixture that enables comprehensive cleanup.
    
    This fixture automatically enables the cleanup plugin for all tests
    in the session, ensuring proper resource management.
    """
    # The cleanup plugin is automatically configured via pytest hooks
    # This fixture just serves as documentation and can be used to
    # customize cleanup behavior if needed
    
    yield
    
    # Final cleanup happens in pytest_sessionfinish hook