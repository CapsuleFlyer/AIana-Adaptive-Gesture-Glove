"""Tests for the acquisition layer. Run from the repo root:  python -m pytest tests -q
(needs `src` on the path: set PYTHONPATH=src, or run `pip install -e .` once we add packaging)."""
import itertools

import numpy as np

from aiana.acquisition import (FakeSource, N_CHANNELS, ReplaySource, StreamStats, Windower,
                               parse_line, resample_window)

GOOD = "S,5,100,1500,1510,1490,1505,1520,10,-20,8192,3,-4,5"


def test_parse_good_line():
    s = parse_line(GOOD)
    assert s.seq == 5 and s.t_ms == 100
    assert s.values.shape == (N_CHANNELS,)
    assert s.values[0] == 1500 and s.values[7] == 8192 and s.values[10] == 5


def test_parse_rejects_bad_lines():
    assert parse_line("") is None
    assert parse_line("#AIANA,fw=1,rate_hz=50") is None
    assert parse_line("S,1,2,3") is None                                   # too short
    assert parse_line("S,5,100,1500,1510,1490,1505,x,10,-20,8192,3,-4,5") is None   # not a number
    assert parse_line("S,5,100,9999,1510,1490,1505,1520,10,-20,8192,3,-4,5") is None  # ADC out of range
    assert parse_line("S,5,100,1500,1510,1490,1505,1520,99999,-20,8192,3,-4,5") is None  # not int16
    assert parse_line("X," + GOOD[2:]) is None


def test_stream_stats_counts_drops_and_resync():
    st = StreamStats()
    for seq in [0, 1, 2, 5, 6]:     # 3 and 4 are missing
        st.good(seq)
    assert st.total == 5 and st.drops == 2
    st.good(0)                       # board rebooted: resync, no drop counted
    assert st.drops == 2
    st.bad_line()
    assert st.bad == 1


def test_fake_source_shape_labels_and_range():
    src = FakeSource(seed=1)
    samples = list(itertools.islice(src.read_samples(), 500))
    assert [s.seq for s in samples] == list(range(500))
    arr = np.stack([s.values for s in samples])
    assert arr.shape == (500, N_CHANNELS)
    assert arr[:, :5].min() >= 0 and arr[:, :5].max() <= 4095
    # fist should read higher than idle on the flex channels
    src = FakeSource(schedule=[("idle", 2.0), ("fist", 2.0)], seed=2, loop=False)
    arr = np.stack([s.values for s in src.read_samples()])
    assert arr[150:200, :5].mean() > arr[50:100, :5].mean() + 500


def test_fake_source_is_reproducible():
    a = [s.values for s in itertools.islice(FakeSource(seed=3).read_samples(), 50)]
    b = [s.values for s in itertools.islice(FakeSource(seed=3).read_samples(), 50)]
    assert np.array_equal(np.stack(a), np.stack(b))


def test_windower_counts_and_shape():
    w = Windower(length=100, hop=10)
    out = [w.push(s) for s in itertools.islice(FakeSource().read_samples(), 200)]
    windows = [o for o in out if o is not None]
    # first window at sample 100, then every 10 samples: 100,110,...,200 -> 11 windows
    assert len(windows) == 11
    assert windows[0].shape == (100, N_CHANNELS) and windows[0].dtype == np.float32
    assert out[98] is None and out[99] is not None


def test_windower_window_is_most_recent_samples():
    src = list(itertools.islice(FakeSource(seed=4).read_samples(), 130))
    w = Windower(length=100, hop=10)
    last = None
    for s in src:
        r = w.push(s)
        if r is not None:
            last = r
    assert np.array_equal(last, np.stack([s.values for s in src[30:130]]))


def test_resample_window_keeps_ends_and_shape():
    x = np.linspace(0, 1, 75, dtype=np.float32)[:, None] * np.ones((1, N_CHANNELS), dtype=np.float32)
    y = resample_window(x, 64)
    assert y.shape == (64, N_CHANNELS)
    assert np.allclose(y[0], x[0]) and np.allclose(y[-1], x[-1])


def test_replay_source_reads_recording_csv(tmp_path):
    p = tmp_path / "hello_001.csv"
    p.write_text("timestamp_ms,flex1,flex2,flex3,flex4,flex5,ax,ay,az,gx,gy,gz\n"
                 "0,1500,1500,1500,1500,1500,0,0,8192,0,0,0\n"
                 "20,1510,1500,1500,1500,1500,0,0,8192,0,0,0\n")
    s = list(ReplaySource(str(p)).read_samples())
    assert len(s) == 2 and s[1].t_ms == 20 and s[1].values[0] == 1510
