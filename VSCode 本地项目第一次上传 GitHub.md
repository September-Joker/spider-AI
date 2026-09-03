# VSCode 本地项目第一次上传 GitHub（完整流程）
>前提：电脑安装 **Git**，注册 GitHub 账号；项目文件夹已经在 VSCode 打开（就是你刚才用venv的Python项目）。

## 🔔 重要前置：Python项目一定要写 `.gitignore`
把虚拟环境、缓存、日志排除，**不要上传venv文件夹**！
在项目根新建文件，名字叫 `.gitignore`，复制下面内容：
```gitignore
# 虚拟环境
venv/
.venv/
myenv/

# python缓存
__pycache__/
*.pyc
*.pyo
*.pyd

# 环境变量、密钥
.env
*.log

# vscode配置
.vscode/
```

---

## 方式一：VSCode图形界面（最简单，推荐新手）
1. 左侧图标打开【源代码管理】 `Ctrl+Shift+G`
2. 点击 **初始化仓库 Initialize Repository** → 选择当前项目文件夹。
> 等价终端执行 `git init`，生成隐藏 `.git` 文件夹。

3. 填写提交信息（例如：`初始化项目代码`），点 **提交(Commit)**。

4. 点击 **发布到 GitHub(Publish to GitHub)**
    - 弹出浏览器授权登录GitHub
    - 选择：**公开仓库 / 私有仓库**
    - VSCode自动在GitHub创建仓库，并且把代码推送上去。

>完成后打开github网页，就能看到你的项目。

---

## 方式二：终端命令行（更可控，强烈建议掌握）
### 步骤1：GitHub网页新建仓库
1. github右上角点加号 → New repository
2. 填写仓库名字，选公开/私有
3. ⚠️**三个选项全部不要勾选**：不要Add README、不要.gitignore、不要License，否则首次推送会冲突！
4. 点Create repository，复制仓库HTTPS地址，类似：
`https://github.com/你的用户名/仓库名.git`

### 步骤2 VSCode终端操作（Ctrl+`打开终端）
```bash
# 1.初始化git仓库
git init

# 2.把所有文件加入暂存（会自动遵守.gitignore规则，不会上传venv）
git add .

#3.本地提交
git commit -m "初始化项目代码"

#4.关联远程github仓库，粘贴你复制的仓库地址
git remote add origin https://github.com/你的用户名/仓库名.git

#5.修改分支名为main（新版github默认分支main）
git branch -M main

#6.第一次推送
git push -u origin main
```
执行完，网页刷新github，代码就全部上去了。

> `-u origin main`：设置上游，以后推送只需要简单写 `git push`。

---

## 🧩首次使用git，需要配置用户名邮箱（只做一次）
```bash
git config --global user.name "你的github用户名"
git config --global user.email "注册github的邮箱"
```
查看配置：`git config --global --list`

## 后续日常提交代码流程
1. 修改代码
2. `Ctrl+Shift+G`源代码管理
3. 写提交信息 → Commit
4. 点右上角同步更改（Sync Changes），等价 `git push`

## 常见踩坑
1. **千万不要上传 venv虚拟环境文件夹**，靠requirements.txt做环境复现。
2. 推送提示密码错误：github不再支持账号密码登录，HTTPS方式会弹窗浏览器授权登录，按提示完成。
3. 报错 `fatal: remote origin already exists`：已经关联过远程，执行清除旧远程：
```bash
git remote remove origin
```
再重新执行 `git remote add origin xxx`。
4. 如果你创建github仓库时手贱勾选了README，需要先拉取一次再推送：
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 补充：把requirements.txt也提交到github
```bash
pip freeze > requirements.txt
```
这个文件要上传，别人拿到你的项目就可以一键重建虚拟环境。

>别人拿到项目：
```bash
python -m venv venv
#激活虚拟环境
pip install -r requirements.txt
```

