import struct
import zlib

import numpy as np

from cadastre_gnaf.report import cover_image, dataset_files
from cadastre_gnaf.report.cover_image import BACKGROUND, HEIGHT, WIDTH


def read_png(data):
    """PNG bytes written by cover_image -> (height, width, 3) uint8 array."""
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    pos, idat, size = 8, b"", None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        assert struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])[0] == zlib.crc32(kind + body)
        if kind == b"IHDR":
            size = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    w, h = size
    rows = np.frombuffer(zlib.decompress(idat), dtype=np.uint8).reshape(h, 1 + w * 3)
    assert (rows[:, 0] == 0).all()                      # filter type "none" on every row
    return rows[:, 1:].reshape(h, w, 3)


def test_density_map_of_parcel_points(dataset_out):
    path = cover_image(dataset_out, dataset_files(dataset_out))
    assert path.name == "dataset-cover-image.png"
    img = read_png(path.read_bytes())
    assert img.shape == (HEIGHT, WIDTH, 3)
    lit = (img != BACKGROUND).any(axis=2)
    assert 1 <= lit.sum() <= 2                          # the two parcel points, nothing else
    ys, xs = np.nonzero(lit)
    assert (xs > WIDTH // 2).all() and (ys < HEIGHT).all()   # east of centre: Canberra is on the east coast


def test_no_parcels_gives_a_blank_cover(config):
    config.out_dir.mkdir()
    img = read_png(cover_image(config, []).read_bytes())
    assert (img == BACKGROUND).all()
