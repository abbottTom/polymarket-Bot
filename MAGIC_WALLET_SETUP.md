# Magic/邮箱钱包配置指南

## ✅ 已完成的修改

已将代码修改为支持 Magic/邮箱钱包（signature_type=1）：

1. **config.py**: 添加了 `POLYMARKET_SIGNATURE_TYPE` 配置
2. **core/wallet.py**: 修改订单签名使用配置的签名类型
3. **.env**: 已设置 `POLYMARKET_SIGNATURE_TYPE=1`

## 🔑 还需要的步骤：获取私钥

**重要**：即使使用 Magic/邮箱钱包（signature_type=1），仍然需要提供私钥来签署订单。区别在于 Polymarket 验证签名的方式不同，但签名过程本身还是需要私钥。

### 从 Magic 钱包导出私钥

Magic 钱包允许导出私钥。有两种方法：

#### 方法 1: 通过 Polymarket 网站导出

1. 登录 Polymarket (https://polymarket.com)
2. 点击右上角钱包地址
3. 进入 "Settings" 或 "Wallet Settings"
4. 查找 "Export Private Key" 或 "Reveal Private Key"
5. 验证邮箱后显示私钥
6. 复制私钥到 `.env` 文件中的 `PRIVATE_KEY`

#### 方法 2: 通过 Magic Dashboard

1. 访问 Magic 仪表板
2. 找到 "Reveal Private Key" 选项
3. 完成身份验证
4. 导出私钥

### 配置 .env 文件

导出私钥后，在 `.env` 文件中配置：

```bash
# 你的 Magic 钱包私钥
PRIVATE_KEY=0x你的私钥...

# 使用 Magic 钱包签名类型
POLYMARKET_SIGNATURE_TYPE=1
```

## 🔍 signature_type 的区别

- **signature_type=0 (EOA)**: Polymarket 期望标准的以太坊钱包签名
- **signature_type=1 (Magic/Email)**: Polymarket 知道这是 Magic 钱包，使用委托验证流程
- **signature_type=2 (Proxy)**: 代理合约签名

**关键点**：signature_type 告诉 Polymarket 如何**验证**签名，但不改变如何**生成**签名。你仍然需要私钥。

## ⚠️ 安全提示

1. **绝对不要**将私钥提交到 Git
2. `.env` 文件已在 `.gitignore` 中
3. 定期轮换私钥
4. 只在机器人钱包中保留必要的资金

## 🧪 测试配置

配置完成后，运行预检查：

```bash
python scripts/preflight_check.py
```

如果一切正常，会显示：
- ✅ 钱包已初始化
- ✅ 签名类型: Magic/Email (1)

## ❓ 如果无法导出私钥

如果 Polymarket 的 Magic 钱包不允许导出私钥，你有两个选择：

1. **联系 Polymarket 支持**：询问程序化交易的 API 访问方式
2. **创建新的 EOA 钱包**：使用标准钱包（signature_type=0）
   ```bash
   python -c "from core.wallet import Wallet; Wallet.create_random_wallet()"
   ```
   然后将资金从邮箱钱包转到新钱包

## 📚 参考资源

- Polymarket API 文档: https://docs.polymarket.com
- Magic 文档: https://magic.link/docs
- EIP-712 签名标准: https://eips.ethereum.org/EIPS/eip-712
