# camenashi_san
- ねこちゃんおトイレ監視の[かめなしくん](https://github.com/showgayaki/camenashi_kun)からのPOSTを受け取ってデータベースに登録
- ユーザーからのPOSTに応じて集計、リプライする

Discord Botです。  

こんな感じ  
![camenashi](https://github.com/user-attachments/assets/14c953bc-9c15-49ff-838c-045da8f5e427)

## データベース
絵文字をUNIQUE制約で登録するため、区別できる照合順序で作成する必要があります。  
```
CREATE DATABASE IF NOT EXISTS camenashi DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
```
devのときは、`docker/camenashi_db/init.sql`  
として保存しておくと、Docker初回起動時にデータベースが作成されます。

## envサンプル
devのときは`env.dev`  
prodのときは`env.prod`  
としてルートディレクトリに保存しておく。  
```
ENVIRONMENT=dev or prod  # 実行環境
NON_MONITORED_CHANNEL_ID=  # リプライしないチャンネル(本番用チャンネルを除くため、prodの場合は記載なしでOK)
DISCORD_TOKEN=  # Discord Botのトークン
DISCORD_GUILD_ID=  # サーバーのID
DISCORD_ADMIN_CHANNEL_ID=  # 管理用チャンネルのID
MENTION_ID=  # かめなしさん(app)のID

DB_ROOT_PASS=  # データベースのrootパスワード
DB_HOST=camenashi_db  # データベースホスト名
DB_PORT=33061  # データベースのポート番号
DB_USER=  # データベースのユーザー名
DB_PASS=  # DB_USERのパスワード
DB_NAME=camenashi  # データーベース名
```

## Docker実行
@dev  
`docker compose --env-file .env.dev -f docker/compose.dev.yml up -d --build`

@prod  
`docker compose -f docker/compose.yml up -d --build`  
