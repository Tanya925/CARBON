import calendar
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify

from database.db import get_db_connection


analysis = Blueprint("analysis", __name__)


# 數據分析 API：每日碳排圖表
@analysis.route("/api/analysis/daily", methods=["GET"])
def get_daily_analysis():
    try:
        user_id = request.args.get("user_id")
        date_str = request.args.get("date")

        if not user_id or not date_str:
            return jsonify({"error": "缺少必要參數 (user_id 或 date)"}), 400

        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        offset = target_date.isoweekday() % 7
        start_date = target_date - timedelta(days=offset)
        end_date = start_date + timedelta(days=6)

        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                usage_date,
                SUM(carbon_emission) as daily_total
            FROM Traffic_Records
            WHERE user_id = %s AND usage_date BETWEEN %s AND %s
            GROUP BY usage_date
            ORDER BY usage_date ASC
            """,
            (user_id, start_str, end_str)
        )
        records = cursor.fetchall()

        chart_data = []
        for row in records:
            chart_data.append({
                "date": row["usage_date"].strftime("%Y-%m-%d"),
                "total": float(row["daily_total"])
            })

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"成功取得 {start_str} 到 {end_str} 的當週每日數據",
            "data": chart_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 數據分析 API：每週碳排圖表
@analysis.route("/api/analysis/weekly", methods=["GET"])
def get_weekly_analysis():
    try:
        user_id = request.args.get("user_id")
        date_str = request.args.get("date")

        if not user_id or not date_str:
            return jsonify({"error": "缺少必要參數 (user_id 或 date)"}), 400

        target_date = datetime.strptime(date_str[:7], "%Y-%m")
        first_day_of_month = datetime(target_date.year, target_date.month, 1)
        last_day_num = calendar.monthrange(target_date.year, target_date.month)[1]
        last_day_of_month = datetime(target_date.year, target_date.month, last_day_num)

        offset_start = first_day_of_month.isoweekday() % 7
        actual_start_date = first_day_of_month - timedelta(days=offset_start)

        offset_end = 6 - (last_day_of_month.isoweekday() % 7)
        actual_end_date = last_day_of_month + timedelta(days=offset_end)

        start_str = actual_start_date.strftime("%Y-%m-%d")
        end_str = actual_end_date.strftime("%Y-%m-%d")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                YEARWEEK(usage_date, 0) as year_week,
                SUM(carbon_emission) as weekly_total
            FROM Traffic_Records
            WHERE user_id = %s AND usage_date BETWEEN %s AND %s
            GROUP BY year_week
            ORDER BY year_week ASC
            """,
            (user_id, start_str, end_str)
        )
        records = cursor.fetchall()

        chart_data = []
        for idx, row in enumerate(records):
            chart_data.append({
                "week_label": f"第 {idx + 1} 週",
                "year_week_code": str(row["year_week"]),
                "total": float(row["weekly_total"])
            })

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"成功取得 {start_str} 到 {end_str} 的當月每週數據",
            "data": chart_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 數據分析 API：每月碳排圖表
@analysis.route("/api/analysis/monthly", methods=["GET"])
def get_monthly_analysis():
    try:
        user_id = request.args.get("user_id")
        date_str = request.args.get("date")

        if not user_id or not date_str:
            return jsonify({"error": "缺少必要參數 (user_id 或 date)"}), 400

        target_date = datetime.strptime(date_str[:7], "%Y-%m")
        start_month = target_date.month - 2
        start_year = target_date.year

        if start_month <= 0:
            start_month += 12
            start_year -= 1

        start_str = f"{start_year}-{start_month:02d}-01"

        last_day = calendar.monthrange(target_date.year, target_date.month)[1]
        end_str = f"{target_date.year}-{target_date.month:02d}-{last_day}"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                DATE_FORMAT(usage_date, '%Y-%m') as month_label,
                SUM(carbon_emission) as monthly_total
            FROM Traffic_Records
            WHERE user_id = %s AND usage_date BETWEEN %s AND %s
            GROUP BY month_label
            ORDER BY month_label ASC
            """,
            (user_id, start_str, end_str)
        )
        records = cursor.fetchall()

        chart_data = []
        for row in records:
            chart_data.append({
                "month": row["month_label"],
                "total": float(row["monthly_total"])
            })

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"成功取得 {start_str} 到 {end_str} 的前三個月數據",
            "data": chart_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
