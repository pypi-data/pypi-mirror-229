#!/usr/bin/env python3

# Copyright      2022  Xiaomi Corporation (authors: Fangjun Kuang)

import os

import kaldi_native_io

base = "int8_vector"
wspecifier = f"ark,scp,t:{base}.ark,{base}.scp"
rspecifier = f"scp:{base}.scp"


def test_int8_vector_writer():
    with kaldi_native_io.Int8VectorWriter(wspecifier) as ko:
        ko.write("a", [10, 20])
        ko["b"] = [100, 120, -2]


def test_sequential_int8_vector_reader():
    with kaldi_native_io.SequentialInt8VectorReader(rspecifier) as ki:
        for key, value in ki:
            if key == "a":
                assert value == [10, 20]
            elif key == "b":
                assert value == [100, 120, -2]
            else:
                raise ValueError(f"Unknown key {key} with value {value}")


def test_random_access_int8_vector_reader():
    with kaldi_native_io.RandomAccessInt8VectorReader(rspecifier) as ki:
        assert "b" in ki
        assert "a" in ki
        assert ki["a"] == [10, 20]
        assert ki["b"] == [100, 120, -2]


def test_read_single_item():
    a = [10, 20]
    b = [100, 120, -2]

    # You can also generate a text format by adding ",t" if you like
    #  with kaldi_native_io.Int8VectorWriter("ark,scp,t:v.ark,v.scp") as ko:
    with kaldi_native_io.Int8VectorWriter("ark,scp:v.ark,v.scp") as ko:
        ko.write("a", a)
        ko["b"] = b
    """
    v.scp contains:
      a v.ark:2
      b v.ark:15
    """

    va = kaldi_native_io.read_int8_vector("v.ark:2")
    assert va == a

    vb = kaldi_native_io.read_int8_vector("v.ark:15")
    assert vb == b


def main():
    test_int8_vector_writer()
    test_sequential_int8_vector_reader()
    test_random_access_int8_vector_reader()
    test_read_single_item()

    os.remove(f"{base}.scp")
    os.remove(f"{base}.ark")


if __name__ == "__main__":
    main()
