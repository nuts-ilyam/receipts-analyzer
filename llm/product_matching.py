from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from config import db_session
from sqlalchemy import text, func, select
import json

from llm.constants import DUPL_FILTER_THRESHOLD, DUPL_LIMIT
from llm.utils import response_format,user_prompt, system_prompt
from db.models import Product
from openai import OpenAI
from config import settings

def get_llm_candidates(search_product_name: str) -> dict[int, str] | None:
    with db_session() as db:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        db.commit()

        score_col = func.similarity(Product.name, search_product_name).label("score")

        stmt = (
            select(Product.id,
                   Product.name,
                   score_col
                   )
            .where(score_col > DUPL_FILTER_THRESHOLD)
            .order_by(score_col.desc())
            .limit(DUPL_LIMIT)
        )
        # if empty
        result = db.execute(stmt).all()
        if result:
            candidates_dict = {x[0] : x[1] for x in result}
            return candidates_dict
        else:
            return None

def prepare_user_prompt(product_name: str, candidates: dict[int, str]) -> str:
    return user_prompt.format(
        product_name=product_name,
        candidates="\n".join(f"ID={k} : {v}" for k, v in candidates.items())
    )

def get_matched_product_id(product_name: str)-> int|None:

    llm_candidates_dict = get_llm_candidates(product_name)

    if llm_candidates_dict:
        client = OpenAI(
            base_url=settings.llm.llm_base_url,
            api_key=settings.llm.llm_api_key,
        )
#todo try-catch if response
        response = client.chat.completions.create(
            model=settings.llm.llm_model_name,
            response_format=response_format,
            messages=[
                ChatCompletionSystemMessageParam(role= "system",content=system_prompt),
                ChatCompletionUserMessageParam(role="user",
                                               content=prepare_user_prompt(
                                                   product_name=product_name,
                                                   candidates=llm_candidates_dict
                                               )),
            ],
            temperature=0.1,
        )

        try:
            content = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            content = {}

        return content.get('product_id')
    else:
        return None
