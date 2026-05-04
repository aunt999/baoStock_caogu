# MongoDB 安装指南（Windows）

## 方法一：官网下载（推荐）

1. **访问官网下载页面**
   https://www.mongodb.com/try/download/community

2. **选择版本**
   - Version: 7.0.x（当前最新稳定版）
   - Platform: Windows
   - Package: zip

3. **下载后解压到**
   ```
   D:\ProgramData\MongoDB\
   ```

4. **创建数据和日志目录**
   ```powershell
   mkdir D:\ProgramData\MongoDB\data
   mkdir D:\ProgramData\MongoDB\log
   ```

5. **启动 MongoDB**
   ```powershell
   D:\ProgramData\MongoDB\bin\mongod.exe --dbpath D:\ProgramData\MongoDB\data
   ```

6. **验证连接**
   ```powershell
   D:\ProgramData\MongoDB\bin\mongosh.exe
   # 输入 show dbs 应显示默认数据库
   ```

---

## 方法二：使用 Chocolatey

如果已安装 Chocolatey：

```powershell
choco install mongodb -y
```

---

## 方法三：使用 Scoop

如果已安装 Scoop：

```powershell
scoop install mongodb
```

---

## 配置为 Windows 服务（开机自启）

创建配置文件 `D:\ProgramData\MongoDB\mongod.cfg`：

```yaml
storage:
  dbPath: D:\ProgramData\MongoDB\data
systemLog:
  destination: file
  path: D:\ProgramData\MongoDB\log\mongod.log
net:
  port: 27017
  bindIp: 127.0.0.1
```

安装服务：

```powershell
D:\ProgramData\MongoDB\bin\mongod.exe --config D:\ProgramData\MongoDB\mongod.cfg --install

# 启动服务
net start MongoDB

# 停止服务
net stop MongoDB
```

---

## QUANTAXIS 初始化数据

MongoDB 启动后，在 Python 中：

```python
import sys
sys.exit = lambda c=0: None
import QUANTAXIS as QA

# 保存股票列表
QA.QA_save_stock_list()

# 保存日K线数据（需要较长时间）
QA.QA_SU_save_stock_day(client=QA.QAUtil.QA_Setting().client)

# 验证
print(QA.QA_fetch_stock_list().head())
```

---

## 常见问题

**Q: 端口被占用？**
```powershell
netstat -ano | findstr 27017
# 杀掉占用进程
taskkill /PID <pid> /F
```

**Q: 数据目录权限问题？**
```powershell
# 给目录添加当前用户完全控制权限
icacls D:\ProgramData\MongoDB\data /grant:r "%USERNAME%:F"
```
