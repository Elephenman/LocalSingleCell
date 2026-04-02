import sys
sys.path.insert(0, '.')
print('Testing imports...')

try:
    from utils import config_utils, logger_utils, visual_utils, exception_utils, validator_utils
    print('utils modules imported OK')
except Exception as e:
    print(f'Error importing utils: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from core import data_loader, qc_filter, analysis_pipeline, visualization, enrichment, downsampling
    print('core modules imported OK')
except Exception as e:
    print(f'Error importing core: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('All imports successful!')
