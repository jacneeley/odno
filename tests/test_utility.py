import pytest
import datetime

from unittest.mock import Mock, patch, call

import src.utility as util

@pytest.mark.parametrize("date_time, expected",[
    (
        "1988-01-01", datetime.datetime.strptime("1988-01-01", "%Y-%m-%d")
    ),
    (
        "1991-05-26", datetime.datetime.strptime("1991-05-26", "%Y-%m-%d")
    ),
    (
        "1991-01", datetime.datetime.strptime("1991-01", "%Y-%m")
    ),
    (
        "1988", datetime.datetime.strptime("1988", "%Y")
    )
])
def test_convert_date_str(date_time: str, expected: datetime):
    date_str = util.convert_date_str(date_time)
    assert date_str == expected

@pytest.mark.parametrize("track_list, expected", [
    (
        ["track1.wav", "track5.wav", "track2.wav"],
        ["track1.wav", "track2.wav", "track5.wav"]
    ),
    (
        ["1-track.wav", "5-track.wav", "2-track.wav"],
        ["1-track.wav", "2-track.wav", "5-track.wav"]
    ),
    (
        ["1_track.wav", "5_track.wav", "2_track.wav"],
        ["1_track.wav", "2_track.wav", "5_track.wav"]
    ),
    (
        ["1_track.wav", "cover.jpg", "5_track.wav", "2_track.wav"],
        ["1_track.wav", "2_track.wav", "5_track.wav"]
    )
])
def test_sort_tracks(track_list, expected):
    util.sort_tracks(track_list)
    assert expected == track_list

def test_sort_tracks_cannot_sort(mocker):
    track_list = ["tracka.wav", "cover.jpg", "trackb.wav", "trackc.wav"]
    mock_get = mocker.patch("src.utility.sys.exit")

    util.sort_tracks(track_list)

    mock_get.assert_called_once()