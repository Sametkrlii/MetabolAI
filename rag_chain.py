# RAG_CHAIN.PY | LLM ve RAG ZİNCİRİ MODÜLÜ
#
# Amaç:
# 1. Gemini API'ye bağlantıyı kurar.
# 2. ChromaDB veritabanını yükler.
# 3. Kullanıcı sorusunu alır ve RAG zincirini kullanarak Türkçe öneri/cevap üretir.

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os



#ÇEVİRİ FONKSİYONU

def translate_query(query:str)->str:
    """"
    Türkçe sorguyu Gemini kullanarak İngilizceye çevirir.
    """

    try:

        llm_translate=GoogleGenerativeAI(model="gemini-2.5-flash",temperature=0) #yaratıcılık 0

        #Modele sadece çeviri yapmasını söylüyoruz. **gemini ile güçlendirilmiş prompt.
        prompt = (
            f"Aşağıdaki Türkçe metni, sadece veritabanında arama yapmak için kullanılacak "
            f"NET İNGİLİZCE BESİN ADI veya bir İNGİLİZCE SORGUSU olarak çevir. "
            f"Ekstra cümle kurma, sadece çeviriyi döndür: '{query}'"
        )

        #LLM i çağırıp sonucu alıyoruz.
        response=llm_translate.invoke(prompt)

        return response.strip()
    
    except Exception as e:
        print(f"Çeviri hatası:{e}. Orjinal Sorgu Kullanılıyor.(yanlış sonuçlar doğurabilir.)")

        return query




# 1. Veritabanı Yüklemesi ve Retriever (Geri Çağırıcı) Hazırlığı

CHROMA_DB_PATH="./chroma_db"

def get_retriever():
    #veri tabanı kurarken kullandığımla aynı olmalı.
    embeddings_model=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    #veritabanını diskten okuyup yükleme
    vectorstore=Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings_model
    )

    # Retriever objesi, LLM'in kullanacağı arama aracıdır, search_kwargs={"k":3} ifadesi, arama yapıldığında anlamsal olarak en yakın 3 besini getirir.
    retriever=vectorstore.as_retriever(search_kwargs={"k":5})
    
    return retriever


# ----------------------------------------------------
# 2. Prompt Engineering (Modelin Kimliğini Belirleme)


#geminiye kişilik atayalım.
custom_prompt_template="""
Sen, kullanıcıya kalori ve makro takibi konusunda yardımcı olan, fitness odaklı, akıllı bir Beslenme Koçusun.
Yanıtların Türkçe, pozitif ve motivasyonel olmalıdır. Motivasyonel olduğu kadar gerçekçi de olmalı ki karşındaki kişi doğru bilgiler edinebilsin.

Görevler:
1. YALNIZCA sağladığım BESİN BİLGİLERİNİ (CONTEXT) kullan. Asla uydurma veya genel internet bilgisi verme.
2. CONTEXT içindeki TÜM YİYECEK ADLARINI Türkçeye çevirerek (Örn: Cupcake yerine 'Küçük Kek', Butternaan yerine 'Tereyağlı Bazlana' gibi) kullanıcıya sun. Yabancı kelime kullanma.
3. Cevabı kısa, net ve anlaşılır bir Türkçe formatta üret.

Kullanıcının Sorgusu: {question}
BESİN BİLGİLERİ (CONTEXT): {context}

YANITIN (Türkçe ve Beslenme Koçu tarzında):
"""


RAG_PROMPT=PromptTemplate(
    template=custom_prompt_template,
    input_variables=["context","question"]
)

def get_base_llm():
    """Gemini LLM instance'ını döndürür"""
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash-exp",temperature=0.2)



# RAG CHAIN KURULUMU

def setup_rag_chain():
    """
    Gemini LLM'i ve ChromaDB Retriever'ı birleştirerek RAG zincirini kurar.
    """
    # 1. LLM'i tanımlama
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2 
    )
    
    # 2. Retriever'ı yükleme
    retriever = get_retriever()

    # 3. RetrievalQA Zincirini kurma (RAG'in Kalbi)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff", # Çekilen tüm context'i modele gönder demektir.
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": RAG_PROMPT}
    )
    return qa_chain



# ----------------------------------------------------
# 3. Test Bloğu
# ----------------------------------------------------


if __name__ == "__main__":
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    
    print("🔧 ChromaDB Test Ediliyor...\n")
    
    # Veritabanını yükle
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
    
    # Farklı sorgular test et
    test_queries = [
        "high protein low fat",
        "chicken breast",
        "30g protein 10g fat",
        "egg white",
        "fish salmon"
    ]
    
    for query in test_queries:
        print(f"\n📝 Sorgu: '{query}'")
        results = vectorstore.similarity_search(query, k=3)
        
        for i, doc in enumerate(results, 1):
            # İlk satırı al (besin adı)
            food_name = doc.page_content.split('\n')[0].replace('Besin Adı: ', '')
            print(f"   {i}. {food_name}")