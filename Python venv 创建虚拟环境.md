# Python venv 创建虚拟环境
> venv 是 Python3.3+ 自带虚拟环境工具，**无需额外安装**，不同操作系统命令略有区别。

## 1. 创建虚拟环境
打开终端/命令提示符，进入项目文件夹
```bash
# windows / mac / linux 通用创建命令
python -m venv myenv
```
- `myenv`：虚拟环境文件夹名字，可以自定义，比如 `venv`、`.venv`

执行完成，当前目录会生成 `myenv` 文件夹，里面是独立Python解释器、pip、依赖包。

## 2. 激活虚拟环境
### Windows CMD
```cmd
myenv\Scripts\activate
```

### Windows PowerShell
```powershell
.\myenv\Scripts\Activate.ps1
```
> PowerShell 如果报执行策略报错，管理员身份运行：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Mac / Linux
```bash
source myenv/bin/activate
```

✅激活成功：终端前面会出现 `(myenv)` 标识，代表已经进入虚拟环境，此时pip安装包只会装到这个环境。

## 3. 在虚拟环境安装包
```bash
pip install requests parsel
```

导出依赖清单（分享项目必备）
```bash
pip freeze > requirements.txt
```

## 4. 退出虚拟环境
任意系统，激活状态下执行：
```bash
deactivate
```

## 5. 别人拿到项目，恢复环境
```bash
# 创建环境
python -m venv myenv
# 激活环境
# windows: myenv\Scripts\activate
# mac/linux: source myenv/bin/activate

# 根据requirements.txt批量安装
pip install -r requirements.txt
```

## 6. 删除虚拟环境
直接删除 `myenv` 文件夹即可，没有残留。

---

## 常见坑
1. Windows 多Python版本：把 `python` 换成 `py -3` 指定版本
```bash
py -3 -m venv myenv
```
2. 不要把虚拟环境文件夹提交到git，`.gitignore` 添加一行
```
myenv/
.venv/
__pycache__/
*.pyc
```
3. VSCode使用venv：选择解释器，选中 `myenv/Scripts/python.exe`(win) / `myenv/bin/python`(mac)

