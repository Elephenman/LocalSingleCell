import sys
import os

print("=" * 80)
print("LocalSingleCell 快速测试 (不包含大型库)")
print("=" * 80)
print()

sys.path.insert(0, '.')

# 测试1: utils模块
print("[1/5] 测试utils模块...")
try:
    from utils import config_utils
    print("  [OK] config_utils 导入成功")
except Exception as e:
    print(f"  [FAIL] config_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import logger_utils
    print("  [OK] logger_utils 导入成功")
except Exception as e:
    print(f"  [FAIL] logger_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import visual_utils
    print("  [OK] visual_utils 导入成功")
except Exception as e:
    print(f"  [FAIL] visual_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import exception_utils
    print("  [OK] exception_utils 导入成功")
except Exception as e:
    print(f"  [FAIL] exception_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import validator_utils
    print("  [OK] validator_utils 导入成功")
except Exception as e:
    print(f"  [FAIL] validator_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试2: core基础模块 (不包含scanpy)
print("[2/5] 测试core基础模块...")
try:
    from core import data_loader
    print("  [OK] data_loader 导入成功")
except Exception as e:
    print(f"  [FAIL] data_loader 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from core import qc_filter
    print("  [OK] qc_filter 导入成功")
except Exception as e:
    print(f"  [FAIL] qc_filter 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试3: downsampling模块
print("[3/5] 测试downsampling模块...")
try:
    # 先测试单独导入psutil
    import psutil
    print("  [OK] psutil 导入成功")
    
    from core import downsampling
    print("  [OK] downsampling 导入成功")
except Exception as e:
    print(f"  [FAIL] downsampling 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试4: 配置加载
print("[4/5] 测试配置加载...")
try:
    config = config_utils.load_config()
    print("  [OK] 配置文件加载成功")
    print(f"  - 随机种子: {config['random_seed']}")
    print(f"  - 性能配置: {config.get('performance', 'Not found')}")
except Exception as e:
    print(f"  [FAIL] 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试5: UI模块
print("[5/5] 测试UI模块...")
try:
    from ui import home_page
    print("  [OK] home_page 导入成功")
except Exception as e:
    print(f"  [FAIL] home_page 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ui import data_import_page
    print("  [OK] data_import_page 导入成功")
except Exception as e:
    print(f"  [FAIL] data_import_page 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("[SUCCESS] 所有快速测试通过！")
print("=" * 80)
print()
print("说明：")
print("- 此测试不包含scanpy等大型科学计算库")
print("- 导入scanpy等库需要较长时间，这是正常的")
print("- 您的电脑配置较低，导入大型库会更慢")
