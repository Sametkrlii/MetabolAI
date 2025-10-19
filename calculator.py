# METABOLAI | HESAPLAMA MOTORU MODÜLÜ
#
# Amaç:
# 1. Kullanıcıdan alınan fiziksel verilere (kilo, boy, yaş) göre BMR/TDEE hesaplar.
# 2. Günlük kalori hedefine göre makro besin (Protein, Karbonhidrat, Yağ) dağılımını (gram cinsinden) hesaplar.
#
# Bu dosya, projenin tüm matematiksel ve iş mantığını içerir.

import math



#BMR hesaplama fonksiyonu (Mifflin-St Jeor Formülü)

def calculate_bmr(kilo:float,boy:float,yas:int,cinsiyet:str)->float:

    #kullanıcının mantıksız veri girmesini engelle
    if (30<=kilo<=250) and (130<=boy<=230) and (13<=yas<=80):
    
        if cinsiyet.lower()=="erkek":
            bmr=(10*kilo)+(6.25*boy)-(5*yas)+5
        elif cinsiyet.lower()=="kadın": 
            bmr=(10*kilo)+(6.25*boy)-(5*yas)-161
        else:
            raise ValueError("Geçersiz cinsiyet girdiniz.")
    else:
        raise ValueError("Hatalı parametre girdiniz.")
    return round(bmr, 0)
    


        

#TDEE ve kalori hedefi Hesaplayıcı
def calculate_tdee_and_goal(bmr:float,aktivite_seviyesi:str,hedef_kcal_farki:int)-> tuple[float,float]:
    aktivite_seviyeleri={"sedanter","hafif aktif","orta","yuksek","cok yuksek"}
    if aktivite_seviyesi.lower() in aktivite_seviyeleri:
        aktivite_carpanlari={
        "sedanter": 1.2,
        "hafif aktif": 1.375,
        "orta": 1.55,
        "yuksek": 1.725,
        "cok yuksek": 1.9

        }

        carpan=aktivite_carpanlari.get(aktivite_seviyesi.lower(),1.2)

        tdee= bmr*carpan 

        gunluk_kalori_hedefi = tdee + hedef_kcal_farki

        return round(tdee,0), round(gunluk_kalori_hedefi,0)
    else:
        raise ValueError(f"aktivite seviyesini ({aktivite_seviyesi}) yanlış girdiniz.")


#makro dağılım hesaplama fonksiyonu

def calculate_macros(kalori_hedefi:float, amac: str)->tuple[float,float,float]:

    #kullanıcının mantıksız veri girmesini engelle
    if (900<=kalori_hedefi<=10000):
        macro_ratios = {
        "maintain": {"protein": 0.30, "yag": 0.25, "karbonhidrat": 0.45},
        "bulk": {"protein": 0.25, "yag": 0.20, "karbonhidrat": 0.55},
        "cut": {"protein": 0.40, "yag": 0.30, "karbonhidrat": 0.30},
        "recomp": {"protein": 0.40, "yag": 0.25, "karbonhidrat": 0.35},
        "keto": {"protein": 0.25, "yag": 0.70, "karbonhidrat": 0.05}
    }

        if amac.lower() not in macro_ratios:
            raise ValueError("geçersiz amaç. Şunlardan biri olmalı : maintain,bulk,cut,recomp,keto")

        ratios=macro_ratios[amac.lower()]

        protein_g = (kalori_hedefi*ratios["protein"])/4
        karbonhidrat_g=(kalori_hedefi*ratios["karbonhidrat"])/4
        yag_g=(kalori_hedefi*ratios["yag"])/9


        return round(protein_g),round(karbonhidrat_g),round(yag_g)
    else:
        raise ValueError("kalori hedefiniz 900 ile 10000 sınırı arasında olmalıdır.")




#--sonradan özellik olarak eklenebilecek vücut yağ oranı hesaplayıcı(navy method)--(PROJE KAPSAMI DIŞINDADIR GELİŞTİRME İÇİN HAZIRLANMIŞTIR SADECE.)

def  body_fat_ratio(cinsiyet:str,bel:float,boyun:float,boy:int,kalca: float=None)->float:

    #kullanıcının mantıksız veri girmesini engelle
    if not (50<=bel<=180) and (25<=boyun<=60)and (130<=boy<=230):
        raise ValueError("Hata: Bel (50-180), Boyun (25-60) veya Boy (130-230) sınırları dışında.")
    else:
        if cinsiyet.lower()=="erkek":
            vucut_yag_orani=495/(1.0324-0.19077*math.log10(bel-boyun)+0.15456*math.log10(boy))-450
            

        elif cinsiyet.lower()=="kadın":
            if kalca is not None:
                if 70<=kalca<=180:
                    vucut_yag_orani=495/(1.29579-0.350004*math.log10(bel+kalca-boyun)+0.22100*math.log10(boy))-450
                else:
                    raise ValueError("kalca ölçüsü 70 ile 180 arasında olmalıdır.")
            else:
                raise ValueError("Kadınlar için kalça ölçüsü girilmelidir")
                

        else:
            raise ValueError("cinsiyet seçimi erkek ya da kadın olmalı.")

        return round(vucut_yag_orani,2)     

        



