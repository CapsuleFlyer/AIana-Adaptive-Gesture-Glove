import numpy as np
from aiana.acquisition.reader import Windower, count_drops, parse_line, read_samples, resample

GOOD = "S,5,100,1,2,3,4,5,10,20,30,40,50,60"


def test_parse_good():
    s = parse_line(GOOD)
    assert s.seq == 5 and s.t_ms == 100 and s.values == [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60]


def test_parse_rejects_bad_lines():
    for bad in ["", "#AIANA,fw=1", "S,1,2,3", "S,a,b," + ",".join(["1"] * 11), GOOD + ",9", "X" + GOOD[1:]]:
        assert parse_line(bad) is None


def test_fake_and_windows():
    w, wins = Windower(100, 12), []
    for s in read_samples("fake", n=300):
        x = w.push(s)
        if x is not None:
            wins.append(x)
    assert wins[0].shape == (100, 11)
    assert len(wins) == (300 - 100) // 12 + 1


def test_resample_shape_and_ends():
    x = np.arange(200, dtype=np.float32).reshape(100, 2)
    r = resample(x, 64)
    assert r.shape == (64, 2) and r[0, 0] == x[0, 0] and r[-1, 0] == x[-1, 0]


def test_drops():
    class S:  # tiny stand-in
        def __init__(self, q): self.seq = q
    assert count_drops([S(0), S(1), S(4), S(5)]) == 2


def test_replay(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text("timestamp_ms,f1,f2,f3,f4,f5,ax,ay,az,gx,gy,gz\n0,1,2,3,4,5,6,7,8,9,10,11\n20,1,2,3,4,5,6,7,8,9,10,11\n")
    out = list(read_samples("replay", path=str(p)))
    assert len(out) == 2 and out[1].t_ms == 20 and len(out[0].values) == 11
