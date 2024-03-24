# gpt.py
import requests
import json
import logging

def generate_response(user_message, context_messages, theme=None, level=None):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": context_messages,
        "theme": theme,
        "level": level,
        "temperature": 0.7,
        "max_tokens": 50
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get('choices') and data['choices'][0].get('message') and data['choices'][0]['message'].get('content'):
            answer = data['choices'][0]['message']['content']
            logging.info(f"Ответ ИИ: {answer}")
            return answer
        else:
            logging.warning(f"Неожиданная структура ответа от ИИ: {data}")
            return "Не удалось получить ответ от ИИ."
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к ИИ-сервису: {e}")
        return "Извините, произошла ошибка при обращении к ИИ-сервису."
