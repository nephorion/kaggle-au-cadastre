import pandas as pd


def _col(df, name):
    return df[name].fillna("").astype(str) if name in df else pd.Series("", index=df.index)


def _squeeze(s):
    return s.str.replace(r"\s+", " ", regex=True).str.strip()


def format_address(df, state):
    """G-NAF ADDRESS_DETAIL rows (joined to street and locality names) -> address parts and a one-line address.

    e.g. "UNIT 2, 134 ARANDA STREET, BELCONNEN ACT 2614".
    """
    num = {p: _col(df, f"{p}_PREFIX") + _col(df, p) + _col(df, f"{p}_SUFFIX")
           for p in ("FLAT_NUMBER", "LEVEL_NUMBER", "NUMBER_FIRST", "NUMBER_LAST", "LOT_NUMBER")}
    number = num["NUMBER_FIRST"].where(num["NUMBER_LAST"] == "", num["NUMBER_FIRST"] + "-" + num["NUMBER_LAST"])
    lot = ("LOT " + num["LOT_NUMBER"]).where(num["LOT_NUMBER"] != "", "")
    parts = pd.DataFrame({
        "address_building_name": _squeeze(_col(df, "BUILDING_NAME")),
        "address_flat": _squeeze(_col(df, "FLAT_TYPE_CODE") + " " + num["FLAT_NUMBER"]),
        "address_level": _squeeze(_col(df, "LEVEL_TYPE_CODE") + " " + num["LEVEL_NUMBER"]),
        "address_number": number.where(number != "", lot),
        "address_street": _squeeze(_col(df, "STREET_NAME") + " " + _col(df, "STREET_TYPE_CODE") + " "
                                   + _col(df, "STREET_SUFFIX_CODE")),
        "address_locality": _squeeze(_col(df, "LOCALITY_NAME")),
        "address_postcode": _col(df, "POSTCODE"),
    }, index=df.index)
    line = _squeeze(parts["address_number"] + " " + parts["address_street"])
    place = _squeeze(parts["address_locality"] + " " + state + " " + parts["address_postcode"])
    parts.insert(0, "address_full", [", ".join(filter(None, t)) for t in zip(
        parts["address_building_name"], parts["address_flat"], parts["address_level"], line, place)])
    return parts
