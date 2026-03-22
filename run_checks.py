#!/usr/bin/env python3
"""
快速运行套利机器人所有检查的脚本
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """运行命令并在成功时返回 True"""
    print(f"\n🔍 {description}")
    print("=" * 60)

    try:
        # 使用 bash 执行带 source 的命令
        result = subprocess.run(
            f"bash -c '{command}'",
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        success = result.returncode == 0
        status = "✅ 成功" if success else "❌ 错误"
        print(f"\n{status}: {description}")

        return success
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """检查主函数"""
    print("🤖 套利机器人检查")
    print("=" * 60)

    # 激活虚拟环境
    venv_activate = "source venv/bin/activate && "

    checks = [
        # 检查依赖
        (f"{venv_activate}pip list", "检查已安装依赖"),
        # 运行单元测试
        (f"{venv_activate}python -m pytest tests/ -v", "运行单元测试"),
        # 检查主要文件语法
        (f"{venv_activate}python -m py_compile main.py", "检查 main.py 语法"),
        (
            f"{venv_activate}python -m py_compile config.py",
            "检查 config.py 语法",
        ),
        (
            f"{venv_activate}python -m py_compile core/processor.py",
            "检查 processor.py 语法",
        ),
        (
            f"{venv_activate}python -m py_compile core/matcher.py",
            "检查 matcher.py 语法",
        ),
        (
            f"{venv_activate}python -m py_compile core/metrics.py",
            "检查 metrics.py 语法",
        ),
        (
            f"{venv_activate}python -m py_compile core/alerts.py",
            "检查 alerts.py 语法",
        ),
        (
            f"{venv_activate}python -m py_compile connectors/polymarket.py",
            "检查 polymarket.py 语法",
        ),
        (
            f"{venv_activate}python -m py_compile connectors/sx.py",
            "检查 sx.py 语法",
        ),
        (
            f"{venv_activate}python -m py_compile utils/retry.py",
            "检查 retry.py 语法",
        ),
        # 演示运行机器人
        (
            f"{venv_activate}python demo_bot.py --cycles 1 --interval 1",
            "演示运行机器人",
        ),
    ]

    results = []
    for command, description in checks:
        success = run_command(command, description)
        results.append((description, success))

    # 最终报告
    print("\n📊 最终报告")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")

    print(f"\n🎯 结果: {passed}/{total} 个检查通过")

    if passed == total:
        print("🎉 所有检查都通过了！")
        print("🚀 机器人已准备好工作！")
        return 0
    else:
        print("⚠️  一些检查未通过。请检查上面的错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
