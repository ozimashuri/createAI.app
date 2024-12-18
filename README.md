# 考え方

1. **要件定義**
   - まず作りたいアプリケーションの目的を明確にする
   - どんなデータを扱いたいか考える（例：TODO管理→レシピ管理、メモ帳、家計簿など）
   - どんな機能が必要か洗い出す（基本的なCRUD操作に加えて必要な機能）

2. **データモデルの設計**
   - 保存したいデータの構造を決める
   - テーブル設計（必要なカラムとその型を決める）
   - サンプルコードのTodoクラスを参考に、自分のデータモデルを定義

3. **基本的なCRUD操作の実装**
   - サンプルコードを参考に、以下の基本機能を実装：
     - Create（データの作成）
     - Read（データの読み取り）
     - Update（データの更新）
     - Delete（データの削除）

4. **追加機能の実装(余裕あれば)**
   - 基本機能ができたら、オリジナルの機能を追加
   - 例えば：
     - 検索機能
     - データのフィルタリング
     - ソート機能
     - カテゴリ分け

5. **エラーハンドリングの追加(余裕あれば)**
   - ユーザーの入力チェック
   - エラーメッセージの改善
   - 例外処理の追加

具体例として、簡単なレシピ管理アプリケーションを作る場合の流れを見てみましょう：

1. **要件定義の例**
レシピ管理アプリケーション
- レシピの登録、表示、更新、削除ができる
- レシピには料理名、材料、手順、調理時間を登録できる
- カテゴリ（和食、洋食など）で分類できる
- 調理時間で検索できる

2. **データモデルの設計例**
```python
from pydantic import BaseModel
from typing import List, Optional

class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[str]
    cooking_time: int  # 分単位
    category: str
```

3. **データベース設計例**
```python
def init_db():
    with sqlite3.connect('recipes.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ingredients TEXT NOT NULL,  # JSON形式で保存
                steps TEXT NOT NULL,        # JSON形式で保存
                cooking_time INTEGER NOT NULL,
                category TEXT NOT NULL
            )
        ''')
```

4. **基本的なエンドポイントの実装例**
```python
# レシピの新規作成
@app.post("/recipes", response_model=RecipeResponse)
def create_recipe(recipe: Recipe):
    # 実装内容

# レシピの検索（調理時間でフィルタリング）
@app.get("/recipes/search")
def search_recipes(max_time: Optional[int] = None):
    # 実装内容
```

段階的に機能を追加していくことで、複雑なアプリケーションも整理して実装することができます。

アドバイス：
1. まずは小さな機能から始める
2. 動作確認を細かく行う
3. 機能を少しずつ追加する
4. エラーが出たら、エラーメッセージをよく読んで対処する
5. コードにコメントを書いて、後で見返したときに理解できるようにする

# ライブラリのインストール
```bash
pip install -r requirements.txt
```

# サーバーを起動するコマンド
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```