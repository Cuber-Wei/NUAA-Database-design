from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
import hashlib
import random
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 请更换为更安全的密钥

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Wei-040618',  # 请填入你的MySQL密码
    'database': 'wishes_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def init_db():
    """初始化数据库，插入测试数据"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 检查是否已有数据
            cursor.execute("SELECT COUNT(*) as count FROM characters")
            char_count = cursor.fetchone()['count']
            
            if char_count == 0:
                # 插入角色数据
                characters = [
                    (1, '稀罕', 3), (2, '安柏', 4), (3, '凯亚', 4),
                    (4, '迪卢克', 5), (5, '温迪', 5), (6, '钟离', 5),
                    (7, '芭芭拉', 4), (8, '香菱', 4), (9, '北斗', 4),
                    (10, '胡桃', 5), (11, '枫原万叶', 5), (12, '雷电将军', 5)
                ]
                
                cursor.executemany(
                    "INSERT INTO characters (Cno, Cname, Grade) VALUES (%s, %s, %s)",
                    characters
                )
                
                # 插入武器数据
                weapons = [
                    (1, '铁剑', 3), (2, '白铁大剑', 3), (3, '猎弓', 3),
                    (4, '祭礼剑', 4), (5, '西风剑', 4), (6, '黑剑', 4),
                    (7, '狼的末路', 5), (8, '天空之傲', 5), (9, '护摩之杖', 5),
                    (10, '阿莫斯之弓', 5), (11, '风鹰剑', 5), (12, '磐岩结绿', 5)
                ]
                
                cursor.executemany(
                    "INSERT INTO weapons (Wno, Wname, Grade) VALUES (%s, %s, %s)",
                    weapons
                )
                
                connection.commit()
                print("测试数据初始化完成")
                
    except Exception as e:
        print(f"初始化数据库失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()
    
    return True

def login_required(f):
    """登录装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def md5_encrypt(password):
    """MD5加密"""
    return hashlib.md5(password.encode()).hexdigest()

@app.route('/')
def index():
    """主页"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 表单验证
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
            
        if len(username) > 20 or len(password) > 20:
            flash('用户名和密码长度不能超过20个字符', 'error')
            return render_template('register.html')
        
        connection = get_db_connection()
        if not connection:
            flash('数据库连接失败', 'error')
            return render_template('register.html')
        
        try:
            with connection.cursor() as cursor:
                # 检查用户名是否已存在
                cursor.execute("SELECT Uno FROM users WHERE Uname = %s", (username,))
                if cursor.fetchone():
                    flash('用户名已存在', 'error')
                    return render_template('register.html')
                
                # 生成用户ID
                cursor.execute("SELECT IFNULL(MAX(Uno), 0) + 1 as next_id FROM users")
                user_id = cursor.fetchone()['next_id']
                
                # 插入新用户
                encrypted_password = md5_encrypt(password)
                cursor.execute(
                    "INSERT INTO users (Uno, Uname, Upassword) VALUES (%s, %s, %s)",
                    (user_id, username, encrypted_password)
                )
                connection.commit()
                
                flash('注册成功，请登录', 'success')
                return redirect(url_for('login'))
                
        except Exception as e:
            flash(f'注册失败: {str(e)}', 'error')
            connection.rollback()
        finally:
            connection.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('login.html')
        
        connection = get_db_connection()
        if not connection:
            flash('数据库连接失败', 'error')
            return render_template('login.html')
        
        try:
            with connection.cursor() as cursor:
                encrypted_password = md5_encrypt(password)
                cursor.execute(
                    "SELECT Uno, Uname FROM users WHERE Uname = %s AND Upassword = %s",
                    (username, encrypted_password)
                )
                user = cursor.fetchone()
                
                if user:
                    session['user_id'] = user['Uno']
                    session['username'] = user['Uname']
                    flash('登录成功', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('用户名或密码错误', 'error')
                    
        except Exception as e:
            flash(f'登录失败: {str(e)}', 'error')
        finally:
            connection.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash('已成功退出登录', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """用户仪表板"""
    connection = get_db_connection()
    if not connection:
        flash('数据库连接失败', 'error')
        return redirect(url_for('index'))
    
    try:
        with connection.cursor() as cursor:
            # 获取用户抽卡统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_wishes,
                    SUM(CASE WHEN w.Wtype = 0 THEN 1 ELSE 0 END) as character_wishes,
                    SUM(CASE WHEN w.Wtype = 1 THEN 1 ELSE 0 END) as weapon_wishes
                FROM wishes w 
                WHERE w.Wuser = %s
            """, (session['user_id'],))
            stats = cursor.fetchone()
            
            # 获取最近的抽卡记录
            cursor.execute("""
                SELECT 
                    w.Wtime,
                    w.Wtype,
                    c.Cname,
                    c.Grade as CGrade,
                    wp.Wname,
                    wp.Grade as WGrade
                FROM wishes w
                LEFT JOIN characters c ON w.Wcharacter = c.Cno
                LEFT JOIN weapons wp ON w.Wweapon = wp.Wno
                WHERE w.Wuser = %s
                ORDER BY w.Wtime DESC
                LIMIT 10
            """, (session['user_id'],))
            recent_wishes = cursor.fetchall()
            
    except Exception as e:
        flash(f'获取数据失败: {str(e)}', 'error')
        stats = {'total_wishes': 0, 'character_wishes': 0, 'weapon_wishes': 0}
        recent_wishes = []
    finally:
        connection.close()
    
    return render_template('dashboard.html', stats=stats, recent_wishes=recent_wishes)

@app.route('/wish', methods=['GET', 'POST'])
@login_required
def wish():
    """抽卡页面"""
    if request.method == 'POST':
        wish_type = request.form.get('wish_type')  # 'single' or 'ten'
        pool_type = request.form.get('pool_type')  # 'character' or 'weapon'
        
        if wish_type not in ['single', 'ten'] or pool_type not in ['character', 'weapon']:
            return jsonify({'success': False, 'message': '参数错误'})
        
        wish_count = 1 if wish_type == 'single' else 10
        results = []
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        try:
            with connection.cursor() as cursor:
                # 获取卡池数据
                if pool_type == 'character':
                    cursor.execute("SELECT Cno, Cname, Grade FROM characters ORDER BY Grade, RAND()")
                    pool_items = cursor.fetchall()
                else:
                    cursor.execute("SELECT Wno, Wname, Grade FROM weapons ORDER BY Grade, RAND()")
                    pool_items = cursor.fetchall()
                
                for _ in range(wish_count):
                    # 抽卡概率设置
                    rand = random.random()
                    if rand < 0.006:  # 0.6% 概率抽到5星
                        target_grade = 5
                    elif rand < 0.057:  # 5.1% 概率抽到4星
                        target_grade = 4
                    else:  # 其余为3星
                        target_grade = 3
                    
                    # 从对应星级中随机选择
                    grade_items = [item for item in pool_items if item['Grade'] == target_grade]
                    if not grade_items:
                        grade_items = pool_items  # 如果没有对应星级，则从全部中选择
                    
                    selected_item = random.choice(grade_items)
                    
                    # 生成抽卡记录ID
                    cursor.execute("SELECT IFNULL(MAX(Wno), 0) + 1 as next_id FROM wishes")
                    wish_id = cursor.fetchone()['next_id']
                    
                    # 插入抽卡记录
                    now = datetime.datetime.now()
                    if pool_type == 'character':
                        cursor.execute("""
                            INSERT INTO wishes (Wno, Wuser, Wtype, Wcharacter, Wweapon, Wtime)
                            VALUES (%s, %s, 0, %s, 0, %s)
                        """, (wish_id, session['user_id'], selected_item['Cno'], now))
                        results.append({
                            'type': 'character',
                            'name': selected_item['Cname'],
                            'grade': selected_item['Grade']
                        })
                    else:
                        cursor.execute("""
                            INSERT INTO wishes (Wno, Wuser, Wtype, Wcharacter, Wweapon, Wtime)
                            VALUES (%s, %s, 1, 0, %s, %s)
                        """, (wish_id, session['user_id'], selected_item['Wno'], now))
                        results.append({
                            'type': 'weapon',
                            'name': selected_item['Wname'],
                            'grade': selected_item['Grade']
                        })
                
                connection.commit()
                return jsonify({
                    'success': True,
                    'results': results,
                    'message': f'抽卡成功！获得{len(results)}个道具'
                })
                
        except Exception as e:
            connection.rollback()
            return jsonify({'success': False, 'message': f'抽卡失败: {str(e)}'})
        finally:
            connection.close()
    
    return render_template('wish.html')

@app.route('/history')
@login_required
def history():
    """抽卡记录"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    connection = get_db_connection()
    if not connection:
        flash('数据库连接失败', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        with connection.cursor() as cursor:
            # 获取总记录数
            cursor.execute("SELECT COUNT(*) as total FROM wishes WHERE Wuser = %s", (session['user_id'],))
            total = cursor.fetchone()['total']
            
            # 获取分页数据
            cursor.execute("""
                SELECT 
                    w.Wtime,
                    w.Wtype,
                    c.Cname,
                    c.Grade as CGrade,
                    wp.Wname,
                    wp.Grade as WGrade
                FROM wishes w
                LEFT JOIN characters c ON w.Wcharacter = c.Cno
                LEFT JOIN weapons wp ON w.Wweapon = wp.Wno
                WHERE w.Wuser = %s
                ORDER BY w.Wtime DESC
                LIMIT %s OFFSET %s
            """, (session['user_id'], per_page, offset))
            wishes = cursor.fetchall()
            
            # 计算分页信息
            total_pages = (total + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
    except Exception as e:
        flash(f'获取抽卡记录失败: {str(e)}', 'error')
        wishes = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
    finally:
        connection.close()
    
    return render_template('history.html', 
                         wishes=wishes, 
                         page=page, 
                         total_pages=total_pages,
                         has_prev=has_prev, 
                         has_next=has_next,
                         total=total)

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001) 