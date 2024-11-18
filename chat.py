import streamlit as st
import chromadb
import os
from embed import em


# def call_gemini(docs, user_question):
#     safety_settings = [
#         {
#             "category": "HARM_CATEGORY_HARASSMENT",
#             "threshold": "BLOCK_NONE"
#         },
#         {
#             "category": "HARM_CATEGORY_HATE_SPEECH",
#             "threshold": "BLOCK_NONE"
#         },
#         {
#             "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#             "threshold": "BLOCK_NONE"
#         },
#         {
#             "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#             "threshold": "BLOCK_NONE"
#         },
#     ]

#     prompt_template = """
#     Answer the question as detailed as possible from the provided context with Chinese, 
#     make sure to provide all the details, if the answer is not in
#     provided context just say, "answer is not available in the context", 
#     don't provide the wrong answer.\n\n
#     Context:\n\n{context}?\n
#     Question: \n\n{question}\n
#     Answer:
#     """

#     context = ""
#     for doc in docs:
#         context += doc.metadata["source"] + "\n\n"

#     prompt = prompt_template.format(context=context, question=user_question)

#     print(prompt)

#     text = Gemini(model="models/gemini-1.5-flash", max_tokens=16192, safety_settings=safety_settings).complete(prompt).text
#     return text

def user_input(user_question, db):
    results = db.query(query_texts=[user_question], n_results=4)
    print(results)
    # fetch metadatas source

    text= ""
    srcList = results['metadatas'][0]
    for i in range(len(srcList)):
        srcList[i] = srcList[i]["source"]
        # print(srcList[i])
        text += srcList[i] + "\n\n"


    docs = [doc[0] for doc in results['metadatas']]
    # print(docs)
    # text = docs_to_text(docs)
    # print(text)
    st.write("Reply: ", text)




def main(dir):
    db_path = os.path.join(dir,  "db")
    print(f"using db {db_path}")
    # embeddings = GoogleGenerativeAIEmbeddings(model = "models/text-embedding-004")
    # new_db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)

    st.set_page_config("Chat PDF")
    st.header("我的银行业务助手")

    user_question = st.text_input("询问银行相关的问题")


    chroma_client = chromadb.PersistentClient(path=db_path)
    db = chroma_client.get_collection(name="questions", embedding_function=em)


    

    if user_question:
        user_input(user_question, db)





if __name__ == "__main__":
    main("D:\\learns\\dcits\\test\\text")