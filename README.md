# WOL CLI 脚本

一个用于 Linux 的 Wake-on-LAN (WOL) 脚本，支持：

- 保存和管理多台设备的 MAC 地址，并可为每个 MAC 命名  
- 自动识别本机网卡
---

## 功能特点

1. **MAC 地址管理**
   - 新增 MAC 地址并为其命名  
   - 保存到 `saved_macs.json`  
   - 下次运行可直接选择已有 MAC  
---

## 使用说明

### 运行脚本

```bash
python3 wol-cli.py
