from openai.types.shared_params import ResponseFormatJSONSchema
from openai.types.shared_params.response_format_json_schema import JSONSchema
from pydantic import BaseModel, ConfigDict, Field

system_prompt = """Ты — система сопоставления товаров. 
У тебя есть название исходного товара.
Твоя задача — среди кандитатов найти дубликат исходного товара. Учти, что дубликата может и не быть.

Верни только валидный JSON в следующем формате (без markdown-разметки и лишнего текста):
{
  "product_id": ID продукта-дубликата,
  "confidence": степень твоей уверенности в совпадении - вероятность от 0 до 1,

}
"""

user_prompt = """Исходный товар:
{product_name}

Кандидаты:
{candidates}
"""


class CandidateMatch(BaseModel):
    # extra="forbid" добавляет "additionalProperties": False в JSON-схему,
    # что обязательно для strict=True в OpenAI / OpenRouter
    model_config = ConfigDict(extra="forbid")

    product_id: int | None = Field(
        description="ID продукта-дубликата из предложенного списка кандидатов, или null, если дубликата нет"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Степень уверенности в совпадении: вероятность от 0.0 до 1.0",
    )


response_format = ResponseFormatJSONSchema(
    type="json_schema",
    json_schema=JSONSchema(
        name="duplicate_match",
        strict=True,
        schema=CandidateMatch.model_json_schema(),
    ),
)



