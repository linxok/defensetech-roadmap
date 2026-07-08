from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(documents, embeddings)
retriever = db.as_retriever()
results = retriever.get_relevant_documents(' failsafe')
