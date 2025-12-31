"""Run quick checks to verify environment is safe for production.
Exits with non-zero in the presence of critical misconfigurations.
"""
import os
import sys

errors = []
warnings = []

env = os.environ.get('FLASK_ENV', os.environ.get('ENV', 'production'))
if env == 'development':
    warnings.append('FLASK_ENV=development — ensure you are not running in production')

if os.environ.get('DEBUG', '0').lower() in ('1','true','yes'):
    errors.append('DEBUG is enabled — set DEBUG=0 for production')

if os.environ.get('DEV_SQLITE_FALLBACK', '0').lower() in ('1','true','yes'):
    errors.append('DEV_SQLITE_FALLBACK is enabled — disable this in production')

if os.environ.get('ENABLE_DEBUG_ENDPOINTS', '0').lower() in ('1','true','yes'):
    warnings.append('ENABLE_DEBUG_ENDPOINTS is enabled — ensure only enabled for short-term internal troubleshooting')

if os.environ.get('CORS_ORIGINS', '*') == '*':
    warnings.append('CORS_ORIGINS is set to *; consider specifying allowed origins in production')

if os.environ.get('SECRET_KEY') in (None, '', 'change-me-secret'):
    errors.append('SECRET_KEY is missing or using default value')

if os.environ.get('DATABASE_URL') in (None, '', 'mysql+pymysql://root:password@127.0.0.1:3306/studenthub'):
    warnings.append('DATABASE_URL is not set to a production database')

if errors:
    print('ERRORS:')
    for e in errors:
        print('  -', e)
    sys.exit(2)

if warnings:
    print('WARNINGS:')
    for w in warnings:
        print('  -', w)
    sys.exit(1)

print('All pre-deploy checks passed')
