import pandas as pd

from ninetydf import couples, seasons
from ninetydf.data import _load_data


def _validate_dataframe(df, expected_columns):
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    for column in expected_columns:
        assert column in df.columns


def test_load_couples():
    _validate_dataframe(couples, ["show_id", "couple_name"])

    assert couples.loc[0, "show_id"] == "90df"
    assert couples.loc[0, "couple_name"] == "Russ & Paola"


def test_load_seasons():
    _validate_dataframe(seasons, ["show_id", "season", "start_date", "end_date"])

    assert seasons.loc[0, "show_id"] == "90df"
    assert seasons.loc[0, "season"] == 1
    assert seasons.loc[0, "start_date"] == "2014-01-12"
    assert seasons.loc[0, "end_date"] == "2014-02-23"


def test_load_data_function():
    df = _load_data("seasons.csv")
    _validate_dataframe(df, ["show_id", "season", "start_date", "end_date"])
