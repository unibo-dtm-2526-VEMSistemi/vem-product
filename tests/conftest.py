import sys
import os
import io
import pandas as pd
import pytest

# Add src/ to sys.path so internal bare imports (e.g. `from config import X`) resolve
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src"),
)


LOB_CSV = """LOB Code,Name
01001,CABLAGGI COMMSCOPE
01002,CABLAGGIO ALTERNATIVO
02002,APPARATI CISCO LAN
04001,TELEFONIA IP
99001,ALTRO
"""

ARTICLES_CSV = """codice_articolo,descrizione_articolo,lob_associata_cleaned,inventario,code_prefix,duration_months,brand_vendor,product_family,capacity_unit,desc_token_count,desc_char_len,lob_nome,description_norm,rag_text
ART-001,CISCO SWITCH 24P,2002,Inventario,ART,,,CISCO,SWITCH,,50,20,APPARATI CISCO LAN,cisco switch 24p,CISCO SWITCH 24P brand:CISCO family:SWITCH
ART-002,MICROSOFT OFFICE LICENSE,99001,Non in inventario,ART,12.0,MICROSOFT,OFFICE,LICENSE,60,25,ALTRO,microsoft office license,MICROSOFT OFFICE LICENSE brand:MICROSOFT family:OFFICE duration:12.0
ART-003,HP CABLE CAT6,1001,Inventario,ART,,,HP,CABLE,,30,15,CABLAGGI COMMSCOPE,hp cable cat6,HP CABLE CAT6 brand:HP family:CABLE
ART-004,CISCO IP PHONE 7920,4001,Inventario,ART,,,CISCO,PHONE,,40,18,TELEFONIA IP,cisco ip phone 7920,CISCO IP PHONE 7920 brand:CISCO family:PHONE
ART-005,CABLING ALT KIT,1002,Non in inventario,ART,,,GENERIC,CABLE,,35,16,CABLAGGIO ALTERNATIVO,cabling alt kit,CABLING ALT KIT brand:GENERIC family:CABLE
"""


@pytest.fixture
def lob_df():
    return pd.read_csv(io.StringIO(LOB_CSV))


@pytest.fixture
def articles_df_raw():
    """Raw articles DataFrame before zero-padding (as read from CSV)."""
    return pd.read_csv(io.StringIO(ARTICLES_CSV))
