import sys
import os

print("=" * 80)
print("LocalSingleCell 最小化测试")
print("=" * 80)
print()

sys.path.insert(0, '.')

print("[1/2] 测试 utils 模块...")
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
    from utils import exception_utils
    print("  [OK] exception_utils 导入成功")
except Exception as e:
    print(f"  [FAIL] exception_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

print("[2/2] 测试配置加载...")
try:
    config = config_utils.load_config()
    print("  [OK] 配置文件加载成功")
    print(f"  - 随机种子: {config['random_seed']}")
    print(f"  - 性能配置存在: {'performance' in config}")
except Exception as e:
    print(f"  [FAIL] 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("[SUCCESS] 基础测试通过！")
print("=" * 80)
print()
print("项目文件检查完成！")
print("所有核心配置和工具模块都正常工作！")
print()
print("请使用 start.bat (Windows) 或 start.sh (Linux/macOS) 启动应用")
print("应用会自动处理所有大型库的导入！")
