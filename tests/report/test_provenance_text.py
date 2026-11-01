from cadastre_gnaf.report import provenance_text
from cadastre_gnaf.sources import SOURCES

FILES = [{"file": "parquet/ACT_parcels.parquet", "state": "ACT", "kind": "parcels"},
         {"file": "csv/ACT_parcels.csv", "state": "ACT", "kind": "parcels_csv"},
         {"file": "parquet/SA_parcels.parquet", "state": "SA", "kind": "parcels"},
         {"file": "summary.csv", "state": None, "kind": "summary"}]


def test_lists_published_states_gnaf_and_method():
    text = provenance_text(FILES, SOURCES)
    assert f"- ACT cadastre: {SOURCES['ACT'].url} ({SOURCES['ACT'].licence})" in text
    assert "- SA cadastre: licensed local file (" in text
    assert text.count("ACT cadastre") == 1 and "NSW" not in text
    assert "G-NAF" in text and "data.gov.au" in text
    assert "https://www.kaggle.com/datasets/museofnephorion/australian-addresses-gnaf" in text
    assert "kaggle.com/datasets/me/g" in provenance_text(FILES, SOURCES, "me/g")
    assert "https://github.com/nephorion/kaggle-au-cadastre" in text
