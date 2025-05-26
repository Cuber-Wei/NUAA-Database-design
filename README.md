# Flask 抽卡系统

一个基于Flask框架开发的抽卡游戏系统，支持用户注册、登录、抽卡（单抽/十连抽）和抽卡记录查询功能。

## 功能特性

### 🔐 用户系统
- **用户注册**：支持新用户注册，密码MD5加密存储
- **用户登录**：安全的登录验证系统
- **会话管理**：基于Flask Session的用户状态管理

### 🎲 抽卡系统
- **双卡池设计**：角色卡池和武器卡池
- **多种抽卡方式**：单抽和十连抽
- **概率机制**：5星(0.6%) | 4星(5.1%) | 3星(94.3%)
- **实时结果展示**：美观的抽卡结果界面

### 📊 数据管理
- **抽卡记录**：完整的抽卡历史记录
- **统计信息**：用户抽卡数据统计
- **分页显示**：支持大量数据的分页浏览

## 技术栈

- **后端框架**：Flask 2.3.3
- **数据库**：MySQL
- **数据库连接**：PyMySQL
- **前端框架**：Bootstrap 5.1.3
- **图标库**：Bootstrap Icons
- **密码加密**：MD5

## 项目结构

```
databaseLab/
├── app.py                  # Flask主应用文件
├── db.sql                  # 数据库建表脚本
├── requirements.txt        # Python依赖包
├── README.md              # 项目说明文档
└── templates/             # HTML模板文件
    ├── base.html          # 基础模板
    ├── index.html         # 主页
    ├── login.html         # 登录页面
    ├── register.html      # 注册页面
    ├── dashboard.html     # 用户仪表板
    ├── wish.html          # 抽卡页面
    └── history.html       # 抽卡记录页面
```

## 数据库设计

### 表结构
1. **users** - 用户表
   - Uno (bigint): 用户ID
   - Uname (varchar): 用户名
   - Upassword (varchar): 密码(MD5)

2. **characters** - 角色表
   - Cno (bigint): 角色ID
   - Cname (varchar): 角色名
   - Grade (smallint): 星级

3. **weapons** - 武器表
   - Wno (bigint): 武器ID
   - Wname (varchar): 武器名
   - Grade (smallint): 星级

4. **wishes** - 抽卡记录表
   - Wno (bigint): 记录ID
   - Wuser (bigint): 用户ID
   - Wtype (tinyint): 类型(0:角色,1:武器)
   - Wcharacter (bigint): 角色ID
   - Wweapon (bigint): 武器ID
   - Wtime (datetime): 抽卡时间

## 安装和运行

### 1. 环境准备
```bash
# 确保已安装Python 3.7+和MySQL
# 克隆或下载项目文件
```

### 2. 安装依赖
```bash
# 使用uv（推荐）
uv pip install -r requirements.txt

# 或使用pip
pip install -r requirements.txt
```

### 3. 数据库配置
```bash
# 1. 登录MySQL
mysql -u root -p

# 2. 执行建表脚本
source db.sql
```

### 4. 修改数据库配置
编辑 `app.py` 文件中的数据库配置：
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # 修改为你的MySQL密码
    'database': 'wishes_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
```

### 5. 运行应用
```bash
python app.py
```

应用将在 http://localhost:5000 启动

## 使用说明

### 用户注册和登录
1. 访问主页，点击"立即注册"
2. 填写用户名和密码完成注册
3. 使用注册的账号登录系统

### 抽卡功能
1. 登录后进入仪表板
2. 点击"立即抽卡"进入抽卡页面
3. 选择卡池类型（角色/武器）
4. 选择抽卡方式（单抽/十连抽）
5. 查看抽卡结果

### 查看记录
1. 在仪表板查看最近10条记录
2. 点击"查看记录"查看完整历史
3. 支持分页浏览和快速跳转

## 特色功能

### 🎨 精美界面
- 响应式设计，支持移动端
- 现代化UI，流畅的用户体验
- 丰富的图标和动画效果

### 🎯 真实抽卡体验
- 真实的概率机制
- 精美的抽卡结果展示
- 完整的抽卡统计

### 🔒 安全可靠
- 密码加密存储
- SQL注入防护
- 会话安全管理

## 扩展建议

1. **用户系统增强**
   - 添加邮箱验证
   - 忘记密码功能
   - 用户头像上传

2. **抽卡系统优化**
   - 保底机制
   - 卡池UP机制
   - 抽卡动画效果

3. **数据分析**
   - 用户抽卡分析
   - 概率统计报告
   - 导出功能

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过GitHub Issues联系。
