import pytest
import datetime

from unittest.mock import Mock, patch, call

import core.utility as util

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
    '''
        Test convert_date_str functionality. 
    '''
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
    '''
        Test util.sort_tracks behavior.
    '''
    util.sort_tracks(track_list)
    assert expected == track_list

def test_sort_tracks_cannot_sort(mocker):
    '''
        If audio files are ripped from disc, meta data will be lost.
        If metadata is lost (this app assumes it is) then the only reliable way to get accurate metadata is if the files are name numerically.
        While this test case could be sorted in the theory, the application will treat this as a scenario that is not sortable.
        "a", "b", "c" is not a useful sort criteria.
    '''
    track_list = ["tracka.wav", "cover.jpg", "trackb.wav", "trackc.wav"]
    mock_exit = mocker.patch("core.utility.sys.exit")

    util.sort_tracks(track_list)

    assert not mock_exit.assert_called_once()