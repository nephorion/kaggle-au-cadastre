import pyarrow as pa
import pyarrow.parquet as pq

from cadastre_gnaf.publish import write_parquet

CSV = "source_oid,ids,name\n1,a|b,x\n2,,\n3,c,z\n"


def test_writes_typed_parquet_in_chunks(tmp_path):
    src, out = tmp_path / "p.csv", tmp_path / "p.parquet"
    src.write_text(CSV)
    rows = write_parquet(src, out, {"source_oid": "integer", "ids": "list<string>"}, chunk=2)
    t = pq.read_table(out)
    assert rows == t.num_rows == 3
    assert t.schema.field("source_oid").type == pa.int64()
    assert t.schema.field("name").type == pa.string()               # no kind given -> string
    assert t.column("ids").to_pylist() == [["a", "b"], None, ["c"]]
    assert t.column("name").to_pylist() == ["x", None, "z"]
    assert pq.ParquetFile(out).metadata.num_row_groups == 2
    assert not out.with_name(out.name + ".tmp").exists()


def test_header_only_csv_gives_empty_file_with_schema(tmp_path):
    src, out = tmp_path / "p.csv", tmp_path / "p.parquet"
    src.write_text("source_oid\n")
    assert write_parquet(src, out, {"source_oid": "integer"}) == 0
    t = pq.read_table(out)
    assert t.num_rows == 0 and t.schema.field("source_oid").type == pa.int64()


def test_builds_at_tmp_path_then_moves(tmp_path):
    src, out, tmp = tmp_path / "p.csv", tmp_path / "out" / "p.parquet", tmp_path / "work" / "p.parquet.tmp"
    src.write_text(CSV)
    out.parent.mkdir()
    tmp.parent.mkdir()
    write_parquet(src, out, {}, tmp=tmp)
    assert out.exists() and not tmp.exists()
