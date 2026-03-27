import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
import requests
import time
import os
from datetime import datetime

# =====================
# TELEGRAM AYARLARI
# =====================
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8035211094:AAEqHt4ZosBJsuT1FxdCcTR9p9uJ1O073zY')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002715468798')

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}, timeout=15)
        if r.status_code == 200:
            print("📤 Telegram gönderildi", flush=True)
        else:
            print(f"⚠️ Telegram hatası: {r.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ Telegram bağlantı hatası: {e}", flush=True)

def telegram_parcali(baslik, satirlar, parca_basina=20):
    if not satirlar:
        return
    toplam = (len(satirlar) + parca_basina - 1) // parca_basina
    for i in range(0, len(satirlar), parca_basina):
        parca = satirlar[i:i + parca_basina]
        no = (i // parca_basina) + 1
        ek = f" ({no}/{toplam})" if toplam > 1 else ""
        msg = f"{baslik}{ek}\n\n" + "\n".join(parca)
        telegram_gonder(msg)
        time.sleep(0.5)

# =====================
# SUNUCU AYARLARI (SABİT)
# =====================
INTERVAL = Interval.in_4_hour
INTERVAL_ADI = "4 Saat"
N_BARS = 500
SCAN_INTERVAL_SECONDS = 1800  # 30 dakika

# =====================
# İNDİKATÖR PARAMETRELERİ
# =====================
pd_wvf = 22
bbl = 20
mult = 2.0
lb = 50
ph = 0.85
pl = 1.01

# =====================
# BIST HİSSELERİ
# =====================
BIST_ALL_SYMBOLS = [
    'A1CAP','ACSEL','ADEL','ADESE','ADGYO','AEFES','AFYON','AGESA','AGHOL','AGROT',
    'AGYO','AHGAZ','AKBNK','AKCNS','AKENR','AKFGY','AKFYE','AKGRT','AKMGY','AKSA',
    'AKSEN','AKSGY','AKSUE','AKYHO','ALARK','ALBRK','ALCAR','ALCTL','ALFAS','ALGYO',
    'ALKA','ALKIM','ALMAD','ANELE','ANGEN','ANHYT','ANSGR','ARCLK','ARDYZ','ARENA',
    'ARSAN','ARZUM','ASELS','ASGYO','ASTOR','ASUZU','ATAGY','ATAKP','ATATP','ATEKS',
    'AVGYO','AVHOL','AVOD','AVTUR','AYDEM','AYEN','AYES','AYGAZ','AZTEK','BAGFS',
    'BAKAB','BALAT','BANVT','BASCM','BAYRK','BEGYO','BERA','BEYAZ','BFREN','BIMAS',
    'BIOEN','BIZIM','BJKAS','BLCYT','BMSTL','BNTAS','BORLS','BOSSA','BRISA','BRKSN',
    'BRSAN','BRYAT','BSOKE','BTCIM','BUCIM','BURCE','BURVA','BVSAN','CANTE','CCOLA',
    'CELHA','CEMAS','CEMTS','CIMSA','CLEBI','CMENT','COSMO','CRDFA','CRFSA','CUSAN',
    'CWENE','DAGI','DARDL','DENGE','DERIM','DESA','DESPC','DEVA','DGGYO','DITAS',
    'DMRGD','DMSAS','DOAS','DOCO','DOFER','DOGUB','DOHOL','DOKTA','DYOBY','DZGYO',
    'EBEBK','ECILC','ECZYT','EDIP','EGEEN','EGEPO','EGGUB','EGSER','EKGYO','EKOS',
    'EKSUN','EMKEL','ENERY','ENJSA','ENKAI','EPLAS','ERBOS','EREGL','ERSU','ESCOM',
    'ESEN','ETILR','EUHOL','EUPWR','EUREN','EYGYO','FENER','FONET','FORMT','FORTE',
    'FRIGO','FROTO','GARAN','GEDIK','GEDZA','GENIL','GENTS','GEREL','GESAN','GIPTA',
    'GLBMD','GLCVY','GLRMK','GLYHO','GMTAS','GOLTS','GOODY','GOZDE','GRSEL','GSDDE',
    'GSDHO','GSRAY','GUBRF','GWIND','HALKB','HATEK','HATSN','HEDEF','HEKTS','HLGYO',
    'HOROZ','HRKET','HUBVC','HUNER','HURGZ','ICBCT','IDGYO','IHLAS','IHLGM','IMASM',
    'INDES','INFO','INTEK','INVEO','INVES','ISCTR','ISDMR','ISFIN','ISGSY','ISKUR',
    'ISMEN','IZENR','IZMDC','JANTS','KAPLM','KAREL','KARSN','KARTN','KATMR','KAYSE',
    'KBORU','KCHOL','KENT','KGYO','KIMMR','KLGYO','KLKIM','KLMSN','KLNMA','KLRHO',
    'KLSER','KLSYN','KMPUR','KNFRT','KONKA','KONTR','KONYA','KOPOL','KORDS','KOTON',
    'KRDMA','KRDMB','KRDMD','KRONT','KRSTL','KRTEK','KRVGD','KSTUR','KTSKR','KUTPO',
    'KUYAS','LIDER','LIDFA','LINK','LOGO','LUKSK','MAALT','MAGEN','MAKIM','MANAS',
    'MARBL','MARKA','MARTI','MAVI','MEDTR','MEGAP','MEGMT','MEPET','MERCN','MERIT',
    'MERKO','METRO','MGROS','MNDRS','MOBTL','MPARK','MRSHL','MSGYO','MTRKS','NATEN',
    'NETAS','NIBAS','NTGAZ','NTHOL','NUGYO','NUHCM','OBASE','ODAS','ORGE','ORMA',
    'OSTIM','OTKAR','OTTO','OYAKC','OYLUM','OZGYO','OZRDN','OZSUB','PAGYO','PARSN',
    'PATEK','PEKGY','PENTA','PETKM','PETUN','PGSUS','PKART','PKENT','PNSUT','POLHO',
    'PRDGS','PRKAB','PRKME','PSGYO','QNBFK','QNBTR','RAYSG','RGYAS','RODRG','RUBNS',
    'RYSAS','SAHOL','SANEL','SANFM','SANKO','SARKY','SASA','SAYAS','SEGMN','SEGYO',
    'SEKUR','SELEC','SELVA','SILVR','SISE','SKBNK','SKTAS','SMART','SNGYO','SNPAM',
    'SOKM','SONME','SUMAS','SUNTK','SUWEN','TATGD','TAVHL','TBORG','TCELL','TDGYO',
    'TEKTU','TGSAS','THYAO','TKFEN','TKNSA','TLMAN','TMSN','TOASO','TRGYO','TRHOL',
    'TRILC','TRMET','TRALT','TSKB','TTKOM','TTRAK','TUKAS','TUPRS','TURSG','ULKER',
    'ULUSE','ULUUN','UNLU','USAK','VAKBN','VAKKO','VANGD','VBTYZ','VERTU','VESBE',
    'VESTL','VKGYO','VKING','VSNMD','YATAS','YAYLA','YBTAS','YESIL','YGGYO','YIGIT',
    'YKBNK','YONGA','YUNSA','YYAPI','ZEDUR','ZOREN','ZRGYO'
]

# =====================
# HESAPLAMA
# =====================
def calculate_wvf(df):
    df['highest_close'] = df['close'].rolling(pd_wvf).max()
    df['wvf'] = ((df['highest_close'] - df['low']) / df['highest_close']) * 100
    df['sDev'] = mult * df['wvf'].rolling(bbl).std()
    df['midLine'] = df['wvf'].rolling(bbl).mean()
    df['upperBand'] = df['midLine'] + df['sDev']
    df['rangeHigh'] = df['wvf'].rolling(lb).max() * ph
    df['momentum'] = df['close'] - df['close'].shift(4)
    df['AL_SINYALI'] = np.where(
        ((df['wvf'] >= df['upperBand']) | (df['wvf'] >= df['rangeHigh'])) & (df['momentum'] > 0),
        True, False
    )
    return df

# =====================
# TARAMA
# =====================
def tarama_yap(tv, scan_number=1):
    results = []
    toplam = len(BIST_ALL_SYMBOLS)

    print(f"\n{'='*50}", flush=True)
    print(f"🔍 TARAMA #{scan_number} — {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", flush=True)
    print(f"{'='*50}", flush=True)

    for i, symbol in enumerate(BIST_ALL_SYMBOLS, 1):
        if i % 50 == 1:
            print(f"📈 [{i}/{toplam}] İşleniyor...", flush=True)

        try:
            df = tv.get_hist(symbol=symbol, exchange='BIST', interval=INTERVAL, n_bars=N_BARS)
            if df is None or len(df) < 60:
                continue

            df = df.reset_index()
            df = calculate_wvf(df)

            if bool(df['AL_SINYALI'].iloc[-1]):
                results.append({
                    "hisse": symbol,
                    "fiyat": round(float(df['close'].iloc[-1]), 2),
                    "wvf": round(float(df['wvf'].iloc[-1]), 2),
                    "momentum": round(float(df['momentum'].iloc[-1]), 2),
                })
                print(f"  🚨 SİNYAL: {symbol} — {round(float(df['close'].iloc[-1]), 2)} TL", flush=True)

        except Exception:
            continue

        time.sleep(0.3)

    print(f"✅ Tamamlandı! {len(results)} sinyal bulundu.", flush=True)
    return results


# =====================
# ANA DÖNGÜ
# =====================
if __name__ == "__main__":
    print("🚀 CM Williams VixFix Otomatik Tarayıcı Başladı", flush=True)
    print(f"📈 Interval: {INTERVAL_ADI} | Her 30 dakikada bir", flush=True)

    tv = TvDatafeed()

    telegram_gonder(
        f"🤖 <b>CM Williams VixFix Bot Aktif</b>\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"⏰ Interval: {INTERVAL_ADI}\n"
        f"🔄 Her 30 dakikada bir tarama yapılacak\n"
        f"📊 {len(BIST_ALL_SYMBOLS)} hisse takip ediliyor"
    )

    scan_count = 0
    while True:
        scan_count += 1
        simdi = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        try:
            results = tarama_yap(tv, scan_number=scan_count)

            if results:
                telegram_gonder(
                    f"🚨 <b>CM Williams VixFix — #{scan_count}</b>\n"
                    f"📅 {simdi}\n"
                    f"⏰ {INTERVAL_ADI}\n\n"
                    f"✅ AL Sinyali: {len(results)} hisse"
                )
                time.sleep(0.5)

                satirlar = [
                    f"<b>{r['hisse']}</b> — {r['fiyat']} TL  |  WVF: {r['wvf']}  Mom: {r['momentum']}"
                    for r in results
                ]
                telegram_parcali("📈 <b>AL SİNYALLERİ</b>", satirlar)

            else:
                telegram_gonder(
                    f"📊 <b>CM Williams VixFix — #{scan_count}</b>\n"
                    f"📅 {simdi}\n"
                    f"⏰ {INTERVAL_ADI}\n\n"
                    f"❌ AL sinyali bulunamadı\n"
                    f"⏳ Sonraki tarama 30 dakika sonra..."
                )

        except Exception as e:
            print(f"❌ Tarama hatası: {e}", flush=True)
            telegram_gonder(f"⚠️ Tarama hatası: {str(e)[:100]}\n🔄 30 saniye sonra yeniden deneniyor...")
            time.sleep(30)
            continue

        print(f"\n⏳ 30 dakika bekleniyor...", flush=True)
        time.sleep(SCAN_INTERVAL_SECONDS)
