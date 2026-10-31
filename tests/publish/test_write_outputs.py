import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.publish import write_outputs

CHUNKS = [pd.DataFrame({"source_oid": ["1", "2"], "ids": ["a|b", ""], "name": ["x", ""]}),
          pd.DataFrame({"source_oid": ["3"], "ids": ["c"], "name": ["z"]})]


def paths(tmp_path):
    out, work = tmp_path / "out", tmp_path / "work"
    out.mkdir()
    work.mkdir()
    return out / "p.parquet", out / "p.csv", work


def test_writes_parquet_and_csv(tmp_path):
    pq_out, csv_out, work = paths(tmp_path)
    rows = write_outputs(iter(CHUNKS), {"source_oid": "integer", "ids": "list<string>"}, pq_out, csv_out, work)
    t = pq.read_table(pq_out)
    assert rows == t.num_rows == 3 and pq.ParquetFile(pq_out).metadata.num_row_groups == 2
    assert t.schema.field("source_oid").type == pa.int64() and t.schema.field("name").type == pa.string()
    assert t.column("ids").to_pylist() == [["a", "b"], None, ["c"]]
    csv = pd.read_csv(csv_out, dtype=str, keep_default_na=False)
    assert csv.to_dict("list") == {"source_oid": ["1", "2", "3"], "ids": ["a|b", "", "c"], "name": ["x", "", "z"]}
    assert not list(work.iterdir())


def test_stale_temp_files_are_replaced(tmp_path):
    pq_out, csv_out, work = paths(tmp_path)
    (work / "p.csv.tmp").write_text("junk\n")
    write_outputs(iter(CHUNKS), {}, pq_out, csv_out, work)
    assert pd.read_csv(csv_out).columns.tolist() == ["source_oid", "ids", "name"]


def test_empty_chunk_gives_files_with_header(tmp_path):
    pq_out, csv_out, work = paths(tmp_path)
    empty = pd.DataFrame({"source_oid": pd.Series([], dtype=str)})
    assert write_outputs(iter([empty]), {"source_oid": "integer"}, pq_out, csv_out, work) == 0
    assert pq.read_table(pq_out).schema.field("source_oid").type == pa.int64()
    assert csv_out.read_text().strip() == "source_oid"


def test_no_chunks(tmp_path):
    pq_out, csv_out, work = paths(tmp_path)
    assert write_outputs(iter([]), {}, pq_out, csv_out, work) == 0
    assert not pq_out.exists() and not csv_out.exists()
