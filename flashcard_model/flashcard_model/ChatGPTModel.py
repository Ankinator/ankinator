import time
from typing import List, Tuple

from PIL.Image import Image

from flashcard_model.Model import Model

import os
from dotenv import load_dotenv
import openai


class ChatGPTModel(Model):
    def model_forward(self, extracted_pages: List[Tuple[int, str, str, Image]]) -> List[Tuple[int, List[str]]]:
        # Implement chatgpt model here
        load_dotenv()
        openai.api_key = os.getenv("OPENAI-API-KEY")
        results = []
        for i in range(3):
            card_back = extracted_pages[i][1]  # storing the input as back of the card
            #print("card back = " + card_back)
            #print("extracted page number = " + str(extracted_pages[i][0]))

            generated_question = "Open AI services not available"
            for i in range(3):
                try:
                    generated_question = self.chat_gpt(
                        "Generate a question in a flashcard style for the following content: " + card_back)
                    break
                except Exception:
                    time.sleep(1)
                    continue

            results.append((extracted_pages[i][0], [generated_question]))

        return results

    def chat_gpt(self, prompt):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

