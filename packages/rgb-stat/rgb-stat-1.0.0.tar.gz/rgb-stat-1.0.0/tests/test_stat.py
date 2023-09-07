"""Test stat.py"""

from rgb.stat import *

data = [
    [
        1, 4, 6, 7, 9, 3, 23, 
        5, 6, 7, 8, 4, 47, 3,
        5, 34, 3, 3, 34, 3, 3,
        46, 57, 68, 9, 9, 67, 67
    ],
    [
        56, 23, 34, 5, 6, 2, 6,
        34, 2, 34, 4, 6, 7, 8,
        6, 7, 86, 4, 55, 44, 106,
        13, 34, 6, 64, 64, 2, 34
    ],
    [
        3, 3, 4, 6, 7, 9, 9,
        21, 1, 2, 3, 5, 6, 7,
        12, 56, 123, 56, 78, 76, 6,
        75, 32, 11, 224, 55, 250, 21
    ]
]

mu = 20

print(np.mean(data[0]), np.mean(data[1]), np.mean(data[2]))
print(np.median(data[0]), np.median(data[1]), np.median(data[2]))
print(np.max(data[0]), np.max(data[1]), np.max(data[2]))
print(np.min(data[0]), np.min(data[1]), np.min(data[2]))
print(np.var(data[0]), np.var(data[1]), np.var(data[2]))
print(np.std(data[0], ddof=1) / 28, np.std(data[1], ddof=1) / 28, np.std(data[2], ddof=1) / 28)


expected_stat = {
    "mean": 1,
    "median": 2,
    "maximum": 3,
    "minimum": 4,
    "var": 5,
    "std_error": 6,
    "confidence_test": 7,
    "ok": False,
}


def test_mean():
    pass


def test_median():
    pass


def test_maximum():
    pass


def test_minimum():
    pass


def test_var():
    pass


def test_standard_error():
    pass


def test_confidence_test():
    pass


def test_interpret_confidence_test():
    pass
