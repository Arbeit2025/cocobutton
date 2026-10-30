# ============================================================
# Cocoa Button (single file)
# cocoletter の「ココアを呼ぶ」ボタンだけを切り出した単体ツール。
# ボタンを押すとココアのセリフがランダムで出て、押した回数を数えます。
# ============================================================

# =========================
# [S1] DESIGN
# =========================
HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{{ UI.app_title }}</title>
<style>
body{margin:0;background:#1b120f;color:#fff;font-family:sans-serif;text-align:center;}
.card{background:#fff;color:#000;padding:16px;margin:14px;}
button{padding:12px 20px;font-size:1.1rem;}
#cocoaText{min-height:1.6em;font-size:1.15rem;white-space:pre-wrap;}
</style>
</head>
<body>

<h1>{{ UI.app_title }}</h1>
<p>{{ UI.lead }}</p>

<div class="card">
<button id="cocoaBtn">ココアを呼ぶ</button>
<p id="cocoaText"></p>
<p>
{{ UI.count_label }}：<span id="totalCount">{{ total }}</span>
（{{ UI.today_label }}：<span id="todayCount">{{ today }}</span>）
</p>
</div>

<script>
const lines=[
"あなた、ちゃんと書いてる？",
"今日は少し静かですね。",
"その一言、大事にして。",
"無理しなくていいんですよ。",
"私は見ています。",
"……ふふ、呼びました？",
"おかえりなさい。待っていましたよ。",
"たまには休憩も大事です。",
"今日の言葉、あとで読み返すのが楽しみです。",
"無理に長く書かなくていいんです。短くても、あなたの言葉です。",
"ココアでも淹れましょうか。……気持ちだけですけど。",
"書く手が止まったら、深呼吸をひとつ。",
"その調子です。少しずつで大丈夫。",
"わたしはここにいますよ。",
"今日はどんな一日でした？",
"うまく書けない日もあります。それも記録のうちです。",
"あなたの言葉は、ちゃんと届いています。",
"静かな時間も、悪くないでしょう。",
"ふふ、また呼ばれましたね。",
"続き、気になります。",
"今日の一言が、明日のあなたを助けるかもしれません。",
"肩の力を抜いて。……はい、上手です。",
"書いてくれて、ありがとう。",
"夜更かしはほどほどに、ですよ。"
];
const b=document.getElementById("cocoaBtn");
const t=document.getElementById("cocoaText");
let lastLine=-1;
if(b){b.onclick=()=>{
  let i;do{i=Math.floor(Math.random()*lines.length);}while(lines.length>1&&i===lastLine);
  lastLine=i;t.textContent=lines[i];
  fetch("/count",{method:"POST"}).then(r=>r.json()).then(d=>{
    document.getElementById("totalCount").textContent=d.total;
    document.getElementById("todayCount").textContent=d.today;
  }).catch(()=>{});
};}
</script>

</body>
</html>
"""

# =========================
# [S2] OTHER
# =========================
from flask import Flask, render_template_string, jsonify
import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

# DB file will be created next to this app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("COCOBUTTON_DB_PATH", os.path.join(BASE_DIR, "presses.db"))

UI_TEXT = {
    "app_title": "Cocoa Button",
    "lead": "押すとココアが応えてくれる、ボタンだけの小さなツールです。",
    "count_label": "呼ばれた回数",
    "today_label": "今日",
}

@app.context_processor
def inject():
    return dict(UI=UI_TEXT)

SQL_INIT = """
CREATE TABLE IF NOT EXISTS presses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pressed_at TEXT NOT NULL
)
"""

def db():
    # check_same_thread=False is safe here because we open/close per request
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def db_init():
    with db() as c:
        c.execute(SQL_INIT)

def today_str() -> str:
    return datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")

def db_counts():
    with db() as c:
        total = c.execute("SELECT COUNT(*) FROM presses").fetchone()[0]
        today = c.execute(
            "SELECT COUNT(*) FROM presses WHERE pressed_at LIKE ?",
            (today_str() + "%",),
        ).fetchone()[0]
    return total, today

def db_press():
    now = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
    with db() as c:
        c.execute("INSERT INTO presses(pressed_at) VALUES(?)", (now,))
    return db_counts()

# init table on import
db_init()

# =========================
# [S3] RUN
# =========================
@app.route("/")
def index():
    total, today = db_counts()
    return render_template_string(HTML, total=total, today=today)

@app.route("/count", methods=["POST"])
def count():
    total, today = db_press()
    return jsonify({"total": total, "today": today})

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
