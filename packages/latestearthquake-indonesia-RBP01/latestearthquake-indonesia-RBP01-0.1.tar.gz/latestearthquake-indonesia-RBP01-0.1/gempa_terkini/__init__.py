import requests
from bs4 import BeautifulSoup


def ekstraksi_data():
    """
    Tanggal: 04 Agustus 2023
    Waktu: 18:48:38 WIB
    Magnitudo: 6.0
    Kedalaman: 10 km
    Lokasi: 0.21 LS - 125.03 BT
    Pusat gempak: Pusat gempa berada di laut 117 km Tenggara Bolaang Mongondo Timur
    Dirasakan (Skala MMI): III - IV Bone Bolango, III - IV Gorontalo, III Manado, III Tomohon, III Tondano, III Minahasa Utara, III Bolaang Mongondow Selatan, III Minahasa Tenggara, III Bolaang Mongondow Timur, III Kotamobagu, III Bitung, III Kab. Gorontalo, II-III Luwuk, II-III Kab. Gorontalo Utara, II-III Banggai Kepulauan, II Ampana
    :return:
    """

    try:
        content = requests.get('https://bmkg.go.id')
    except Exception:
        return None
    if content.status_code==200:
        soup = BeautifulSoup(content.text, 'html.parser')

        result = soup.find('span', {'class': 'waktu'})
        result = result.text.split(', ')
        waktu = result[0]
        tanggal = result[1]

        result = soup.find('div', {'class':'col-md-6 col-xs-6 gempabumi-detail no-padding'})
        result = result.findChildren('li')

        i=0
        magnitudo = None
        kedalaman = None
        ls = None
        bt = None
        pusat = None
        dirasakan = None

        for res in result:
            if i == 1:
                magnitudo = res.text
            elif i==2:
                kedalaman = res.text
            elif i==3:
                koordinat = res.text.split(' - ')
                ls = koordinat[0]
                bt = koordinat[1]
            elif i==4:
                lokasi = res.text
            elif i==5:
                dirasakan = res.text
            i=i+1

        hasil = dict()
        hasil['tanggal'] = tanggal
        hasil['waktu'] = waktu
        hasil['magnitudo'] = magnitudo
        hasil['kedalaman'] = kedalaman
        hasil['koordinat'] = { 'ls':ls, 'bt':bt }
        hasil['lokasi'] = lokasi
        hasil['dirasakan'] = dirasakan
        return hasil
    else:
        return None

def tamilkan_data(result):
    if result is None:
        print ("Tidak bisa menemukan gempa terkini")
        return

    print('Gempa Terakhir Berdasarkan BMKG')
    print(f"Tanggal {result['tanggal']}")
    print (f"Waktu {result['waktu']}")
    print (f"Magnitudo {result['magnitudo']}")
    print (f"Kedalaman {result['kedalaman']}")
    print (f"Koordinat: LS={result ['koordinat']['ls']}, BT={result ['koordinat']['bt']}")
    print(f"Lokasi {result['lokasi']}")
    print (f"Dirasakan {result['dirasakan']}")

#if __name__ == '__main__':
#    print('ini adalah package gempaterkini')
# kode yang paling kiri di jalankan. jika tidak di paling pinggir tidak dijalankan
if __name__ == '__main__':
    result=ekstraksi_data()
    tamilkan_data(result)
