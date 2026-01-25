import requests
from rdflib import Graph, Namespace, Literal

# --- KONFIGURASI ---
EX = Namespace("http://example.org/gadget#")
FILE_RDF = "knowledge_base.ttl"
URL_API_HARGA = "http://localhost/ws/gadgetsemantic/api_market.php" 

# Load Graph
try:
    g = Graph()
    g.parse(FILE_RDF, format="turtle")
except Exception as e:
    print(f"Error loading RDF: {e}")

def get_harga_terkini():
    try:
        response = requests.get(URL_API_HARGA)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def cari_rekomendasi(scenario=None, brand_dicari=None, min_ram=0, max_price=0):
    
    # --- 1. MEMBANGUN PENJELASAN LOGIKA (INI RAHASIANYA) ---
    # Kita susun kalimat penjelasan "AI" di sini
    penjelasan_list = []
    
    if brand_dicari:
        penjelasan_list.append(f"• 🏷️ <b>Brand:</b> Fokus mencari merek {brand_dicari}.")
    else:
        penjelasan_list.append(f"• 🏷️ <b>Brand:</b> Mencari dari semua merek global.")

    if scenario == "konser":
        penjelasan_list.append("• 📸 <b>Skenario Konser:</b> Saya mencari HP dengan fitur <i>Telephoto (Zoom Optik)</i> atau kamera resolusi super tinggi (>100MP).")
    elif scenario == "kompetitif":
        penjelasan_list.append("• 🏆 <b>Skenario Kompetitif:</b> Saya memfilter layar dengan <i>Refresh Rate 120Hz</i> ke atas agar responsif.")
    elif scenario == "ojol":
        penjelasan_list.append("• 🔋 <b>Skenario Driver:</b> Saya mencari HP dengan baterai badak (>= 5000mAh) untuk seharian.")
    elif scenario == "roblox":
        penjelasan_list.append("• 🎮 <b>Skenario Casual:</b> Mencari spek menengah (RAM 6GB+) yang cukup untuk game ringan.")
    
    # Penjelasan RAM & Harga
    if min_ram > 0 and not scenario: # Kalau skenario kosong, jelaskan RAM
        penjelasan_list.append(f"• ⚙️ <b>Performa:</b> Mencari RAM minimal {min_ram}GB.")
    
    if max_price > 0:
        penjelasan_list.append(f"• 💰 <b>Budget:</b> Dibatasi maksimal Rp {max_price:,}.")
    
    # Gabungkan jadi satu paragraf pembuka
    header_analisa = "🧠 <b>Analisa Semantik Gadget:</b>\n" + "\n".join(penjelasan_list) + "\n\n" + "─" * 20 + "\n"

    # --- 2. PROSES SPARQL (QUERY RDF) ---
    query_str = """
    PREFIX ex: <http://example.org/gadget#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?sku ?nama ?ram ?prosesor ?telephoto ?refreshRate ?battery ?cameraMP
    WHERE {
        ?hp a ex:Smartphone ;
            ex:hasModel ?nama ;
            ex:hasRAM ?ram ;
            ex:hasProcessor ?prosesor .
        
        OPTIONAL { ?hp ex:hasTelephoto ?telephoto . }
        OPTIONAL { ?hp ex:refreshRateHz ?refreshRate . }
        OPTIONAL { ?hp ex:batteryCapacity ?battery . }
        OPTIONAL { ?hp ex:mainCameraMP ?cameraMP . }
        
        BIND(STRAFTER(STR(?hp), "#") AS ?sku)
    """
    
    # Filter Logic
    if brand_dicari:
        query_str += f'    ?hp ex:hasBrand "{brand_dicari}" .\n'
    if min_ram > 0:
        query_str += f'    FILTER (?ram >= {min_ram})\n'

    if scenario == "konser":
        query_str += f'    FILTER (?telephoto = "Ya" || ?cameraMP >= 100)\n'
    elif scenario == "kompetitif":
        query_str += f'    FILTER (?refreshRate >= 120)\n'
    elif scenario == "roblox":
        query_str += f'    FILTER (?ram >= 6)\n'
    elif scenario == "ojol":
        query_str += f'    FILTER (?battery >= 5000)\n'

    query_str += "}"

    hasil_sparql = g.query(query_str)
    
    # --- 3. PROSES HASIL RDF ---
    # Kita simpan nama HP yang ditemukan di RDF (walaupun stok kosong)
    # Ini agar bot bisa bilang: "Saya nemu HP-nya di database, tapi gak ada di toko."
    list_hp_rdf = [] 
    
    kandidat_hp = {}
    for row in hasil_sparql:
        clean_sku = str(row.sku).replace("sku_", "")
        nama_hp = str(row.nama)
        list_hp_rdf.append(nama_hp) # Simpan nama buat laporan
        
        kandidat_hp[clean_sku] = {
            "nama": nama_hp,
            "ram": str(row.ram),
            "prosesor": str(row.prosesor),
            "refreshRate": str(row.refreshRate) if row.refreshRate else "-",
            "battery": str(row.battery) if row.battery else "-",
            "telephoto": str(row.telephoto) if row.telephoto else "-"
        }
    
    # Jika di RDF saja sudah tidak ada
    if not kandidat_hp:
        return header_analisa + "❌ <b>Hasil:</b> Maaf, tidak ditemukan data HP di Knowledge Base yang memenuhi syarat teknis di atas."

    # --- 4. CEK API & STOK ---
    data_pasar = get_harga_terkini()
    hasil_pesan = [] 
    ada_barang = False

    for penawaran in data_pasar:
        sku_toko = penawaran.get('sku_ref') or penawaran.get('sku') 
        
        if sku_toko in kandidat_hp:
            harga_barang = int(penawaran['price_idr'])
            
            if max_price > 0 and harga_barang > max_price: continue

            ada_barang = True
            info = kandidat_hp[sku_toko]
            harga_fmt = f"Rp {harga_barang:,}"
            
            # Tagging Fitur
            tag = ""
            detail_fitur = ""
            if scenario == "konser": 
                tag = "📸 "
                detail_fitur = f"| Telephoto: {info['telephoto']}"
            elif scenario == "kompetitif": 
                tag = "🏆 "
                detail_fitur = f"| {info['refreshRate']}Hz"
            elif scenario == "ojol": 
                tag = "🔋 "
                detail_fitur = f"| {info['battery']}mAh"
            
            teks = (f"{tag}<b>{info['nama']}</b> ({penawaran['item_condition']})\n"
                    f"   └ Spek: RAM {info['ram']}GB {detail_fitur}\n"
                    f"   └ Harga: {harga_fmt} @ {penawaran['store_name']}\n")
            hasil_pesan.append(teks)

    # --- 5. FINAL RESPONSE (Informatif) ---
    if not ada_barang:
        # Ini bagian cerdasnya: Dia memberi tahu HP apa yang sebenarnya cocok, tapi kosong.
        hp_terdeteksi = ", ".join(list_hp_rdf[:3]) # Ambil 3 sampel nama HP
        if len(list_hp_rdf) > 3: hp_terdeteksi += ", dll"
        
        pesan_error = (f"❌ <b>Stok Habis / Over Budget</b>\n\n"
                       f"Secara teknis, saya menemukan HP yang cocok di database spek: \n"
                       f"<i>({hp_terdeteksi})</i>\n\n"
                       f"Namun, saat ini tidak ada toko mitra yang menjualnya atau harganya di atas budget Anda.")
        
        return header_analisa + pesan_error
    
    return header_analisa + "✅ <b>Rekomendasi Ditemukan:</b>\n\n" + "\n".join(hasil_pesan)