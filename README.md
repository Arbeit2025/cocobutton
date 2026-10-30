# Cocoa Button

cocoletter の「ココアを呼ぶ」ボタン機能だけを切り出した、単体の小さなツールです。

ボタンを押すとココアのセリフ（24種）がランダムで表示され、押した回数（累計と今日の分）を数えて表示します。連続で同じセリフは出ません。

Single-file Flask + SQLite button app, spun out of cocoletter's cocoa button.

## Features
- 「ココアを呼ぶ」ボタンでセリフをランダム表示（24種・連続重複なし）
- 押した回数のカウント表示（累計／今日）

## Run (local)
pip install -r requirements.txt
python app.py

## Deploy (Render)
cocoletter と同じ構成です。Render でこのリポジトリから Web Service を作り、Start Command を `gunicorn app:app` にすると公開できます（無料プランでは SQLite データは再デプロイ等で消えます）。
