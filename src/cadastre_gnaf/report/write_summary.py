import pandas as pd

from cadastre_gnaf.report.attribution_markdown import attribution_markdown
from cadastre_gnaf.report.summary_rows import summary_rows
from cadastre_gnaf.sources import SOURCES


def write_summary(config, summaries, sources=SOURCES):
    """Write summary.csv and ATTRIBUTION.md, then print the summary and the output file list."""
    rows = summary_rows(config, sources, summaries)
    summary = pd.DataFrame(rows)
    config.out_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(config.out_dir / "summary.csv", index=False)
    (config.out_dir / "ATTRIBUTION.md").write_text(attribution_markdown(rows), encoding="utf-8")

    print(summary.to_string(index=False))
    for f in sorted(config.out_dir.rglob("*")):
        if f.is_file():
            print(f"{f.stat().st_size/1e6:10.1f} MB  {f.relative_to(config.out_dir).as_posix()}")
    return summary
