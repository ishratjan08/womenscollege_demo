import os
import logging
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage
from langchain.memory import ConversationBufferWindowMemory
from services.prompt import base_prompt
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
#from sentence_transformers import CrossEncoder

from services.import_service import vectorstore_object, embedder_object
from models.messages import message_service_object

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatEngine:
    context_dict = {}
    def __init__(self):
        self.parser = StrOutputParser()
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL"),
            callbacks= [StreamingStdOutCallbackHandler()],
            disable_streaming=False,    
            )
        self.chain = self._build_chain()

        self.vectorstore_object = vectorstore_object
        self.embedder_object = embedder_object
        self.message_service = message_service_object

        self.folder_path = os.getenv("DATA_FOLDER_PATH")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.chroma_persist_dir = os.getenv("CHROMA_DB_PATH")
 #       self.cross_encoder =  CrossEncoder(os.getenv("CROSS_ENCODER"))

        logger.info("ChatEngine initialized.")

    def _format_history(self, messages: list):
        history = []
        for message in messages:
            if message.role == "user":
                history.append(HumanMessage(content=message.message))
            else:
                history.append(AIMessage(content=message.message))

        memory = ConversationBufferWindowMemory(
            k=6,
            return_messages=True,
            memory_key="chat_history",
            input_key="question"
        )
        memory.chat_memory.messages = history

        logger.info("Formatted chat history with %d messages.", len(history))


        # nBufferWindowMemory(k=3))
        return memory

    def _format_inputs(self, inputs: dict):
        memory = self._format_history(inputs.get("chat_history", []))
        memory_vars = memory.load_memory_variables({})
        inputs.update(memory_vars)

        logger.info("Formatted inputs with memory keys: %s", list(memory_vars.keys()))
        print
        return {**inputs, **memory_vars}

    def _build_chain(self):
        logger.info("LLM chain built with prompt and parser.")
        return RunnableLambda(self._format_inputs) | base_prompt | self.llm | self.parser
    
    
    # def re_ranker(self, result_vectors: list, query: str) -> list:
    #     # Create query-document pairs
    #     query_doc_pairs = [(query, doc.page_content) for doc in result_vectors]

    #     # Get relevance scores
    #     scores = self.cross_encoder.predict(query_doc_pairs)
    #     print(scores)

    #     # Pair scores with original documents
    #     scored_docs = list(zip(scores, result_vectors))

    #     # Sort in descending order of score
    #     sorted_scored_docs = sorted(scored_docs, key=lambda x: x[0], reverse=True)

    #     # Separate positives and negatives
    #     positive_docs = [doc for score, doc in sorted_scored_docs if score > 0]
    #     negative_docs = [doc for score, doc in sorted_scored_docs if score <= 0]

    #     # Include one negative if available
    #     if negative_docs:
    #         positive_docs.append(negative_docs[0])

    #     return positive_docs  # List of Document objects



    def retrieve_context(self, query: str, k: int = 14) -> str:
        result_vectors = self.vectorstore_object.similarity_search(query=query, k=k)
        context = result_vectors
        print(len(context),type(context))
        context = "\n".join([doc.page_content for doc in context])
        #context = "\n".join([doc.page_content for doc in result_vectors])

        logger.info("Retrieved context for query: '%s' with %d documents.", query, len(result_vectors))
        return context

    def get_chat_history(self, session_id: str, user_id: str, limit: int = 6):
        history = self.message_service.get_messages(session_id, user_id, limit=limit)
        logger.info("Retrieved %d chat messages for session_id='%s', user_id='%s'.", len(history), session_id, user_id)
        return history

    def save_user_message(self, query: str, session_id: str, user_id: str):
        self.message_service.save_message(sess_id=session_id, user_id=user_id, role="user", message=query)
        logger.info("Saved user message: '%s'", query)

    def save_bot_message(self, response: str, session_id: str, user_id: str):
        self.message_service.save_message(sess_id=session_id, user_id=user_id, role="bot", message=response)
        logger.info("Saved bot response: '%s'", response)

    def update_dict(self, context: str, session_id: str, user_id: str) -> str:
        # Create nested structure if user_id not present
        if user_id not in self.context_dict:
            self.context_dict[user_id] = {session_id: []}
        
        # Create session_id entry if not present
        if session_id not in self.context_dict[user_id]:
            self.context_dict[user_id][session_id] = []

        # Append the new context
        self.context_dict[user_id][session_id].append(context)

        # Keep only the latest 4 messages (sliding window)
        self.context_dict[user_id][session_id] = self.context_dict[user_id][session_id][-4:]

        # Log the current context length
        logger.info("Context List Length is: '%s'", len(self.context_dict[user_id][session_id]))


        # Return the joined context in reverse (latest message first)
        # return "\n".join(self.context_dict[user_id][session_id][::-1])
        return "\n".join(self.context_dict[user_id][session_id][::-1])

    def run_chat(self, query: str, session_id: str, user_id: str) -> str:

        self.save_user_message(query, session_id, user_id)

        context = self.retrieve_context(query)
        chat_history = self.get_chat_history(session_id, user_id)

        prev_context = self.update_dict(context,session_id,user_id)

        response = self.chain.invoke({
            "question": query,
            "context": context,
            "chat_history": chat_history,
            "prev_context": prev_context
        })

        self.save_bot_message(response, session_id, user_id)


        logger.info("Generated response for query: '%s'", query)
        
        print(response)

        return response


# Global instance
chat_engine = ChatEngine()
