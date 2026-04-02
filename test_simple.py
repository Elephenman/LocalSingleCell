import sys
import os

print("=" * 80)
print("LocalSingleCell 简单导入测试")
print("=" * 80)
print()

sys.path.insert(0, '.')

# 测试1: 基础模块
print("[1/8] 测试基础模块导入...")
try:
    import yaml
    print("  ✓ yaml 导入成功")
except Exception as e:
    print(f"  ✗ yaml 导入失败: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"  ✓ numpy 导入成功 (版本: {np.__version__})")
except Exception as e:
    print(f"  ✗ numpy 导入失败: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print(f"  ✓ pandas 导入成功 (版本: {pd.__version__})")
except Exception as e:
    print(f"  ✗ pandas 导入失败: {e}")
    sys.exit(1)

print()

# 测试2: utils模块
print("[2/8] 测试utils模块...")
try:
    from utils import config_utils
    print("  ✓ config_utils 导入成功")
except Exception as e:
    print(f"  ✗ config_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import logger_utils
    print("  ✓ logger_utils 导入成功")
except Exception as e:
    print(f"  ✗ logger_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import visual_utils
    print("  ✓ visual_utils 导入成功")
except Exception as e:
    print(f"  ✗ visual_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import exception_utils
    print("  ✓ exception_utils 导入成功")
except Exception as e:
    print(f"  ✗ exception_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from utils import validator_utils
    print("  ✓ validator_utils 导入成功")
except Exception as e:
    print(f"  ✗ validator_utils 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试3: Streamlit
print("[3/8] 测试Streamlit...")
try:
    import streamlit as st
    print(f"  ✓ streamlit 导入成功 (版本: {st.__version__})")
except Exception as e:
    print(f"  ✗ streamlit 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试4: Scanpy (可能比较慢)
print("[4/8] 测试Scanpy (可能需要一些时间)...")
try:
    import scanpy as sc
    print(f"  ✓ scanpy 导入成功 (版本: {sc.__version__})")
except Exception as e:
    print(f"  ✗ scanpy 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试5: core基础模块
print("[5/8] 测试core基础模块...")
try:
    from core import data_loader
    print("  ✓ data_loader 导入成功")
except Exception as e:
    print(f"  ✗ data_loader 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from core import qc_filter
    print("  ✓ qc_filter 导入成功")
except Exception as e:
    print(f"  ✗ qc_filter 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试6: downsampling模块
print("[6/8] 测试downsampling模块...")
try:
    from core import downsampling
    print("  ✓ downsampling 导入成功")
except Exception as e:
    print(f"  ✗ downsampling 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试7: 可视化模块
print("[7/8] 测试可视化模块...")
try:
    from core import visualization
    print("  ✓ visualization 导入成功")
except Exception as e:
    print(f"  ✗ visualization 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from core import enrichment
    print("  ✓ enrichment 导入成功")
except Exception as e:
    print(f"  ✗ enrichment 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试8: 配置加载
print("[8/8] 测试配置加载...")
try:
    config = config_utils.load_config()
    print("  ✓ 配置文件加载成功")
    print(f"  - 随机种子: {config['random_seed']}")
except Exception as e:
    print(f"  ✗ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("✅ 所有测试通过！")
print("=" * 80)
