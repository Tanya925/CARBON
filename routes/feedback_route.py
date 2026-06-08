# 功能：讓已登入使用者送出一筆問題或意見回饋，存進 Feedback_Forms 資料表。

from flask import Blueprint, request, jsonify, session

from database.db import get_db_connection


feedback = Blueprint("feedback", __name__)


# 使用者送出問題或意見回饋
@feedback.route("/api/feedback", methods=["POST"])
def add_feedback():

    # 先檢查使用者是否登入
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "尚未登入"
        }), 401

    # 取得前端送來的 JSON 資料。例如前端會傳送：
    # {
    # "question_content": "希望可以新增匯出 Excel 功能"
    # }
    # 這行會拿到一個 Python 字典：
    # data = {
    #     "question_content": "希望可以新增匯出 Excel 功能"
    # }
    data = request.get_json()

    question_content = data.get("question_content")  # 從 data 中取得 question_content（使用者的問題或意見回饋內容）

    # 如果沒取到代表裡面沒內容，就回傳錯誤給前端
    if not question_content:
        return jsonify({
            "success": False,
            "message": "請輸入回饋內容"
        }), 400

    user_id = session["user_id"]  # 取得目前登入者的 user_id（因為回饋表 Feedback_Forms 裡面有：user_id，用來表示這筆回饋紀錄屬於哪個使用者）

    conn = get_db_connection()  # 連接 MySQL
    cursor = conn.cursor(dictionary=True)  # 建立 cursor 物件，是拿來執行 SQL 指令的工具。dictionary=True 的意思是查詢結果會長得像字典，因為本來是 tuple（例如：("Daniel", "1234")）

    # 新增一筆回饋資料到資料庫！
    cursor.execute(
        """
        INSERT INTO Feedback_Forms
        (
            user_id,
            question_content
        )
        VALUES
        (
            %s,
            %s
        )
        """,
        (
            user_id,
            question_content
        )
    )

    conn.commit()  # 確認寫入資料庫

    # 關閉 cursor 和連線
    cursor.close()
    conn.close()

    # 回傳成功 JSON 格式的資料給前端
    return jsonify({
        "success": True,
        "message": "回饋送出成功"
    }), 201