from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
import pymysql
import hashlib
import random
import datetime
from functools import wraps

# 导入安全模块
from security import (
    SQLInjectionProtector,
    SecureDatabase,
    sql_injection_protection,
    validate_user_input,
    validate_wish_params,
    validate_pagination_params,
    log_security_event,
)

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # 请更换为更安全的密钥

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",  # 请填入你的MySQL密码
    "database": "wishes_db",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

# 初始化安全数据库实例
secure_db = SecureDatabase(DB_CONFIG)


def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


def init_db():
    """初始化数据库表结构"""
    connection = get_db_connection()
    if not connection:
        return False

    try:
        with connection.cursor() as cursor:
            # 检查数据库表是否存在，如果不存在则创建
            cursor.execute("SHOW TABLES LIKE 'characters'")
            if not cursor.fetchone():
                print("数据库表不存在，请先运行 db.sql 创建表结构")
                return False

            print("数据库表结构检查完成")

    except Exception as e:
        print(f"检查数据库失败: {e}")
        return False
    finally:
        connection.close()

    return True


def login_required(f):
    """登录装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("请先登录", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def md5_encrypt(password):
    """MD5加密"""
    return hashlib.md5(password.encode()).hexdigest()


@app.route("/")
def index():
    """主页"""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
@sql_injection_protection
def register():
    """用户注册"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # 使用安全验证
        validation_result = validate_user_input(username, password)
        if not validation_result["valid"]:
            for error in validation_result["errors"]:
                flash(error, "error")
            log_security_event(
                "INVALID_INPUT", f"Registration attempt with invalid input: {username}"
            )
            return render_template("register.html")

        # 验证密码确认
        if password != confirm_password:
            flash("两次输入的密码不一致", "error")
            return render_template("register.html")

        # 使用验证后的安全数据
        safe_username = validation_result["username"]
        safe_password = validation_result["password"]

        connection = get_db_connection()
        if not connection:
            flash("数据库连接失败", "error")
            return render_template("register.html")

        try:
            with connection.cursor() as cursor:
                # 检查用户名是否已存在
                cursor.execute(
                    "SELECT Uno FROM users WHERE Uname = %s", (safe_username,)
                )
                if cursor.fetchone():
                    flash("用户名已存在", "error")
                    log_security_event(
                        "DUPLICATE_USERNAME",
                        f"Registration attempt with existing username: {safe_username}",
                    )
                    return render_template("register.html")

                # 生成用户ID
                cursor.execute("SELECT IFNULL(MAX(Uno), 0) + 1 as next_id FROM users")
                user_id = cursor.fetchone()["next_id"]

                # 插入新用户
                encrypted_password = md5_encrypt(safe_password)
                cursor.execute(
                    "INSERT INTO users (Uno, Uname, Upassword) VALUES (%s, %s, %s)",
                    (user_id, safe_username, encrypted_password),
                )
                connection.commit()

                log_security_event(
                    "USER_REGISTERED", f"New user registered: {safe_username}", user_id
                )
                flash("注册成功，请登录", "success")
                return redirect(url_for("login"))

        except Exception as e:
            flash(f"注册失败: {str(e)}", "error")
            connection.rollback()
        finally:
            connection.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@sql_injection_protection
def login():
    """用户登录"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # 使用安全验证
        validation_result = validate_user_input(username, password)
        if not validation_result["valid"]:
            for error in validation_result["errors"]:
                flash(error, "error")
            log_security_event(
                "INVALID_LOGIN_INPUT", f"Login attempt with invalid input: {username}"
            )
            return render_template("login.html")

        # 使用验证后的安全数据
        safe_username = validation_result["username"]
        safe_password = validation_result["password"]

        connection = get_db_connection()
        if not connection:
            flash("数据库连接失败", "error")
            return render_template("login.html")

        try:
            with connection.cursor() as cursor:
                encrypted_password = md5_encrypt(safe_password)
                cursor.execute(
                    "SELECT Uno, Uname FROM users WHERE Uname = %s AND Upassword = %s",
                    (safe_username, encrypted_password),
                )
                user = cursor.fetchone()

                if user:
                    session["user_id"] = user["Uno"]
                    session["username"] = user["Uname"]
                    log_security_event(
                        "USER_LOGIN", f"User logged in: {safe_username}", user["Uno"]
                    )
                    flash("登录成功", "success")
                    return redirect(url_for("dashboard"))
                else:
                    log_security_event(
                        "LOGIN_FAILED",
                        f"Failed login attempt for username: {safe_username}",
                    )
                    flash("用户名或密码错误", "error")

        except Exception as e:
            flash(f"登录失败: {str(e)}", "error")
        finally:
            connection.close()

    return render_template("login.html")


@app.route("/logout")
def logout():
    """用户登出"""
    session.clear()
    flash("已成功退出登录", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    """用户仪表板"""
    connection = get_db_connection()
    if not connection:
        flash("数据库连接失败", "error")
        return redirect(url_for("index"))

    try:
        with connection.cursor() as cursor:
            # 优化的用户抽卡统计查询
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_wishes,
                    SUM(CASE WHEN Wtype = 0 THEN 1 ELSE 0 END) as character_wishes,
                    SUM(CASE WHEN Wtype = 1 THEN 1 ELSE 0 END) as weapon_wishes
                FROM wishes 
                WHERE Wuser = %s
            """,
                (session["user_id"],),
            )
            stats = cursor.fetchone()

            # 优化的最近抽卡记录查询 - 使用覆盖索引避免JOIN
            cursor.execute(
                """
                SELECT Wtime, Wtype, Wcharacter, Wweapon
                FROM wishes 
                WHERE Wuser = %s
                ORDER BY Wtime DESC
                LIMIT 10
            """,
                (session["user_id"],),
            )
            wishes_data = cursor.fetchall()

            # 批量获取角色和武器信息
            recent_wishes = []
            if wishes_data:
                character_ids = [
                    w["Wcharacter"] for w in wishes_data if w["Wcharacter"]
                ]
                weapon_ids = [w["Wweapon"] for w in wishes_data if w["Wweapon"]]

                characters = {}
                weapons = {}

                if character_ids:
                    cursor.execute(
                        """
                        SELECT Cno, Cname, Grade 
                        FROM characters 
                        WHERE Cno IN ({})
                    """.format(",".join(["%s"] * len(character_ids))),
                        character_ids,
                    )
                    characters = {c["Cno"]: c for c in cursor.fetchall()}

                if weapon_ids:
                    cursor.execute(
                        """
                        SELECT Wno, Wname, Grade 
                        FROM weapons 
                        WHERE Wno IN ({})
                    """.format(",".join(["%s"] * len(weapon_ids))),
                        weapon_ids,
                    )
                    weapons = {w["Wno"]: w for w in cursor.fetchall()}

                # 组装结果
                for wish in wishes_data:
                    wish_data = {
                        "Wtime": wish["Wtime"],
                        "Wtype": wish["Wtype"],
                        "Cname": None,
                        "CGrade": None,
                        "Wname": None,
                        "WGrade": None,
                    }

                    if wish["Wtype"] == 0 and wish["Wcharacter"] in characters:
                        char = characters[wish["Wcharacter"]]
                        wish_data["Cname"] = char["Cname"]
                        wish_data["CGrade"] = char["Grade"]
                    elif wish["Wtype"] == 1 and wish["Wweapon"] in weapons:
                        weapon = weapons[wish["Wweapon"]]
                        wish_data["Wname"] = weapon["Wname"]
                        wish_data["WGrade"] = weapon["Grade"]

                    recent_wishes.append(wish_data)

    except Exception as e:
        flash(f"获取数据失败: {str(e)}", "error")
        stats = {"total_wishes": 0, "character_wishes": 0, "weapon_wishes": 0}
        recent_wishes = []
    finally:
        connection.close()

    return render_template("dashboard.html", stats=stats, recent_wishes=recent_wishes)


@app.route("/wish", methods=["GET", "POST"])
@login_required
@sql_injection_protection
def wish():
    """抽卡页面"""
    if request.method == "POST":
        wish_type = request.form.get("wish_type")  # 'single' or 'ten'
        pool_type = request.form.get("pool_type")  # 'character' or 'weapon'

        # 使用安全验证
        validation_result = validate_wish_params(wish_type, pool_type)
        if not validation_result["valid"]:
            log_security_event(
                "INVALID_WISH_PARAMS",
                f"Invalid wish parameters: {wish_type}, {pool_type}",
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "参数错误"})

        # 使用验证后的安全参数
        safe_wish_type = validation_result["wish_type"]
        safe_pool_type = validation_result["pool_type"]

        wish_count = 1 if safe_wish_type == "single" else 10
        results = []

        connection = get_db_connection()
        if not connection:
            return jsonify({"success": False, "message": "数据库连接失败"})

        try:
            with connection.cursor() as cursor:
                # 获取用户当前保底计数
                cursor.execute(
                    """
                    SELECT character_4star_pity, weapon_4star_pity, 
                           character_5star_pity, weapon_5star_pity 
                    FROM users WHERE Uno = %s
                """,
                    (session["user_id"],),
                )
                user_pity = cursor.fetchone()

                if safe_pool_type == "character":
                    current_4star_pity = user_pity["character_4star_pity"]
                    current_5star_pity = user_pity["character_5star_pity"]
                else:
                    current_4star_pity = user_pity["weapon_4star_pity"]
                    current_5star_pity = user_pity["weapon_5star_pity"]

                # 获取卡池数据
                if safe_pool_type == "character":
                    cursor.execute(
                        "SELECT Cno, Cname, Grade FROM characters ORDER BY Grade, RAND()"
                    )
                    pool_items = cursor.fetchall()
                else:
                    cursor.execute(
                        "SELECT Wno, Wname, Grade FROM weapons ORDER BY Grade, RAND()"
                    )
                    pool_items = cursor.fetchall()

                for i in range(wish_count):
                    # 更新保底计数
                    current_4star_pity += 1
                    current_5star_pity += 1

                    # 保底机制：80次必出5星，10次必出4星
                    if current_5star_pity >= 80:
                        target_grade = 5
                        current_5star_pity = 0  # 重置5星保底
                        current_4star_pity = 0  # 5星也重置4星保底
                    elif current_4star_pity >= 10:
                        target_grade = 4
                        current_4star_pity = 0  # 重置4星保底
                    else:
                        # 正常概率抽卡
                        rand = random.random()
                        if rand < 0.006:  # 0.6% 概率抽到5星
                            target_grade = 5
                            current_5star_pity = 0  # 重置5星保底
                            current_4star_pity = 0  # 5星也重置4星保底
                        elif rand < 0.057:  # 5.1% 概率抽到4星
                            target_grade = 4
                            current_4star_pity = 0  # 重置4星保底
                        else:  # 其余为3星
                            target_grade = 3

                    # 根据卡池类型和星级选择物品
                    if safe_pool_type == "character":
                        # 角色卡池逻辑
                        if target_grade == 5:
                            # 5星只出角色
                            grade_items = [
                                item for item in pool_items if item["Grade"] == 5
                            ]
                        elif target_grade == 4:
                            # 4星可以出角色或武器 (70%角色, 30%武器)
                            if random.random() < 0.7:
                                grade_items = [
                                    item for item in pool_items if item["Grade"] == 4
                                ]
                            else:
                                # 获取4星武器
                                cursor.execute(
                                    "SELECT Wno, Wname, Grade FROM weapons WHERE Grade = 4"
                                )
                                weapon_items = cursor.fetchall()
                                grade_items = weapon_items
                        else:  # target_grade == 3
                            # 3星出武器（因为角色池没有3星角色）
                            cursor.execute(
                                "SELECT Wno, Wname, Grade FROM weapons WHERE Grade <= 3"
                            )
                            weapon_items = cursor.fetchall()
                            grade_items = weapon_items
                    else:
                        # 武器卡池逻辑：只出武器
                        grade_items = [
                            item for item in pool_items if item["Grade"] == target_grade
                        ]
                        if not grade_items and target_grade == 3:
                            # 如果没有3星武器，选择1-2星武器
                            grade_items = [
                                item for item in pool_items if item["Grade"] <= 3
                            ]

                    # 确保有可选物品
                    if not grade_items:
                        grade_items = pool_items

                    selected_item = random.choice(grade_items)

                    # 生成抽卡记录ID
                    cursor.execute(
                        "SELECT IFNULL(MAX(Wno), 0) + 1 as next_id FROM wishes"
                    )
                    wish_id = cursor.fetchone()["next_id"]

                    # 插入抽卡记录
                    now = datetime.datetime.now()

                    # 判断抽到的是角色还是武器
                    if "Cno" in selected_item:
                        # 抽到角色
                        cursor.execute(
                            """
                            INSERT INTO wishes (Wno, Wuser, Wtype, Wcharacter, Wweapon, Wtime)
                            VALUES (%s, %s, 0, %s, NULL, %s)
                        """,
                            (wish_id, session["user_id"], selected_item["Cno"], now),
                        )
                        results.append(
                            {
                                "type": "character",
                                "name": selected_item["Cname"],
                                "grade": selected_item["Grade"],
                            }
                        )
                    else:
                        # 抽到武器
                        cursor.execute(
                            """
                            INSERT INTO wishes (Wno, Wuser, Wtype, Wcharacter, Wweapon, Wtime)
                            VALUES (%s, %s, 1, NULL, %s, %s)
                        """,
                            (wish_id, session["user_id"], selected_item["Wno"], now),
                        )
                        results.append(
                            {
                                "type": "weapon",
                                "name": selected_item["Wname"],
                                "grade": selected_item["Grade"],
                            }
                        )

                # 更新用户保底计数
                if safe_pool_type == "character":
                    cursor.execute(
                        """
                        UPDATE users 
                        SET character_4star_pity = %s, character_5star_pity = %s 
                        WHERE Uno = %s
                    """,
                        (current_4star_pity, current_5star_pity, session["user_id"]),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE users 
                        SET weapon_4star_pity = %s, weapon_5star_pity = %s 
                        WHERE Uno = %s
                    """,
                        (current_4star_pity, current_5star_pity, session["user_id"]),
                    )

                connection.commit()

                # 添加保底信息到返回结果
                pity_info = {
                    "current_4star_pity": current_4star_pity,
                    "current_5star_pity": current_5star_pity,
                    "next_4star_guarantee": 10 - current_4star_pity,
                    "next_5star_guarantee": 80 - current_5star_pity,
                }

                return jsonify(
                    {
                        "success": True,
                        "results": results,
                        "pity_info": pity_info,
                        "message": f"抽卡成功！获得{len(results)}个道具",
                    }
                )

        except Exception as e:
            connection.rollback()
            return jsonify({"success": False, "message": f"抽卡失败: {str(e)}"})
        finally:
            connection.close()

    return render_template("wish.html")


@app.route("/get_pity_info")
@login_required
@sql_injection_protection
def get_pity_info():
    """获取用户保底信息"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"success": False, "message": "数据库连接失败"})

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT character_4star_pity, weapon_4star_pity, 
                       character_5star_pity, weapon_5star_pity 
                FROM users WHERE Uno = %s
            """,
                (session["user_id"],),
            )
            user_pity = cursor.fetchone()

            if user_pity:
                pity_info = {
                    "character": {
                        "current_4star_pity": user_pity["character_4star_pity"],
                        "current_5star_pity": user_pity["character_5star_pity"],
                        "next_4star_guarantee": 10 - user_pity["character_4star_pity"],
                        "next_5star_guarantee": 80 - user_pity["character_5star_pity"],
                    },
                    "weapon": {
                        "current_4star_pity": user_pity["weapon_4star_pity"],
                        "current_5star_pity": user_pity["weapon_5star_pity"],
                        "next_4star_guarantee": 10 - user_pity["weapon_4star_pity"],
                        "next_5star_guarantee": 80 - user_pity["weapon_5star_pity"],
                    },
                }

                return jsonify({"success": True, "pity_info": pity_info})
            else:
                return jsonify({"success": False, "message": "用户信息不存在"})

    except Exception as e:
        return jsonify({"success": False, "message": f"获取保底信息失败: {str(e)}"})
    finally:
        connection.close()


@app.route("/history")
@login_required
@sql_injection_protection
def history():
    """抽卡记录"""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # 使用安全验证分页参数
    pagination_result = validate_pagination_params(page, per_page)
    safe_page = pagination_result["page"]
    safe_per_page = pagination_result["per_page"]
    offset = (safe_page - 1) * safe_per_page

    connection = get_db_connection()
    if not connection:
        flash("数据库连接失败", "error")
        return redirect(url_for("dashboard"))

    try:
        with connection.cursor() as cursor:
            # 获取总记录数
            cursor.execute(
                "SELECT COUNT(*) as total FROM wishes WHERE Wuser = %s",
                (session["user_id"],),
            )
            total = cursor.fetchone()["total"]

            # 优化的分页查询 - 使用覆盖索引避免JOIN
            cursor.execute(
                """
                SELECT Wtime, Wtype, Wcharacter, Wweapon
                FROM wishes 
                WHERE Wuser = %s
                ORDER BY Wtime DESC
                LIMIT %s OFFSET %s
            """,
                (session["user_id"], safe_per_page, offset),
            )
            wishes_data = cursor.fetchall()

            # 批量获取角色和武器信息
            wishes = []
            if wishes_data:
                character_ids = [
                    w["Wcharacter"] for w in wishes_data if w["Wcharacter"]
                ]
                weapon_ids = [w["Wweapon"] for w in wishes_data if w["Wweapon"]]

                characters = {}
                weapons = {}

                if character_ids:
                    cursor.execute(
                        """
                        SELECT Cno, Cname, Grade 
                        FROM characters 
                        WHERE Cno IN ({})
                    """.format(",".join(["%s"] * len(character_ids))),
                        character_ids,
                    )
                    characters = {c["Cno"]: c for c in cursor.fetchall()}

                if weapon_ids:
                    cursor.execute(
                        """
                        SELECT Wno, Wname, Grade 
                        FROM weapons 
                        WHERE Wno IN ({})
                    """.format(",".join(["%s"] * len(weapon_ids))),
                        weapon_ids,
                    )
                    weapons = {w["Wno"]: w for w in cursor.fetchall()}

                # 组装结果
                for wish in wishes_data:
                    wish_data = {
                        "Wtime": wish["Wtime"],
                        "Wtype": wish["Wtype"],
                        "Cname": None,
                        "CGrade": None,
                        "Wname": None,
                        "WGrade": None,
                    }

                    if wish["Wtype"] == 0 and wish["Wcharacter"] in characters:
                        char = characters[wish["Wcharacter"]]
                        wish_data["Cname"] = char["Cname"]
                        wish_data["CGrade"] = char["Grade"]
                    elif wish["Wtype"] == 1 and wish["Wweapon"] in weapons:
                        weapon = weapons[wish["Wweapon"]]
                        wish_data["Wname"] = weapon["Wname"]
                        wish_data["WGrade"] = weapon["Grade"]

                    wishes.append(wish_data)

            # 计算分页信息
            total_pages = (total + safe_per_page - 1) // safe_per_page
            has_prev = safe_page > 1
            has_next = safe_page < total_pages

    except Exception as e:
        flash(f"获取抽卡记录失败: {str(e)}", "error")
        wishes = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
    finally:
        connection.close()

    return render_template(
        "history.html",
        wishes=wishes,
        page=safe_page,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        total=total,
    )


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5001)
