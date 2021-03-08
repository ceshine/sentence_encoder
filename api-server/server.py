import os
from typing import List, Optional

import typer
import uvicorn
from opencc import OpenCC
from fastapi import FastAPI
from pydantic import BaseModel, Field

from oggdo.encoder import SentenceEncoder


os.environ["TOKENIZERS_PARALLELISM"] = "false"

PORT = int(os.environ.get("PORT", "8666"))
APP = FastAPI()
T2S = OpenCC('t2s')
MODEL: Optional[SentenceEncoder] = None


class TextInput(BaseModel):
    text: str = Field(
        None, title="The piece of text you want to create embeddings for.", max_length=256
    )
    t2s: bool = False


class EmbeddingsResult(BaseModel):
    vector: List[float]


@APP.post("/", response_model=EmbeddingsResult)
def get_embeddings(text_input: TextInput):
    assert MODEL is not None, "MODEL is not loaded."
    text = text_input.text.replace("\n", " ")
    if text_input.t2s:
        text = T2S.convert(text)
    print(text)
    vector = MODEL.encode(
        [text],
        batch_size=1,
        show_progress_bar=True
    )[0]
    return EmbeddingsResult(vector=vector.tolist())


def main(model_path: str = typer.Argument("streamlit-model/")):
    global MODEL
    MODEL = SentenceEncoder(model_path, device="cpu")
    print(f"Listening to port {PORT}")
    uvicorn.run(APP, host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    typer.run(main)
