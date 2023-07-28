import base64
import io
import random
from typing import List

import genanki

from api.extractor_database import load_processed_data
from api.pdf_document_database import load_pdf_file
from api.user_database import get_user


def create_anki_export(username: str, result_id: str, questions: List[str]) -> bytes:
    processed_data = load_processed_data(result_id)
    flashcards = []

    for index, question in enumerate(questions, 0):
        if question is None:
            continue

        back_image = processed_data[index][3]
        buffered = io.BytesIO()
        back_image.save(buffered, format="PNG")
        back_image_encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")

        model_id = random.randrange(1 << 30, 1 << 31)
        new_model = genanki.Model(
            model_id,
            f'Ankinator Model {model_id}',
            fields=[
                {'name': 'Question'},
                {'name': 'Image'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}',
                    'afmt': '{{Image}}'
                }
            ]
        )

        image_src_field = f'<img src="data:image/png;base64,{back_image_encoded}">'
        my_note = genanki.Note(
            model=new_model,
            fields=[question, image_src_field]
        )
        flashcards.append(my_note)

    deck_id = random.randrange(1 << 30, 1 << 31)

    db_user = get_user(username)
    pdf_document_id = db_user.model_results[result_id]["pdf_document_id"]
    _, pdf_document_name = load_pdf_file(pdf_document_id)

    deck = genanki.Deck(deck_id, pdf_document_name + " flashcards")
    for flashcard in flashcards:
        deck.add_note(flashcard)

    package = genanki.Package(deck)
    anki_package_bytes = io.BytesIO()
    package.write_to_file(anki_package_bytes)

    return anki_package_bytes.getvalue()
