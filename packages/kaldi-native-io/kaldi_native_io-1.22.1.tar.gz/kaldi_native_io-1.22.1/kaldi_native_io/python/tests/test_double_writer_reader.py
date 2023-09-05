#!/usr/bin/env python3

# Copyright      2022  Xiaomi Corporation (authors: Fangjun Kuang)

import os

import kaldi_native_io

base = "double"
wspecifier = f"ark,scp,t:{base}.ark,{base}.scp"
rspecifier = f"scp:{base}.scp"


def test_double_writer():
    with kaldi_native_io.DoubleWriter(wspecifier) as ko:
        ko.write("a", 10.5)
        ko["b"] = 20.25


def test_sequential_double_reader():
    with kaldi_native_io.SequentialDoubleReader(rspecifier) as ki:
        for key, value in ki:
            if key == "a":
                assert value == 10.5
            elif key == "b":
                assert value == 20.25
            else:
                raise ValueError(f"Unknown key {key} with value {value}")


def test_random_access_double_reader():
    with kaldi_native_io.RandomAccessDoubleReader(rspecifier) as ki:
        assert "b" in ki
        assert "a" in ki
        assert ki["a"] == 10.5
        assert ki["b"] == 20.25


def main():
    test_double_writer()
    test_sequential_double_reader()
    test_random_access_double_reader()

    os.remove(f"{base}.scp")
    os.remove(f"{base}.ark")


if __name__ == "__main__":
    main()
