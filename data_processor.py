# METABOLAI | VERİ İŞLEME VE RAG HAZIRLIĞI
#
# 1. 'nutrition_dataset.csv' dosyasını okur ve sütunları temizler/Türkçeleştirir.
# 2. Besin verilerini LLM'in okuyacağı RAG metnine (source_text) dönüştürür.
# 3. Bu metinleri vektörleştirir ve ChromaDB'ye yükler (Vektör Veritabanı).




import pandas as pd
#---lansgchain ve ChromaDB'ye veri yüklemek için---
from langchain_community.document_loaders.dataframe import DataFrameLoader 
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

import os

DOSYA_ADI="nutrition_dataset.csv"

try:
    df=pd.read_csv(DOSYA_ADI)
    print("---yüklenen gerçek veri seti---")
    print(df.head(n=10)) #n=10, ilk 10 satırı yazdırır.
    print("\nSütun ve Veri Tipleri:")
    df.info()
except FileNotFoundError:
    print(f"Hata: Dosya bulunamadı: {DOSYA_ADI}")
    exit()
except Exception as e:
    print(f"Hata: {e}")


#df.head(n=6) ilk 6 satırı yazdırır.

print("\n--- Yüklenen Veri setinin ilk 6 Satırı(Başlıklar)---")
print(df.head(n=6))


#df.info() sütun ve veri tiplerini yazdırır.

print("\n--- Sütun ve Veri Tipleri Kontrolü (df.info())---")
df.info()

df.columns = df.columns.str.replace(r'[()\s\-\/\.]', '', regex=True)

df.rename(columns={
    'FoodItems': 'yiyecek_adi',        
    'Energykcal': 'kalori_kcal',          
    'Carbs': 'karbonhidrat_g',           
    'Proteing': 'protein_g',      
    'Fatg': 'yag_g',                 
    'Freesugarg': 'ilave_seker_g',      
    'Fibreg': 'lif_g',                  
    'Cholestrolmg': 'kolestrol_mg',      
    'Calciummg': 'kalsiyum_mg'

}, inplace=True)

print("\n--- ✅ Sütun İsimleri Başarıyla Temizlendi ve Türkçeleştirildi ---")
print(df.columns.tolist()) 




df['source_text'] = df.apply(

    lambda row:(
        f"Besin Adı: {row['yiyecek_adi']}\n"
        f"Kalori: {row['kalori_kcal']}kcal\n"
        f"Makrolar (100 gr için): Protein: {row['protein_g']}g, Karbonhidrat: {row['karbonhidrat_g']}g, Yağ: {row['yag_g']}g \n"
        f"Ek Bilgiler: Kolesterol {row['kolestrol_mg']}mg, Kalsiyum {row['kalsiyum_mg']}mg, Lif {row['lif_g']}g"
    ),
    axis=1
)
print("\n --- Rag İçin Hazırlanan Veri Örneği(Tr format)---")

#ilk yiyeceğin hazırlanan metni
print(df['source_text'].iloc[0])


#--ChromaDB kurulumu ve veri yükleme--

CHROMA_DB_PATH="./chroma_db"

def setup_chromadb(df):
    
    ###   Pandas DataFrame'i alır, LangChain Dokümanlarına çevirir ve ChromaDB'ye yükler.

    #LongChain dökümanlarına çevirme
    
    loader=DataFrameLoader(df, page_content_column="source_text")
    documents=loader.load()
    
    #Türkçe uyumlu embedding modeli seçimi
    
    embedding_model= SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    #ChromaDB'ye kaydetme(yoksa oluşturup kaydeder.)
    vectorstore=Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

    print("\n---ChromaDB Kurulumu Başarılı---")
    print(f"Vektör Veritabanı {CHROMA_DB_PATH} dizininde oluşturuldu ve {len(df)} besin yüklendi." )
    return vectorstore


# Ana çalıştırma ve test bloğu(SADECE dosya çalıştırıldığında)

if __name__ == "__main__":

    #ChromaDB kurulup veri tabanı nesnesi alalım.
    db=setup_chromadb(df)

    #RAG Testi: Türkçe sorgu ile veri çağırıyoruz.
    query="Hangi yiyecekte en çok protein var?"
    results=db.similarity_search(query,k=1)

    print(f"\n--- Türkçe Sorgu Sonucu ('{query}')---")
    print("Geri Çağırılan Besin Bilgisi:",results[0].page_content)

    #"chroma_db" klasörü artık oluştu, proje bu chromaDB verisini kullanacaktır.

