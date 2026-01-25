import requests
import xml.etree.ElementTree as ET
from rdflib import Graph, Literal, RDF, RDFS, Namespace
from rdflib.namespace import XSD

# 1. Konfigurasi Namespace
EX = Namespace("http://example.org/gadget#")
SCHEMA = Namespace("http://schema.org/") 

g = Graph()
g.bind("ex", EX)
g.bind("schema", SCHEMA)

# 2. Ambil Data XML
url_xml = "http://localhost/ws/gadgetsemantic/xml_specs.php" 

print(f"Sedang mengambil data dari {url_xml}...")

try:
    response = requests.get(url_xml)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        print("Mulai konversi XML ke RDF dengan Atribut Baru...")
        
        for gadget in root.findall('gadget'):
            sku = gadget.get('id')
            model_name = gadget.find('model').text
            brand_name = gadget.find('brand').text
            
            hp_uri = EX[sku] 
            
            # Type
            g.add((hp_uri, RDF.type, EX.Smartphone))
            
            # Basic Info
            g.add((hp_uri, RDFS.label, Literal(model_name)))
            g.add((hp_uri, EX.hasBrand, Literal(brand_name)))
            g.add((hp_uri, EX.hasModel, Literal(model_name)))
            
            # Teknis
            teknis = gadget.find('teknis')
            if teknis is not None:
                # 1. RAM & Processor (Basic)
                g.add((hp_uri, EX.hasProcessor, Literal(teknis.find('processor').text)))
                g.add((hp_uri, EX.hasRAM, Literal(int(teknis.find('ram').text), datatype=XSD.integer)))
                g.add((hp_uri, EX.hasStorage, Literal(int(teknis.find('storage').text), datatype=XSD.integer)))
                
                # 2. Refresh Rate (Untuk Gaming Kompetitif)
                rr = teknis.find('refresh_rate').text
                g.add((hp_uri, EX.refreshRateHz, Literal(int(rr), datatype=XSD.integer)))
                
                # 3. Baterai (Untuk Ojol/Driver)
                bat = teknis.find('battery').text
                g.add((hp_uri, EX.batteryCapacity, Literal(int(bat), datatype=XSD.integer)))
                
                # 4. Kamera (Untuk Konser)
                cam = teknis.find('camera_mp').text
                g.add((hp_uri, EX.mainCameraMP, Literal(int(cam), datatype=XSD.integer)))
                
                tele = teknis.find('telephoto').text # Ya / Tidak
                # Kita simpan sebagai String "Ya"/"Tidak" atau Boolean
                g.add((hp_uri, EX.hasTelephoto, Literal(tele)))

        # Simpan ke File
        output_file = "knowledge_base.ttl"
        g.serialize(destination=output_file, format="turtle")
        print(f"✅ Sukses! Data RDF Lengkap tersimpan di '{output_file}'")
        print(f"Total Triple: {len(g)}")
        
    else:
        print(f"❌ Gagal mengambil XML. Kode: {response.status_code}")

except Exception as e:
    print(f"❌ Terjadi Error: {e}")