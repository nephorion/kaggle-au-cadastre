import math
import struct
import zlib

import numpy as np
import pyarrow.parquet as pq

COVER_FILE = "dataset-cover-image.png"   # the Kaggle CLI uploads this as the cover, not as a data file
WIDTH, HEIGHT = 1600, 800
LON, LAT = (112.5, 154.0), (-44.0, -9.5)   # mainland Australia and Tasmania
BACKGROUND = (11, 19, 32)
# Colour ramp from sparse to dense parcels: dark teal, teal, amber, near white.
RAMP = np.array([(20, 70, 90), (40, 170, 170), (245, 190, 70), (255, 250, 230)], dtype=float)


def _png(rgb):
    """uint8 array (height, width, 3) -> PNG bytes, using only the standard library."""
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def cover_image(config, files):
    """Write the Kaggle cover image: a density map of every parcel's interior point. Returns its path."""
    k = math.cos(math.radians(sum(LAT) / 2))                       # shrink longitude to keep the map's shape
    scale = 0.95 * min(WIDTH / ((LON[1] - LON[0]) * k), HEIGHT / (LAT[1] - LAT[0]))
    w, h = round((LON[1] - LON[0]) * k * scale), round((LAT[1] - LAT[0]) * scale)
    counts = np.zeros((h, w))
    for f in files:
        if f["kind"] != "parcels":
            continue
        t = pq.read_table(config.out_dir / f["file"], columns=["point_lon", "point_lat"])
        lon, lat = (t.column(c).to_numpy(zero_copy_only=False) for c in ("point_lon", "point_lat"))
        ok = ~(np.isnan(lon) | np.isnan(lat))
        counts += np.histogram2d(LAT[1] - lat[ok], lon[ok] - LON[0], bins=(h, w),
                                 range=((0, LAT[1] - LAT[0]), (0, LON[1] - LON[0])))[0]

    rgb = np.empty((HEIGHT, WIDTH, 3), dtype=np.uint8)
    rgb[:] = BACKGROUND
    level = np.log1p(counts) / max(np.log1p(counts).max(), 1e-9)   # 0..1, log so rural parcels still show
    pos = level * (len(RAMP) - 1)
    lo = np.minimum(pos.astype(int), len(RAMP) - 2)
    frac = (pos - lo)[..., None]
    colour = RAMP[lo] * (1 - frac) + RAMP[lo + 1] * frac
    top, left = (HEIGHT - h) // 2, (WIDTH - w) // 2
    tile = rgb[top:top + h, left:left + w]
    tile[counts > 0] = colour[counts > 0].round().astype(np.uint8)

    path = config.out_dir / COVER_FILE
    path.write_bytes(_png(rgb))
    return path
