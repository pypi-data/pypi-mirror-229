# type : ignore
from dataclasses import dataclass
from typing import List, Union

import torch
import torch.nn.functional as F
from kodali import NerTags
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast

from luie.labels.named_entity_recognition.korean_corpus import NerKoreanCorpusLabels
from luie.models.sequence_labeling import SequenceLabelingModel
from luie.tokenizers import KoCharElectraTokenizer

TOKENIZER_NAME = "monologg/kocharelectra-base-discriminator"

HF_MODEL_NAME = "chnaaam/kocharelectra-ner"


@dataclass
class NerOutput:
    word: str
    label: str
    start_idx: int
    end_idx: int


def decode(
    tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
    token_ids: List[int],
    labels: List[str],
) -> List[NerOutput]:
    outputs = []
    buffer = {}

    for idx, label in enumerate(labels):
        if label.startswith(str(NerTags.SINGLE)):
            outputs.append(
                NerOutput(
                    word=tokenizer.decode(token_ids=token_ids[idx]),
                    label=label.replace(f"{str(NerTags.SINGLE)}", ""),
                    start_idx=idx,
                    end_idx=idx,
                )
            )
        if label.startswith(str(NerTags.BEGIN)):
            buffer = {
                "idx": idx,
                "label": label.replace(f"{str(NerTags.BEGIN)}-", ""),
            }
        elif label.startswith(str(NerTags.END)):
            start_idx = buffer["idx"]
            label = buffer["label"]

            outputs.append(
                NerOutput(
                    word=tokenizer.decode(token_ids=token_ids[start_idx : idx + 1]),
                    label=label,
                    start_idx=start_idx,
                    end_idx=idx,
                )
            )

            # Reset
            start_idx = -1
            label = str(NerTags.OUTSIDE)

    return outputs


class NerInferenceEngineModule:
    def __init__(self, device_id: int = 0) -> None:
        self.device = f"cuda:{device_id}" if device_id != -1 else "cpu"

        if not torch.cuda.is_available():
            self.device = "cpu"

        self.model = SequenceLabelingModel(model_name=HF_MODEL_NAME)
        self.model.eval()
        self.model = self.model.to(self.device)  # type: ignore

        self.tokenizer = KoCharElectraTokenizer.from_pretrained(TOKENIZER_NAME)

    def run(self, sentence: str) -> List[NerOutput]:
        encoded_inputs = self.tokenizer(sentence, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in encoded_inputs.items()}

        outputs = self.model(**inputs)
        outputs = torch.argmax(F.softmax(outputs.logits, dim=-1), dim=-1).tolist()[0]

        outputs = decode(
            tokenizer=self.tokenizer,
            token_ids=encoded_inputs["input_ids"].tolist()[0][1:-1],  # Skip CLS and SEP tokens,
            labels=[NerKoreanCorpusLabels.IDX2LABEL[str(o)] for o in outputs][1:-1],  # Skip CLS and SEP tokens,
        )

        return outputs
