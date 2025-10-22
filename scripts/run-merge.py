"""執行 auto-daily-report.py 的 merge_to_public 函數"""
import sys
import os

# 動態載入 auto-daily-report.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "auto_daily_report",
    os.path.join(os.path.dirname(__file__), "auto-daily-report.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# 執行 merge_to_public
module.merge_to_public()
