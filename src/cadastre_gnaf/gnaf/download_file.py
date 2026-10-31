from pathlib import Path


def download_file(session, url, dest, chunk=8 << 20):
    """Stream `url` to `dest` (via a .part file); skips if `dest` already has the full size."""
    dest = Path(dest)
    with session.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        if dest.exists() and total and dest.stat().st_size == total:
            print("already downloaded:", dest)
            return dest
        done, tmp = 0, dest.with_suffix(".part")
        with open(tmp, "wb") as fh:
            for b in r.iter_content(chunk):
                fh.write(b)
                done += len(b)
                print(f"\r  {done/1e9:.2f} / {total/1e9:.2f} GB", end="", flush=True)
        tmp.replace(dest)
    print()
    return dest
