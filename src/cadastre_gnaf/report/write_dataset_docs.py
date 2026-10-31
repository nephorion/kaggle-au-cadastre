import json

import pandas as pd

from cadastre_gnaf.report.dataset_files import dataset_files
from cadastre_gnaf.report.dictionary_markdown import dictionary_markdown
from cadastre_gnaf.report.dictionary_rows import dictionary_rows
from cadastre_gnaf.report.kaggle_metadata import kaggle_metadata
from cadastre_gnaf.report.kaggle_readme_markdown import kaggle_readme_markdown
from cadastre_gnaf.sources import SOURCES


def write_dataset_docs(config, session=None, sources=SOURCES):
    """Write data_dictionary.md/.csv, README.md and dataset-metadata.json describing the output folder."""
    out = config.out_dir
    files = dataset_files(config)
    rows = dictionary_rows(config, files, sources, session)
    pd.DataFrame(rows, columns=["file", "column", "type", "description", "example"]).to_csv(
        out / "data_dictionary.csv", index=False)
    (out / "data_dictionary.md").write_text(dictionary_markdown(rows, files), encoding="utf-8")

    summary_csv, attribution_md = out / "summary.csv", out / "ATTRIBUTION.md"
    summary = []
    if summary_csv.exists():
        s = pd.read_csv(summary_csv)
        summary = s.astype(object).where(s.notna(), None).to_dict("records")
    attribution = attribution_md.read_text(encoding="utf-8") if attribution_md.exists() else ""
    readme = kaggle_readme_markdown(files, summary, config.kaggle_id, attribution,
                                    gnaf_kaggle_id=config.gnaf_kaggle_id)
    (out / "README.md").write_text(readme, encoding="utf-8")
    (out / "dataset-metadata.json").write_text(
        json.dumps(kaggle_metadata(config.kaggle_id, files, rows, readme), indent=2), encoding="utf-8")
    print(f"dataset docs -> {out}: README.md, data_dictionary.md, data_dictionary.csv, dataset-metadata.json")
    return rows
