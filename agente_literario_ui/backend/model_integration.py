import json  # Import the json library
import os
import re  # Import the re library for regex
from typing import ClassVar, Dict, List, Optional, Tuple  # Add Tuple

import requests
from dotenv import load_dotenv
from langchain.llms.base import \
    LLM  # Keep LLM base class if needed for type hinting elsewhere

import logging_manager  # Importar para usar log_debug

# Remove ConversationChain and ConversationBufferMemory imports as they won't be used here


load_dotenv()  # Carga las variables de entorno
API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiLLM(LLM):
    model_name: str = "gemini-2.0-flash-001"
    api_key: str = API_KEY
    # Suponemos un endpoint para la API de Gemini; ajústalo según la documentación real.
    endpoint: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent"

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "gemini_custom"

    @property
    def _identifying_params(self) -> Dict:
        return {"model_name": self.model_name}

    # Remove memory and conversation chain initialization from LLM class
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     # Conversation chain should be managed outside this class

    # Define system instructions as a constant or method if needed, but not tied to Langchain here
    def get_system_instructions(self) -> str:
        # Read instructions from the external file
        prompt_file_path = os.path.join(os.path.dirname(__file__), '..', 'system_prompt.txt') # Assumes file is in parent dir
        # Adjust path if system_prompt.txt is in the same directory as model_integration.py:
        # prompt_file_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
        try:
            # Use absolute path based on current file's location
            # Go up one level from model_integration.py to the project root
            project_root = os.path.dirname(os.path.abspath(__file__))
            prompt_file_path = os.path.join(project_root, 'system_prompt.txt')

            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logging_manager.log_error(f"Error: No se encontró el archivo de prompt del sistema en {prompt_file_path}")
            # Fallback to a minimal default prompt if file not found
            return "Eres un asistente IA. Responde en español."
        except Exception as e:
            logging_manager.log_error(f"Error leyendo el archivo de prompt del sistema: {e}")
            return "Eres un asistente IA. Responde en español."

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Makes a direct call to the Gemini API.
        The 'prompt' received here should include system instructions and conversation history,
        managed by the calling code (e.g., ConversationChain in agent.py).
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}], # Send the full prompt as received
            "generationConfig": {"maxOutputTokens": 512}
        }
        params = {"key": self.api_key}

        # Log the prompt being sent (might be long with history)
        # Consider logging only the last part or truncating for brevity if needed
        logging_manager.log_debug("Prompt Completo Enviado a API", prompt)

        try:
            response = requests.post(self.endpoint, headers=headers, json=data, params=params)
            response.raise_for_status()
            result = response.json()
            raw_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            logging_manager.log_debug("Respuesta Cruda API", raw_text)
            response_text = raw_text
        except requests.exceptions.RequestException as e:
            logging_manager.log_error(f"Error en llamada API Gemini: {e}")
            # Return a specific error message or raise an exception
            return "respuesta usuario: Error al contactar el modelo de lenguaje."
        except Exception as e:
            logging_manager.log_error(f"Error inesperado procesando respuesta API: {e}")
            return "respuesta usuario: Error inesperado al procesar la respuesta del modelo."

        # --- Robust Parsing ---
        # (Parsing logic remains the same, but now applied to response from chain)
        text_cleaned = re.sub(r"^```(?:\w+\n)?(.*?)```$", r"\1", response_text, flags=re.DOTALL | re.MULTILINE).strip()

        # Look for the expected labels
        match_command = re.match(r"execute_command:\s*(.*)", text_cleaned, re.IGNORECASE | re.DOTALL)
        match_response = re.match(r"respuesta usuario:\s*(.*)", text_cleaned, re.IGNORECASE | re.DOTALL)
        match_replace = re.match(r"replace:\s*search=(.*?) replace=(.*)", text_cleaned, re.IGNORECASE | re.DOTALL)

        if match_command:
            parsed_response = f"execute_command: {match_command.group(1).strip()}"
            logging_manager.log_debug("Respuesta Parseada", parsed_response)
            return parsed_response
        elif match_response:
            parsed_response = f"respuesta usuario: {match_response.group(1).strip()}"
            logging_manager.log_debug("Respuesta Parseada", parsed_response)
            return parsed_response
        elif match_replace:
            search_term = match_replace.group(1).strip()
            replace_term = match_replace.group(2).strip()
            parsed_response = f"replace: search={search_term} replace={replace_term}"
            logging_manager.log_debug("Respuesta Parseada", parsed_response)
            return parsed_response
        else:
            # Fallback: If no label found, assume it's a response to the user
            logging_manager.log_debug("Respuesta Parseada (Fallback)", f"respuesta usuario: {text_cleaned}")
            return f"respuesta usuario: {text_cleaned}" # Return the cleaned text as user response

    def _clean_and_parse_response(self, raw_text: str) -> str:
        """
        (This method is now effectively replaced by the logic within _call)
        Kept for potential future refactoring or if called elsewhere,
        but the primary parsing now happens directly in _call.
        """
        # Simple pass-through or basic cleaning if needed,
        # but main logic is above.
        return raw_text.strip()

        # --- Robust Parsing (Moved from the end of the old _call) ---
        # This parsing logic should ideally live where the response is *used* (agent.py),
        # but we keep it here for now to maintain the LLM's output format contract.
        text_cleaned = re.sub(r"^```(?:\w+\n)?(.*?)```$", r"\1", response_text, flags=re.DOTALL | re.MULTILINE).strip()

        match_command = re.match(r"execute_command:\s*(.*)", text_cleaned, re.IGNORECASE | re.DOTALL)
        match_response = re.match(r"respuesta usuario:\s*(.*)", text_cleaned, re.IGNORECASE | re.DOTALL)
        match_replace = re.match(r"replace:\s*search=(.*?) replace=(.*)", text_cleaned, re.IGNORECASE | re.DOTALL)

        if match_command:
            parsed_response = f"execute_command: {match_command.group(1).strip()}"
            logging_manager.log_debug("Respuesta Parseada (LLM)", parsed_response)
            return parsed_response
        elif match_response:
            parsed_response = f"respuesta usuario: {match_response.group(1).strip()}"
            logging_manager.log_debug("Respuesta Parseada (LLM)", parsed_response)
            return parsed_response
        elif match_replace:
            search_term = match_replace.group(1).strip()
            replace_term = match_replace.group(2).strip()
            parsed_response = f"replace: search={search_term} replace={replace_term}"
            logging_manager.log_debug("Respuesta Parseada (LLM)", parsed_response)
            return parsed_response
        else:
            logging_manager.log_debug("Respuesta Parseada (LLM Fallback)", f"respuesta usuario: {text_cleaned}")
            return f"respuesta usuario: {text_cleaned}"

    # Remove the now unused _clean_and_parse_response method
    # def _clean_and_parse_response(self, raw_text: str) -> str: ...
