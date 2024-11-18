import os
import re
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
import chromadb
from typing import List

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=gemini_api_key)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model, content=input, task_type="retrieval_document", title=title)["embedding"]

def get_paragraphs(text):
    """
    Extract paragraphs from text. Paragraphs are separated by two or more newlines.
    
    Args:
        text (str): Input text
        
    Returns:
        list: List of paragraphs
    """
    # Split text by one or more newlines
    lines = text.split('\n')
    
    paragraphs = []
    current_paragraph = []
    empty_line_count = 0
    
    for line in lines:
        if line.strip():  # Non-empty line
            current_paragraph.append("\n"+line)
            empty_line_count = 0
        else:  # Empty line
            empty_line_count += 1
            if empty_line_count >= 2 and current_paragraph:
                # Join lines in current paragraph and add to result
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
    
    # Don't forget the last paragraph
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    return paragraphs

def get_qa_chunks_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        # 通过3个或更多的空行分隔文本
        text_chunks = get_paragraphs(text)
        print(len(text_chunks))
        # text_chunks = get_text_chunks(text)
        return text_chunks

def remove_duplicated_chunks(text_chunks):
    unique_titles = []
    documents = []
    for chunk in text_chunks:
        chunk = chunk.strip()
        

        title_line = chunk.split("\n")[0].strip()
        # extract title that after first . or 、

        # print("`"+chunk+"`")
        title =  re.split('[.、]', title_line, maxsplit=1)[1].strip()
        if title == "":
            continue

        if title not in unique_titles:
            unique_titles.append(title)
            print("`"+title+"`")

            doc = {
                "page_content": title,
                "source": chunk
            }
            documents.append(doc)

    # print(unique_chunks)
    return documents

def save_qa_chunks_to_vector_store(docs, db_path):
        
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    # Create a Chroma database with the given documents
    def create_chroma_db(documents: List[dict], path: str, name: str):
        chroma_client = chromadb.PersistentClient(path=path)
        db = chroma_client.create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
        for i, d in enumerate(documents):
            meta = {"source": d["source"]}
            print(d)
            db.add(documents=[d["page_content"]],metadatas=[meta],ids=[str(i)])
        return db, name

    # Specify the path and collection name for Chroma database
    db_name = "questions"
    db_path = os.path.join(os.getcwd(), db_path)
    db, db_name = create_chroma_db(docs, db_path, db_name)


def store_all_text_file(dir):
    db_path = os.path.join(dir,  "db")
    chunks = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".txt"):
                text_file = os.path.join(root, file)
                print(f"process text file {text_file}")
                chunks = chunks + get_qa_chunks_from_file(text_file)
    docs = remove_duplicated_chunks(chunks)

    print(f"save chunks to {db_path}")

    save_qa_chunks_to_vector_store(docs, db_path)

if __name__ == "__main__":
    store_all_text_file("D:\\learns\\dcits\\test\\text")