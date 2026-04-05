import urllib.parse
import urllib.request
from pathlib import Path
import csv, io
from datetime import date, datetime

EMPTY_VALUE = -9999


def get_date_str(d: date) -> str:
    """
    日付オブジェクトを`Store`のキャッシュディレクトリ名用の "yy.mm.dd" 形式に変換します。

    Parameters
    -----------
    d : date
        日付オブジェクト。
    """
    return d.strftime("%y.%m.%d")


def get_date_wn_str(d: date) -> str:
    """
    日付オブジェクトをAPIクエリ用の "YYYYMMDD" 形式に変換します。

    Parameters
    -----------
    d : date
        変換対象の日付オブジェクト。
    """
    return d.strftime("%Y%m%d")


class Store:
    def __init__(self, citycode: str):
        """
        指定された市区町村コードでStoreを初期化します。

        Parameters
        -----------
        citycode : str
            市区町村コード（Weathernews APIで使用）。
        """
        self.citycode = citycode
        self.citypath = Path(f"./Cache/{self.citycode}")

    def get_daypath(self, d: date) -> Path:
        """
        特定の日付に対応するキャッシュファイルのパスを取得します。
        必要に応じてディレクトリを作成します。

        Parameters
        -----------
        d : date
            対象の日付。
        """
        date_str = get_date_str(d)
        self.citypath.mkdir(exist_ok=True, parents=True)
        datepath = self.citypath / date_str
        return datepath

    def get_day_record(self, d: date, force_update: bool = False) -> list[int] | None:
        """
        指定した日付の1日分（24時間）のデータを取得します。
        キャッシュがない場合やデータが未更新の場合はAPIから取得します。

        Parameters
        -----------
        d : date
            取得したい日付。
        force_update : bool, optional
            キャッシュの有無にかかわらず強制的にAPIから再取得するかどうか。
        """
        record = None

        if not force_update:
            try:
                record = self.read_day_record(d)
            except:
                pass

        current_h = datetime.now().hour
        should_update = (record is None) or (
            d == date.today() and record[current_h] < 0
        )

        if force_update or should_update:
            self.update_data(d, d)
            record = self.get_day_record(d)
        return record

    def write_day_record(self, d: date, record: list[int]):
        """
        1日分のデータをスペース区切りのテキスト形式でキャッシュに保存します。

        Parameters
        -----------
        d : date
            保存対象の日付。
        record : list[int]
            24時間分のデータを含む整数のリスト。
        """
        daypath = self.get_daypath(d)
        daypath.write_text(" ".join(map(str, record)))

    def read_day_record(self, d: date) -> list[int]:
        """
        キャッシュファイルから1日分のデータを読み込みます。

        Parameters
        -----------
        d : date
            読み込み対象の日付。
        """
        daypath = self.get_daypath(d)
        assert daypath.exists(), f"The day record file {daypath} does not exist."
        text = daypath.read_text()
        record = list(map(int, text.split()))
        assert len(record) == 24, f"Expected 24 hours of data in {d}."
        return record

    def update_data(self, start: date, end: date):
        """
        指定された期間のデータをAPIから取得し、キャッシュを更新します。

        Parameters
        -----------
        start : date
            更新開始日。
        end : date
            更新終了日。
        """
        new_records = self.fetch_data(start, end)
        for d, record in new_records.items():
            self.write_day_record(d, record)

    def fetch_data(self, start: date, end: date) -> dict[date, list[int]]:
        """
        WeathernewsのオープンデータAPIから花粉飛散量データを取得します。

        Parameters
        -----------
        start : date
            データ取得の開始日。
        end : date
            データ取得の終了日。
        """
        start_str = get_date_wn_str(start)
        end_str = get_date_wn_str(end)
        query_parameter_clause = urllib.parse.urlencode(
            {"citycode": self.citycode, "start": start_str, "end": end_str}
        )
        url = (
            "https://wxtech.weathernews.com/opendata/v1/pollen"
            + "?"
            + query_parameter_clause
        )
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as connection:
            body = connection.read()
        file = io.StringIO()
        file.write(body.decode())
        file.seek(0)
        reader = csv.DictReader(file)
        new_records = {}
        for row in reader:
            dt = datetime.fromisoformat(row["date"])
            d = dt.date()
            if d not in new_records:
                new_records[d] = [EMPTY_VALUE for _ in range(24)]
            h = dt.hour
            new_records[d][h] = int(row["pollen"])
        return new_records
