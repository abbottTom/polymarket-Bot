# Kalshi 功能已禁用

本代码库已禁用所有 Kalshi 相关功能，仅保留 **Polymarket** 和 **SX** 两个交易所。

## 已修改的文件

1. **main.py**
   - ✅ 移除 `kalshi` 导入
   - ✅ 禁用 auto_pipeline 中的 Kalshi API key

2. **config.py**
   - ✅ 强制设置 `AUTO_MATCH_INCLUDE_KALSHI = False`

## 验证禁用

运行以下命令确认没有错误：

```bash
# 检查语法
python -m py_compile main.py
python -m py_compile config.py

# 运行测试（会跳过 Kalshi 相关测试）
python -m pytest tests/ -v -k "not kalshi"
```

## 如果需要重新启用 Kalshi

1. 恢复 `main.py` 第14行的导入：
   ```python
   from connectors import polymarket, sx, kalshi
   ```

2. 恢复 `config.py` 第36-38行：
   ```python
   AUTO_MATCH_INCLUDE_KALSHI = (
       os.getenv("AUTO_MATCH_INCLUDE_KALSHI", "false").lower() == "true"
   )
   ```

3. 在 `.env` 文件中设置：
   ```bash
   AUTO_MATCH_INCLUDE_KALSHI=true
   KALSHI_API_KEY=your_key_here
   ```

## 当前支持的交易所

- ✅ **Polymarket** - 完全支持
- ✅ **SX** - 完全支持
- ❌ **Kalshi** - 已禁用

---

**修改日期**: 2026-03-22
