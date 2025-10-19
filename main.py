# MAIN.PY | ANA UYGULAMA VE ARAYÜZ (STREAMLIT)
#
# Amaç:
# 1. Streamlit kütüphanesi ile web arayüzünü (UI) tasarlar.
# 2. Kullanıcıdan veri (kilo, boy, yenen yemekler) alır.
# 3. 'calculator.py' ve 'rag_chain.py' modüllerindeki fonksiyonları çağırarak tüm akışı yönetir ve çıktıları ekranda gösterir.
import streamlit as st
import os


#kendi modüllerimbaşla bakal
from calculator import calculate_bmr, calculate_macros,calculate_tdee_and_goal
from rag_chain import setup_rag_chain,translate_query



if "messages" not in st.session_state:
    st.session_state.messages=[]


# ----------------------------------------------------
# 1. RAG Zincirini Tek Seferde Yükleme Fonksiyonu
#-----------------------------------------------------

@st.cache_resource
def initialize_models():
    """
    RAG zincirini (Gemini + ChromaDB) sunucu çalıştığı sürece sadece bir kez yükler.
    """
    try:
        # Tam çalışan RAG chaini döndür.
        qa_chain = setup_rag_chain()
        return qa_chain
    except Exception as e:
        st.error(f"AI Modülü Yüklenirken Hata: {e}")
        st.code(f"Detay: {e}")
        return None

# Uygulama başlangıcında modeli yükleyelim
RAG_CHAIN = initialize_models()
    
# ----------------------------------------------------
# 2. Arayüz Düzeni ve Başlık
# ----------------------------------------------------


st.set_page_config(page_title="MetabolAI",
                layout="wide",
                page_icon="MetabolAI.png"                   
                   )

col_logo, col_title = st.columns([0.5, 3],vertical_alignment="center") # 0.5 birim logo, 3 birim başlık metni

with col_logo:
    # 120 piksel genişlikte logo
    st.image("MetabolAI.png", width=120) 

with col_title:
    # st.title, büyük boyutta başlık gösterir
    st.title("MetabolAI: Yapay Zeka Destekli Beslenme Takip Asistanınız")

st.markdown("""
    Merhaba! Ben, fitness hedeflerinize ulaşmanız için özel olarak tasarlanmış yapay zeka asistanınız.
    Lütfen fiziksel bilgilerinizi girerek başlayalım.
""")

# ----------------------------------------------------
# 3. Ana Akış: Kullanıcıdan Veri Alma (Streamlit Formu)
# ----------------------------------------------------

if RAG_CHAIN:

    #kullanıcıdan fiziksel verilerini almak için başlık
    st.header("Fiziksel Veri ve Hedef Girişi")


    amaclar_listesi = ['Cut', 'Maintain', 'Bulk', 'Recomp', 'Keto']
    amac_aciklamasi = "Cut: Yağ yakımı. Maintain: Kilo koruma. Bulk: Kas kütlesi kazanımı. Recomp: Kilo koruyarak kas yapımı. Keto: Düşük Karbonhidrat/Yüksek Yağ."


    with st.form("hesaplama_formu"):
        
        #formu 3 sütuna ayırıyoruz.
        col1,col2,col3=st.columns(3)

        #Column1: Kilo, Boy ve Yaş

        with col1:
            kilo=st.number_input("Kilo(kg)",min_value=30.0, max_value=250.0,value=80.0,step=0.1)
            boy=st.number_input("Boy(cm)",min_value=130.0,max_value=230.0,value=180.0,step=1.0)
            yas=st.number_input("Yaş",min_value=15,max_value=80,value=20,step=1)

        # COLUMN 2: Aktivite, Hedef ve Kalori Farkı

        with col2:
            aktivite=st.selectbox("Aktivite Seviyesi", ['Hafif Aktif', 'Sedanter','Orta', 'Yuksek', 'Cok yuksek'],index=2)
            amac=st.selectbox(
                "Beslenme Amacı",
                options=amaclar_listesi,
                index=1,
                help=amac_aciklamasi
            )

            #varsayılan 0 kcal fark seçiyoruz, onun dışında duruma göre ekrana yazdırıyor.
            if amac.lower()=="bulk":
                hedef_kcal_farki=500

            elif amac.lower()=="maintain":
                hedef_kcal_farki=0

            elif amac.lower()=="cut":
                hedef_kcal_farki=-500

            elif amac.lower()=="keto":
                hedef_kcal_farki=-250

            elif amac.lower()=="recomp":
                hedef_kcal_farki=-200

            else:
                hedef_kcal_farki=0


            



        # COLUMN 3: Cinsiyet 
        with col3:
            cinsiyet=st.radio("Cinsiyet",('Erkek','Kadın')).lower()

  


        #sumbitted: Formdaki butona basıldığını kontrol eder.
        
        submitted=st.form_submit_button("Kalori & Makro Hesapla ve Hedefi Belirle")

        if submitted:

            # ----------------------------------------------------
            # 4. Hesaplama ve Sonuç Gösterimi (calculator.py'nin Bağlantısı)
            # ----------------------------------------------------  
            #       
            try:


                #column 2de hedef kcal farkını gösteriyoruz.
                #     
                with col2:
                    st.info(f"Hedef kcal farkınız: {hedef_kcal_farki} kcal",icon=":material/arrow_forward_ios:")

                #1. bmr hesaplama

                bmr=calculate_bmr(kilo,boy,yas,cinsiyet)

                #2.TDEE ve Kalori Hedefi

                tdee,kalori_hedefi=calculate_tdee_and_goal(bmr,aktivite,hedef_kcal_farki)

                #3.Makro Dağılımı
                protein,carb,yag=calculate_macros(kalori_hedefi,amac)

                #Not: st.session_state,değerleri tarayıcıda bu sayfa yenilense de korur.

                st.session_state.bmr=bmr
                st.session_state.tdee = tdee
                st.session_state.kalori_hedefi = kalori_hedefi
                st.session_state.protein = protein
                st.session_state.carb = carb
                st.session_state.yag = yag
                st.session_state.amac = amac

                #Başarı mesajı ve temel sonuçların gösterimi

                st.success(f"✅ Hesaplama Başarılı! Günlük Kalori Hedefiniz: **{kalori_hedefi} kcal**")
                st.markdown(f"""
                **TDEE (Tahmini Harcama):** {tdee} kcal  
                **Hedef Makrolar ({amac.upper()} için):** - Protein: **{protein}g** - Karbonhidrat: **{carb}g** - Yağ: **{yag}g**
                """)

            except ValueError as e:
                
                st.error(f"HESAPLAMA HATASI:{e}")




# ----------------------------------------------------
# 4. Chatbot Sorgu Bölümü
# ----------------------------------------------------           
st.header("Yapay Zekaya Soru Sor")
st.info("""
👤 **Kişisel Bilgiler**: Doğru sonuçlar için gerçek değerlerinizi girin.   
⏱️ **Süre**: Hesaplama sadece 2 saniye!
""")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



if st.session_state.get('kalori_hedefi'):
        
        # Soru girişi ve buton yan yana olsun
        col_q, col_b = st.columns([4, 1])
        
        with col_q:
            user_question = st.text_input("Besinler hakkında bilgi al",
                placeholder="Örn: Cut dönemine uygun düşük kalorili atıştırmalık nedir?"
            )
        
        with col_b:
            # st.text_input'un altına buton eklemek için biraz boşluk bırakalım.
            st.markdown("<br>", unsafe_allow_html=True) 
            ask_button = st.button("Sor! 🧠")
            
        # KULLANICI SORU YAZDIYSA VE BUTONA BASTIYSA ÇALIŞTIR
        if ask_button:
            
            st.session_state.messages.append({"role": "user", "content": user_question})
            

            if not user_question or len(user_question.strip())<5:
                st.warning("Lütfen daha uzun ve anlamlı bir sorgu giriniz.")

            else:
                with st.spinner("🤖 MetabolAI Beslenme Koçu yanıt hazırlıyor..."):
                    try:
                        # 1. Türkçe sorguyu İngilizceye çevirir
                        english_query=translate_query(user_question)

                        # 2. Kullanıcı profiline göre sorguyu zenginleştir
                        augmented_question=f"""
                        Kullanıcı Profili:
                        -Amaç : {st.session_state.amac}
                        - Günlük Kalori Hedefi: {st.session_state.kalori_hedefi} kcal
                        - Protein Hedefi: {st.session_state.protein}g
                        - Karbonhidrat: {st.session_state.carb}g
                        - Yağ: {st.session_state.yag}g
                    
                        Kullanıcı Sorusu (Türkçe): {user_question}
                        Arama Sorgusu (İngilizce): {english_query}
                    
                        Lütfen bu profil bilgilerini dikkate alarak Türkçe yanıt ver.
                        """


                        # 3. RAG chain'i çağır
                        response= RAG_CHAIN.invoke({"query":augmented_question})

                        # 4. Yanıtı göster
                        st.success("✅ Chatbot Yanıtı:")
                        st.markdown(response['result'])
                        
                        st.session_state.messages.append({"role": "assistant", "content": response['result']})

                    except Exception as e:
                        st.error("❌ AI yanıt oluşturulamadı. Lütfen API anahtarınızı kontrol edin.")
                        st.code(f"Hata Detayı:{str(e)}")
                    
else:
    st.warning("⚠️ Lütfen önce fiziksel verilerinizi girerek kalori hedefinizi hesaplayın.")
                        



            
        