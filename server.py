from fastapi import (
    FastAPI,
    HTTPException,
)  # FastAPIフレームワークの基本機能とエラー処理用のクラス
from fastapi.middleware.cors import CORSMiddleware  # CORSを有効にするためのミドルウェア
from pydantic import BaseModel  # データのバリデーション（検証）を行うための基本クラス
from typing import Optional  # 省略可能な項目を定義するために使用
import sqlite3  # SQLiteデータベースを使用するためのライブラリ

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
    with sqlite3.connect("todos.db") as conn:
        # TODOを保存するテーブルを作成（すでに存在する場合は作成しない）
        # 自動増分する一意のID（INTEGER PRIMARY KEY AUTOINCREMENT）
        # TODOのタイトル（TEXT NOT NULL）
        # 完了状態（BOOLEAN DEFAULT FALSE）
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            )
        """
        )


# アプリケーション起動時にデータベースを初期化
init_db()


# リクエストボディのデータ構造を定義するクラス
class Todo(BaseModel):
    title: str  # TODOのタイトル（必須）
    completed: Optional[bool] = False  # 完了状態（省略可能、デフォルトは未完了）


# レスポンスのデータ構造を定義するクラス（TodoクラスにIDを追加）
class TodoResponse(Todo):
    id: int  # TODOのID


# 新規TODOを作成するエンドポイント
@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: Todo):
    with sqlite3.connect("todos.db") as conn:
        cursor = conn.execute(
            # SQLインジェクション対策のためパラメータ化したSQL文を使用
            "INSERT INTO todos (title, completed) VALUES (?, ?)",
            (todo.title, todo.completed),
        )
        todo_id = cursor.lastrowid  # 新しく作成されたTODOのIDを取得
        return {"id": todo_id, "title": todo.title, "completed": todo.completed}


# 全てのTODOを取得するエンドポイント
@app.get("/todos")
def get_todos():
    with sqlite3.connect("todos.db") as conn:
        todos = conn.execute("SELECT * FROM todos").fetchall()  # 全てのTODOを取得
        # データベースから取得したタプルをJSON形式に変換して返す
        return [{"id": t[0], "title": t[1], "completed": bool(t[2])} for t in todos]


# 指定されたIDのTODOを取得するエンドポイント
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    with sqlite3.connect("todos.db") as conn:
        # 指定されたIDのTODOを検索
        todo = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not todo:  # TODOが見つからない場合は404エラーを返す
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"id": todo[0], "title": todo[1], "completed": bool(todo[2])}


# 指定されたIDのTODOを更新するエンドポイント
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: Todo):
    with sqlite3.connect("todos.db") as conn:
        # タイトルと完了状態を更新
        cursor = conn.execute(
            "UPDATE todos SET title = ?, completed = ? WHERE id = ?",
            (todo.title, todo.completed, todo_id),
        )
        if cursor.rowcount == 0:  # 更新対象のTODOが存在しない場合は404エラーを返す
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"id": todo_id, "title": todo.title, "completed": todo.completed}


# 指定されたIDのTODOを削除するエンドポイント
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with sqlite3.connect("todos.db") as conn:
        # 指定されたIDのTODOを削除
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:  # 削除対象のTODOが存在しない場合は404エラーを返す
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"message": "Todo deleted"}
