# PromptShareSite

簡易的なプロンプト共有サイトのサンプル実装です。OktaのPrimary認証を行い、MongoDBに保存されたプロンプトを一覧表示します。Flaskベースで実装されています。

## 必要なもの
- Python 3
- MongoDB
- Okta ドメインとAPI設定 (`OKTA_DOMAIN` 環境変数で指定)

## 使い方
1. `pip install -r requirements.txt` で依存パッケージをインストールします。
2. `MONGO_URL` と `OKTA_DOMAIN` を環境変数で設定します。
3. `python app.py` を実行してサーバを起動します。
4. ブラウザで `http://localhost:3000` にアクセスするとログイン画面が表示されます。
   ログイン後は一覧画面 `/prompts` にリダイレクトされ、`/post` から新規投稿が行えます。
5. サイト名やページ名、業務分類を変更したい場合は `config.json` を編集してください。

## 機能
- Oktaに対してユーザ名とパスワードで認証を実施
- プロンプト投稿、一覧、👍評価、コメント投稿、削除
- `config.json` でサイト名やページ名、業務分類を変更可能
- すべてのデータはMongoDBに保存され、ページ表示時に取得されます
