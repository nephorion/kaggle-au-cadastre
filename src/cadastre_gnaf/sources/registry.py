from cadastre_gnaf.keys import keys_act, keys_nsw, keys_nt, keys_qld, keys_sa, keys_tas, keys_vic, keys_wa
from cadastre_gnaf.sources.source import Source

SOURCES = {
    "NSW": Source(
        url="https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer/9",
        keys=keys_nsw, licence="CC BY, (c) NSW Spatial Services (DCS)"),
    "VIC": Source(
        url="https://services-ap1.arcgis.com/P744lA0wf4LlBZ84/ArcGIS/rest/services/Vicmap_Parcel/FeatureServer/0",
        keys=keys_vic, licence="CC BY 4.0, (c) State of Victoria (Vicmap Property)"),
    "QLD": Source(
        url="https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/"
            "QSCF_LandParcelPropertyFramework/FeatureServer/120",
        keys=keys_qld, licence="CC BY 4.0, (c) State of Queensland"),
    "TAS": Source(
        url="https://services.thelist.tas.gov.au/arcgis/rest/services/Public/CadastreParcels/MapServer/0",
        keys=keys_tas, licence="CC BY 3.0 AU, (c) State of Tasmania (theLIST); see LIST Web Services T&Cs"),
    "ACT": Source(
        url="https://services1.arcgis.com/E5n4f1VY84i0xSjy/ArcGIS/rest/services/ACTGOV_BLOCKS/FeatureServer/0",
        keys=keys_act, licence="(c) Australian Capital Territory (ACTmapi)"),
    "WA": Source(
        # LGATE-001 "Cadastre (No Attributes)": geometry only, public under personal-use terms.
        # With a SLIP subscription, swap in a fully attributed layer (and pass its token in Config).
        url="https://public-services.slip.wa.gov.au/public/rest/services/SLIP_Public_Services/"
            "Property_and_Planning/MapServer/2",
        keys=keys_wa, licence="Landgate SLIP public services, personal-use licence"),
    "SA": Source(url=None, keys=keys_sa, licence="Purchased from Land Services SA (not open data)"),
    "NT": Source(url=None, keys=keys_nt, licence="NT Government (NTLIS), not open data"),
}
