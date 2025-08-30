#!/usr/bin/env python3
"""
Simple test script to output diagnostic information for debugging worker issues.
This will help validate the environment and system setup.
"""

import os
import platform
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_diagnostics():
    """Run diagnostic tests and output information."""

    print("="*80)
    print("WORKER DIAGNOSTIC INFORMATION")
    print("="*80)

    # System information
    print("\n1. SYSTEM INFORMATION:")
    print(f"   Operating System: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"   Platform: {platform.platform()}")
    print(f"   Python Version: {platform.python_version()}")
    try:
        import sys
        print(f"   Python Executable: {sys.executable}")
    except Exception as e:
        print(f"   Python Executable: Unable to determine ({e})")
    print(f"   Current Working Directory: {os.getcwd()}")
    print(f"   Process ID: {os.getpid()}")

    # Environment variables
    print("\n2. ENVIRONMENT VARIABLES:")
    broker_url = os.getenv('CELERY_BROKER_URL')
    backend_url = os.getenv('CELERY_RESULT_BACKEND')
    db_url = os.getenv('DATABASE_URL')

    print(f"   CELERY_BROKER_URL: {broker_url}")
    print(f"   CELERY_RESULT_BACKEND: {backend_url}")
    print(f"   DATABASE_URL: {'***MASKED***' if db_url else None}")

    # Try to import required modules
    print("\n3. MODULE IMPORTS:")

    try:
        import multiprocessing
        print("   ✓ multiprocessing: imported successfully")
        print(f"     CPU count: {multiprocessing.cpu_count()}")
        print(f"     Context: {multiprocessing.get_context()}")
    except ImportError as e:
        print(f"   ✗ multiprocessing: failed - {e}")

    try:
        import celery
        print("   ✓ celery: imported successfully")
        print(f"     Version: {celery.__version__}")
    except ImportError as e:
        print(f"   ✗ celery: failed - {e}")

    try:
        import redis
        print("   ✓ redis: imported successfully")
        print(f"     Version: {redis.__version__}")
    except ImportError as e:
        print(f"   ✗ redis: failed - {e}")

    try:
        import billiard
        print("   ✓ billiard: imported successfully")
        print(f"     Version: {billiard.__version__}")
    except ImportError as e:
        print(f"   ✗ billiard: failed - {e}")

    # Test Redis connection
    print("\n4. REDIS CONNECTIVITY:")
    if broker_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(broker_url)
            if parsed.hostname:
                import redis
                redis_client = redis.Redis(
                    host=parsed.hostname,
                    port=parsed.port or 6379,
                    db=int(parsed.path.lstrip('/')) if parsed.path else 0,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                redis_client.ping()
                print("   ✓ Redis connection test: SUCCESS")
                print(f"     Connected to: {parsed.hostname}:{parsed.port or 6379}")
            else:
                print("   ⚠ Unable to parse Redis URL format")
        except Exception as e:
            print(f"   ✗ Redis connection test: FAILED - {e}")
    else:
        print("   ⚠ CELERY_BROKER_URL not set")

    # Windows-specific checks
    if platform.system() == 'Windows':
        print("\n5. WINDOWS-SPECIFIC CHECKS:")

        # Test multiprocessing lock creation (this often fails on Windows)
        try:
            from multiprocessing import Lock
            lock = Lock()
            lock.acquire(timeout=1)  # Short timeout
            lock.release()
            print("   ✓ Multiprocessing Lock creation: SUCCESS")
        except Exception as e:
            print(f"   ✗ Multiprocessing Lock creation: FAILED - {e}")

        # Check for common Windows multiprocessing issues
        try:
            import billiard
            print("   ✓ Billiard import: SUCCESS")
            # Test billiard pool creation
            try:
                from billiard import Pool
                pool = Pool(processes=1, maxtasksperchild=1)
                result = pool.apply_async(lambda x: x + 1, (1,))
                output = result.get(timeout=5)
                pool.close()
                pool.join()
                print("   ✓ Billiard pool creation and operation: SUCCESS")
            except Exception as e:
                print(f"   ✗ Billiard pool creation/operation: FAILED - {e}")
        except ImportError:
            print("   ⚠ Billiard not available")

    print("\n" + "="*80)
    print("DIAGNOSTIC TEST COMPLETED")
    print("="*80)

if __name__ == '__main__':
    test_diagnostics()