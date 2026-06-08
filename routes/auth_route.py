# 功能：使用者註冊、登入、登出、確認目前登入者的 API

from flask import Blueprint  # Blueprint ：一組路由的分類資料夾（現在把登入相關 API 放在 auth_routes.py，就是用 Blueprint 讓 app.py 不用塞一堆 route）
from flask import request, jsonify, session  # request：用來處理 HTTP 請求的資料，jsonify：用來將 Python 資料轉換成 JSON 格式，session：用來管理使用者的 session 資料

from database.db import get_db_connection  # 匯入資料庫連線函式（之後只要寫：conn = get_db_connection() 就可以連到 MySQL）

# 建立一個 Blueprint，名字叫 auth
# auth 是一組登入相關 API 的集合。之後在 app.py 裡面會用： app.register_blueprint(auth) 把這組 API 掛到 Flask 主程式上
auth = Blueprint("auth", __name__)


# 1. 註冊 API
@auth.route("/api/register", methods=["POST"])
def register():

    # 取得前端送來的 JSON 資料
    # 例如前端送：
    # {
    # "username": "Daniel",
    # "password": "123456"
    # }

    # 這行會把它變成 Python 字典：

    # data = {
    #     "username": "Daniel",
    #     "password": "123456"
    # }
    data = request.get_json()  

    username = data.get("username")  # 從 data 字典裡面取出 username 的值，存在 username 變數裡面
    password = data.get("password")  # 從 data 字典裡面取出 password 的值，存在 password 變數裡面

    # 判斷有沒有少填
    if not username or not password:

        # 回傳錯誤訊息給前端(格式是 JSON)
        return jsonify({
            "success": False,
            "message": "請輸入完整"
        }), 400

    conn = get_db_connection()  # 建立 MySQL 連線
    cursor = conn.cursor(dictionary=True)  # 建立 cursor 物件，是拿來執行 SQL 指令的工具。dictionary=True 的意思是查詢結果會長得像字典，因為本來是 tuple（例如：("Daniel", "123456")），加了 dictionary=True 之後就會變成 {"username": "Daniel", "password": "123456"}，這樣就比較好讀懂。

    # 用來檢查這個 username 有沒有已經被註冊
    cursor.execute(
        "SELECT * FROM Users WHERE username=%s",
        (username,)
    )

    user = cursor.fetchone()  # 拿出查詢結果的第一筆資料（有找到的畫會是一筆資料；沒找到則會是 None）

    # 如果 user 有資料，代表使用者名稱已經存在
    if user:

        # 關閉 cursor 和資料庫連線
        cursor.close()
        conn.close()

        # 回傳錯誤訊息給前端，告訴他使用者名稱已經存在了(回傳格式是 JSON，裡面 success 是 False，message 是 "使用者已存在")，HTTP 狀態碼是 409（代表衝突，Conflict）
        return jsonify({
            "success": False,
            "message": "使用者已存在"
        }), 409

    # 不進行加密直接存入資料庫
    cursor.execute(
        """
        INSERT INTO Users
        (username,user_password)
        VALUES(%s,%s)
        """,
        (
            username,
            password
        )
    )

    conn.commit()  # 確認寫入資料庫！

    # 關閉 cursor 和資料庫連線
    cursor.close()
    conn.close()

    # 回傳註冊成功的訊息給前端(格式是 JSON，裡面 success 是 True)
    return jsonify({
        "success": True,
        "message": "註冊成功"
    })


# 2. 登入 API
@auth.route("/api/login", methods=["POST"])
def login():

    # 取得前端送來的 JSON 資料（會是包含 username 和 password 的字典）
    data = request.get_json()

    username = data.get("username")  # 從 data 字典裡面取出 username 的值，存在 username 變數裡面
    password = data.get("password")  # 從 data 字典裡面取出 password 的值，存在 password 變數裡面

    # 連接資料庫，並建立 cursor 物件
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 查詢資料庫，看看有沒有這個 username 的使用者
    cursor.execute(
        """
        SELECT *
        FROM Users
        WHERE username=%s
        """,
        (username,)
    )

    user = cursor.fetchone()  # 拿出查詢結果的第一筆資料（有找到的話會是一筆資料；沒找到就是 None）

    # 如果 user 是 None，代表沒有找到這個使用者名稱，所以登入會失敗
    if user is None:

        # 關閉 cursor 和資料庫連線
        cursor.close() 
        conn.close() 
        
        # 回傳登入失敗
        return jsonify({
            "success": False,
            "message": "使用者不存在"
        }), 401

    # 檢查明文密碼
    if user["user_password"] != password:

        # 關閉 cursor 和資料庫連線
        cursor.close()
        conn.close()

        # 回傳登入失敗
        return jsonify({
            "success": False,
            "message": "密碼錯誤"
        }), 401

    # 登入成功後，把 "使用者 ID"、"使用者名稱" 存進 session，這樣之後就可以知道目前是誰登入了
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]

    # 關閉 cursor 和資料庫連線
    cursor.close()
    conn.close()

    # 回傳登入成功的訊息給前端(格式是 JSON，裡面 success 是 True)
    return jsonify({
        "success": True,
        "message": "登入成功"
    })


# 3. 登出 API
@auth.route("/api/logout", methods=["POST"])
def logout():

    session.clear()  # 清空 session，代表使用者已經登出

    # 回傳登出成功
    return jsonify({
        "success": True,
        "message": "已登出"
    })


# 4. 取得目前登入者 API
@auth.route("/api/me")
def me():

    # 先檢查 session 裡有沒有 user_id（如果沒有，代表目前沒有登入）
    if "user_id" not in session:

        # 回傳尚未登入
        return jsonify({
            "success": False,
            "message": "尚未登入"
        }), 401

    # 否則代表有登入了，就回傳目前登入者資料
    return jsonify({
        "success": True,
        "user": {
            "id": session["user_id"],
            "name": session["username"]
        }
    })