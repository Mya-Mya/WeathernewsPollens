from flask import Flask, render_template, abort, redirect, url_for
from datetime import date, datetime
from repository import Store, EMPTY_VALUE
from pathlib import Path
from argparse import ArgumentParser

CITYCODES = {}
citycode_bookmark_text = Path("./CitycodeBookmark.txt").read_text(encoding="utf-8").strip()
for row in citycode_bookmark_text.splitlines():
    code, name = row.split(" ", maxsplit=1)
    CITYCODES[code] = name

app = Flask(__name__)


@app.route("/")
def index():
    """観測地点の一覧を表示"""
    return render_template("welcome.html", cities=CITYCODES)


def handle_detail(citycode, date_str):
    """指定された日付の花粉量を表示"""
    if citycode not in CITYCODES:
        abort(404, description="City code not found")

    try:
        target_date = datetime.strptime(date_str, "%Y%m%d").date()
    except ValueError:
        abort(400, description="Invalid date format")

    store = Store(citycode)
    record = store.get_day_record(target_date)

    if record is None:
        # データの取得に失敗した場合
        total = "N/A"
        hourly_data = [(h, EMPTY_VALUE) for h in range(24)]
    else:
        # 合計値の計算（全てEMPTY_VALUEならN/A）
        valid_values = [v for v in record if v != EMPTY_VALUE]
        total = sum(valid_values) if valid_values else "N/A"

        # テンプレートに渡すために時間(0-23)と値をセットにする
        hourly_data = list(enumerate(record))

    return render_template(
        "detail.html",
        city_name=CITYCODES[citycode],
        citycode=citycode,
        target_date=target_date,
        total=total,
        hourly_data=hourly_data,
        EMPTY_VALUE=EMPTY_VALUE,
    )


@app.route("/<citycode>/today")
def today(citycode):
    """今日のデータを表示するパスへリダイレクト、または直接表示"""
    today_str = date.today().strftime("%Y%m%d")
    return handle_detail(citycode, today_str)


@app.route("/<citycode>/<date_str>")
def theday(citycode, date_str):
    return handle_detail(citycode, date_str)


if __name__ == "__main__":
    parser = ArgumentParser(description="Weathernews Pollens Webアプリ")
    parser.add_argument("--port", type=int, default=80, help="ポート番号")
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, debug=False)
