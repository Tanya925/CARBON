from flask import Blueprint, jsonify

from database.db import get_db_connection  # 從自己的 database/db.py 匯入資料庫連線函式


transport = Blueprint("transport", __name__)


# 取得所有交通工具
@transport.route("/api/transports", methods=["GET"])
def get_transports():

    conn = get_db_connection()  # 建立 MySQL 連線
    cursor = conn.cursor(dictionary=True)  # 建立 cursor 物件，是拿來執行 SQL 指令的工具。dictionary=True 的意思是查詢結果會長得像字典，因為本來是 tuple（例如：("Daniel

    # 執行 SQL 指令（從 Vehicles 資料表中，查出交通工具ID、交通工具名稱，並依照 vehicle_id 排序）
    cursor.execute(
        """
        SELECT
            vehicle_id,
            vehicle_name
        FROM Vehicles
        ORDER BY vehicle_id
        """
    )

    vehicles = cursor.fetchall()  # 拿出查詢結果的所有資料（會是一個 list，裡面每一筆資料都是一個字典，例如： [{"vehicle_id": 1, "vehicle_name": "汽車"}, {"vehicle_id": 2, "vehicle_name": "機車"}]）

    # 關閉 cursor 和連線
    cursor.close()
    conn.close()

    # 回傳 JSON 格式的資料給前端
    return jsonify({
        "success": True,
        "transports": vehicles
    })