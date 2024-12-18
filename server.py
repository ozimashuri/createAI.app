from fastapi import (
    FastAPI,
    HTTPException,
)  # FastAPIフレームワークの基本機能とエラー処理用のクラス
from fastapi.middleware.cors import CORSMiddleware  # CORSを有効にするためのミドルウェア
from pydantic import BaseModel  # データのバリデーション（検証）を行うための基本クラス
from typing import Optional, List # 省略可能な項目を定義するために使用
import sqlite3  # SQLiteデータベースを使用するためのライブラリ
from datetime import datetime

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI()


# corsを無効化（開発時のみ）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# データベースの初期設定を行う関数
def init_db():
    # SQLiteデータベースに接続（ファイルが存在しない場合は新規作成）
    with sqlite3.connect("travel_planner.db") as conn:
        # TODOを保存するテーブルを作成（すでに存在する場合は作成しない）
        # 自動増分する一意のID（INTEGER PRIMARY KEY AUTOINCREMENT）
        # TODOのタイトル（TEXT NOT NULL）
        # 完了状態（BOOLEAN DEFAULT FALSE）
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                cost REAL NOT NULL,
                location TEXT NOT NULL,
                notes TEXT,
                completed BOOLEAN DEFAULT FALSE
            )
        """)

        # ほしいものリストテーブル
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                priority INTEGER DEFAULT 1,
                purchased BOOLEAN DEFAULT FALSE
            )
        """)


# アプリケーション起動時にデータベースを初期化
init_db()


# リクエストボディのデータ構造を定義するクラス
class ActivityBase(BaseModel):
    title: str  # TODOのタイトル（必須）
    start_time: str
    duration: int
    cost: float
    location: str
    notes: Optional[str] = None  # 完了状態（省略可能、デフォルトは未完了）


# レスポンスのデータ構造を定義するクラス（TodoクラスにIDを追加）
class Activity(ActivityBase):
    id: int  # TODOのID
    completed: bool = False

#ウィッシュリストを作成する
class WishlistItemBase(BaseModel):
    name: str
    price: float
    priority: int = 1

class WishlistItem(WishlistItemBase):
    id: int
    purchased: bool = False


# 新規TODOを作成するエンドポイント
@app.post("/activities", response_model=Activity)
def create_activity(activity: ActivityBase):
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO activities (title, start_time, duration, cost, location, notes, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (activity.title, activity.start_time, activity.duration, 
             activity.cost, activity.location, activity.notes, False)
        )
        conn.commit()
        activity_id = cursor.lastrowid # 新しく作成されたTODOのIDを取得
        return {**activity.dict(), "id": activity_id, "completed": False}



@app.get("/activities", response_model=List[Activity])
def get_activities():
    with sqlite3.connect("travel_planner.db") as conn:
        cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
        created = cursor.fetchone()
        return {
            "id": created[0],
            "title": created[1],
            "start_time": created[2],
            "duration": created[3],
            "cost": created[4],
            "location": created[5],
            "notes": created[6],
            "completed": bool(created[7])
        }


# 全てのTODOを取得するエンドポイント
@app.post("/wishlist", response_model=WishlistItem)
def create_wishlist_item(item: WishlistItemBase):
    with sqlite3.connect("travel_planner.db") as conn:
        cursor = conn.execute(
            """
            INSERT INTO wishlist (name, price, priority)
            VALUES (?, ?, ?)
            """,
            (item.name, item.price, item.priority)
        )
        item_id = cursor.lastrowid
        return {**item.dict(), "id": item_id, "purchased": False}

@app.get("/wishlist", response_model=List[WishlistItem])
def get_wishlist():
    with sqlite3.connect("travel_planner.db") as conn:
        cursor = conn.execute("SELECT * FROM wishlist ORDER BY priority DESC")
        items = cursor.fetchall()
        return [
            {
                "id": i[0],
                "name": i[1],
                "price": i[2],
                "priority": i[3],
                "purchased": bool(i[4])
            }
            for i in items
        ]

@app.put("/activities/{activity_id}/complete")
def complete_activity(activity_id: int):
    with sqlite3.connect("travel_planner.db") as conn:
        cursor = conn.execute(
            "UPDATE activities SET completed = TRUE WHERE id = ?",
            (activity_id,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Activity not found")
        return {"message": "Activity marked as complete"}

@app.put("/wishlist/{item_id}/purchase")
def purchase_item(item_id: int):
    with sqlite3.connect("travel_planner.db") as conn:
        cursor = conn.execute(
            "UPDATE wishlist SET purchased = TRUE WHERE id = ?",
            (item_id,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item marked as purchased"}

@app.get("/financial-summary")
def get_financial_summary():
    with sqlite3.connect("travel_planner.db") as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(cost) FROM activities')
        activities_cost = cursor.fetchone()[0] or 0

        cursor.execute('SELECT SUM(price) FROM wishlist')
        wishlist_cost = cursor.fetchone()[0] or 0

        cursor.execute('''
            SELECT 
                (SELECT COALESCE(SUM(cost), 0) FROM activities WHERE completed = 1) +
                (SELECT COALESCE(SUM(price), 0) FROM wishlist WHERE purchased = 1)
        ''')
        spent_money = cursor.fetchone()[0] or 0

        total_budget = activities_cost + wishlist_cost

        return {
            "total_budget": total_budget,
            "spent_money": spent_money,
            "remaining_budget": total_budget - spent_money
        }
        @app.get("/debug/database")
def debug_database():
    with sqlite3.connect("travel_planner.db") as conn:
        cursor = conn.cursor()

        # テーブル構造の確認
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        # データの確認
        activities = cursor.execute("SELECT * FROM activities").fetchall()
        wishlist = cursor.execute("SELECT * FROM wishlist").fetchall()

        return {
            "tables": tables,
            "activities": activities,
            "wishlist": wishlist
        }