import os
from typing import Dict

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory

import agente_literario_ui.backend.logging_manager as logging_manager
from agente_literario_ui.backend.model_integration import GeminiLLM

chat_history = ChatMessageHistory()
conversation_memory = ConversationBufferMemory(
    chat_memory=chat_history,
    return_messages=True,
    memory_key="history"
)

class ModelManager:
    def __init__(self):
        self.llm = GeminiLLM()
        self.prompt_template = None
        self.conversation = None
        self.initialize_conversation()

    def initialize_conversation(self):
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template=self.llm.get_system_instructions() + """

Historial de Conversación:
{history}

Usuario: {input}
Agente (responde en español):"""
        )
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=conversation_memory,
            prompt=self.prompt_template,
            verbose=True
        )

    def get_response(self, user_input: str) -> str:
        try:
            response = self.conversation.predict(input=user_input)
            return response
        except Exception as e:
            logging_manager.log_error(f"Error en la generación de la respuesta: {e}")
            return "respuesta usuario: Error al generar la respuesta del modelo."

    def get_file_tree(self) -> str:
        return self.llm._get_file_tree()
