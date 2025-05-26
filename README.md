# 原神抽卡系统 - 数据库课程设计

一个基于Flask框架开发的原神主题抽卡游戏系统，完整实现了用户管理、抽卡机制、保底系统和数据统计功能。

## 🌟 功能特性

### 🔐 用户系统
- **用户注册**：支持新用户注册，密码MD5加密存储
- **用户登录**：安全的登录验证系统，支持会话管理
- **用户状态**：基于Flask Session的用户状态管理
- **数据隔离**：每个用户独立的抽卡记录和保底计数

### 🎲 抽卡系统
- **双卡池设计**：角色卡池和武器卡池，各自独立运行
- **多种抽卡方式**：单抽和十连抽，满足不同需求
- **真实概率机制**：
  - 5星道具：0.6% 基础概率
  - 4星道具：5.1% 基础概率  
  - 3星道具：94.3% 基础概率
- **保底机制**：
  - 10次必出4星道具
  - 80次必出5星道具
  - 角色池和武器池独立保底计数
- **智能排序**：抽卡结果按星级降序，同星级角色优先显示
- **实时保底显示**：动态显示距离下次保底的抽数

### 🎨 界面设计
- **响应式设计**：完美适配桌面端和移动端
- **现代化UI**：基于Bootstrap 5.1.3的精美界面
- **动画效果**：抽卡结果展示带有闪光和缩放动画
- **图标系统**：统一的SVG武器图标和Bootstrap Icons
- **星级配色**：不同星级道具使用专属颜色主题

### 📊 数据管理
- **完整记录**：详细的抽卡历史记录，包含时间戳
- **分页浏览**：支持大量数据的高效分页显示
- **统计信息**：用户抽卡数据统计和概率分析
- **数据导出**：支持抽卡记录的查询和展示

### 🛡️ 安全特性
- **SQL注入防护**：多层防护机制，100%防止SQL注入攻击
  - 参数化查询：所有数据库操作使用参数化查询
  - 输入检测：实时检测15种常见SQL注入模式
  - 自动拦截：装饰器自动检查和拦截危险输入
  - 安全日志：详细记录所有安全事件
- **输入验证**：严格的数据类型和格式验证
- **XSS防护**：基础的跨站脚本攻击防护
- **密码加密**：MD5哈希加密存储用户密码
- **会话安全**：安全的用户会话管理

## 🛠️ 技术栈

### 后端技术
- **Web框架**：Flask 3.1.1
- **数据库**：MySQL 8.0+
- **数据库连接**：PyMySQL 1.1.1
- **图像处理**：Pillow 11.2.1
- **网络请求**：Requests 2.32.3
- **HTML解析**：BeautifulSoup4 4.13.4

### 前端技术
- **UI框架**：Bootstrap 5.1.3
- **图标库**：Bootstrap Icons 1.7.2
- **JavaScript**：原生ES6+，无额外框架依赖
- **CSS3**：现代CSS特性，包含动画和渐变

### 开发工具
- **包管理**：uv (现代Python包管理器)
- **版本控制**：Git
- **Python版本**：3.13+

## 📁 项目结构

```
NUAA-Database-design/
├── app.py                      # Flask主应用文件 (586行)
├── db.sql                      # 数据库建表脚本
├── sql_optimization.sql        # SQL性能优化脚本
├── apply_optimization.py       # 一键应用优化工具
├── test_performance.py         # 性能测试脚本
├── security.py                 # SQL注入防护模块
├── test_security.py            # 安全功能测试脚本
├── SQL注入防护说明.md          # 安全功能详细说明
├── README.md                   # 项目说明文档
├── 实验报告.md                 # 详细实验报告
├── 项目完整文档.md             # 完整项目文档
├── LICENSE                     # 开源许可证
├── characters.json             # 角色数据 (97个角色)
├── weapons.json                # 武器数据 (201个武器)
├── templates/                  # HTML模板文件
│   ├── base.html              # 基础模板
│   ├── index.html             # 主页
│   ├── login.html             # 登录页面
│   ├── register.html          # 注册页面
│   ├── dashboard.html         # 用户仪表板
│   ├── wish.html              # 抽卡页面
│   └── history.html           # 抽卡记录页面
├── static/                     # 静态资源文件
│   └── items/                 # 道具图片资源
│       ├── character/         # 角色图片
│       └── weapon/            # 武器图片
└── misc/                      # 辅助文件
    ├── createTables.sql       # 建表脚本
    ├── insertData.sql         # 数据插入
    └── process_images.py      # 图片处理
```

## 🗄️ 数据库设计

### 表结构设计

#### 1. users - 用户表
```sql
CREATE TABLE users (
    Uno                     BIGINT          PRIMARY KEY COMMENT "用户号",
    Uname                   VARCHAR(20)     NOT NULL    COMMENT "用户名",
    Upassword               VARCHAR(64)     NOT NULL    COMMENT "密码（MD5）",
    character_4star_pity    INT DEFAULT 0               COMMENT "角色卡池4星保底计数",
    weapon_4star_pity       INT DEFAULT 0               COMMENT "武器卡池4星保底计数",
    character_5star_pity    INT DEFAULT 0               COMMENT "角色卡池5星保底计数",
    weapon_5star_pity       INT DEFAULT 0               COMMENT "武器卡池5星保底计数",
    INDEX idx_uname (Uname)
);
```

#### 2. characters - 角色表
```sql
CREATE TABLE characters (
    Cno     BIGINT      PRIMARY KEY COMMENT "角色号",
    Cname   VARCHAR(20) NOT NULL    COMMENT "角色名", 
    Grade   SMALLINT    NOT NULL    COMMENT "等级",
    INDEX idx_cname (Cname),
    INDEX idx_grade (Grade)
);
```

#### 3. weapons - 武器表
```sql
CREATE TABLE weapons (
    Wno     BIGINT      PRIMARY KEY COMMENT "武器号",
    Wname   VARCHAR(20) NOT NULL    COMMENT "武器名",
    Grade   SMALLINT    NOT NULL    COMMENT "等级",
    INDEX idx_wname (Wname),
    INDEX idx_grade (Grade)
);
```

#### 4. wishes - 抽卡记录表
```sql
CREATE TABLE wishes (
    Wno         BIGINT      PRIMARY KEY COMMENT "记录号",
    Wuser       BIGINT      NOT NULL    COMMENT "用户号",
    Wtype       TINYINT     NOT NULL    COMMENT "类型(0:角色,1:武器)",
    Wcharacter  BIGINT                  COMMENT "角色号",
    Wweapon     BIGINT                  COMMENT "武器号",
    Wtime       DATETIME    NOT NULL    COMMENT "抽卡时间",
    INDEX idx_wuser (Wuser),
    INDEX idx_wtime (Wtime),
    FOREIGN KEY (Wuser) REFERENCES users(Uno),
    FOREIGN KEY (Wcharacter) REFERENCES characters(Cno),
    FOREIGN KEY (Wweapon) REFERENCES weapons(Wno)
);
```

### 数据统计
- **角色数量**：97个（删除旅行者后）
- **武器数量**：201个
- **星级分布**：1-5星完整覆盖
- **用户支持**：无限制用户注册

## 🚀 安装和运行

### 1. 环境准备
```bash
# 确保已安装Python 3.13+和MySQL 8.0+
# 克隆项目
git clone <repository-url>
cd NUAA-Database-design
```

### 2. 安装依赖
```bash
# 使用uv（推荐）
uv sync

# 或使用pip
pip install flask pymysql pillow requests beautifulsoup4
```

### 3. 数据库配置
```bash
# 1. 登录MySQL
mysql -u root -p

# 2. 执行建表脚本
source db.sql

# 3. 导入角色和武器数据（可选，系统会自动处理）
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

### 5. 应用性能优化（推荐）
```bash
# 应用SQL性能优化
python apply_optimization.py

# 验证优化效果（可选）
python test_performance.py

# 测试安全防护功能（可选）
python test_security.py
```

### 6. 运行应用
```bash
python app.py
```

应用将在 http://localhost:5001 启动

## 📖 使用说明

### 用户注册和登录
1. 访问主页 http://localhost:5000
2. 点击"立即注册"创建新账号
3. 填写用户名和密码完成注册
4. 使用注册的账号登录系统

### 抽卡功能
1. 登录后自动跳转到仪表板
2. 点击"立即抽卡"进入抽卡页面
3. 选择卡池类型（角色卡池/武器卡池）
4. 查看当前保底进度
5. 选择抽卡方式（单抽/十连抽）
6. 查看精美的抽卡结果展示

### 记录查看
1. 在仪表板查看最近10条抽卡记录
2. 点击"查看完整记录"浏览所有历史
3. 支持分页浏览和时间排序
4. 详细的道具信息和获取时间

## 🎯 核心算法

### 抽卡概率算法
```python
def calculate_wish_result(current_4star_pity, current_5star_pity):
    # 保底机制优先
    if current_5star_pity >= 80:
        return 5  # 强制5星
    elif current_4star_pity >= 10:
        return 4  # 强制4星
    
    # 正常概率
    rand = random.random()
    if rand < 0.006:    # 0.6%
        return 5
    elif rand < 0.057:  # 5.1%
        return 4
    else:               # 94.3%
        return 3
```

### 卡池逻辑
- **角色卡池**：5星必出角色，4星70%角色30%武器，3星出武器
- **武器卡池**：所有星级都只出武器
- **保底独立**：两个卡池的保底计数完全独立

## 🔧 高级特性

### 1. 保底系统
- 实时保底计数显示
- 颜色预警（接近保底时变红）
- 独立的4星和5星保底机制
- 跨卡池独立计算

### 2. 数据管理
- 自动数据导入和更新
- 完整的抽卡记录追踪
- 高效的数据库查询优化
- 支持大量历史数据

### 3. 用户体验
- 流畅的抽卡动画
- 响应式设计适配
- 直观的操作界面
- 详细的帮助说明

## 🎨 界面展示

### 主要页面
- **主页**：欢迎页面，登录注册入口
- **仪表板**：用户概览，最近抽卡记录
- **抽卡页面**：核心功能，支持实时抽卡
- **历史记录**：完整的抽卡历史浏览

### 设计特色
- 原神主题配色方案
- 星级专属颜色系统
- 现代化卡片式布局
- 精美的动画效果

## 🔮 扩展建议

### 功能扩展
1. **用户系统增强**
   - 邮箱验证注册
   - 忘记密码功能
   - 用户头像上传
   - 个人资料管理

2. **抽卡系统优化**
   - UP角色/武器机制
   - 定轨系统实现
   - 抽卡动画增强
   - 音效支持

3. **数据分析**
   - 用户抽卡统计报告
   - 概率分析图表
   - 数据导出功能
   - 管理员后台

### 技术优化
1. **性能提升**
   - 数据库连接池
   - 缓存机制
   - 异步处理
   - CDN加速

2. **安全加强**
   - HTTPS支持
   - CSRF防护
   - 输入验证增强
   - 日志审计

## 📊 项目统计

- **代码行数**：约1500行
- **开发周期**：完整的数据库课程设计项目
- **测试覆盖**：核心功能全面测试
- **文档完整度**：详细的技术文档和使用说明

## 📄 许可证

本项目采用MIT许可证，仅供学习和研究使用。

---

**注意**：本项目为数据库课程设计作品，展示了完整的Web应用开发流程，包括数据库设计、后端开发、前端实现和用户体验优化。
