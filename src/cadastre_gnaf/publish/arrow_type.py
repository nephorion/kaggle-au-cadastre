import pyarrow as pa

TYPES = {"integer": pa.int64(), "number": pa.float64(), "boolean": pa.bool_(), "date": pa.date32(),
         "string": pa.string(), "list<string>": pa.list_(pa.string())}


def arrow_type(kind):
    """Data dictionary type -> Arrow type (unknown types are strings)."""
    return TYPES.get(kind, pa.string())
