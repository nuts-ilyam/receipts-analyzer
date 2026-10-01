import re
from typing import List

from imap_tools import MailMessage
from sqlalchemy import select

from config import db_session
from db.models import Receipts, ReceiptItem
from parser import LentaParser, MagnitParser

WASTE_SUBSTR_MAPPER = {
    "; шт.": "",
    "; кг.": "",
    "; кг": "",
    "вес": "",
    "пл/ст":"",
    "п/уп":"",
    "пэт":"",
    "уп":""
}

STANDARD_MEASURES_MAPPER = {"l": "л", "ml": "мл", "g": "г", "kg": "кг",
                            }


def replace_substrings(text: str, mapper: dict):
    # Create a regex pattern from the dictionary keys
    pattern = re.compile("|".join(map(re.escape, mapper.keys())))

    # Replace matches using a lambda function lookup
    return pattern.sub(lambda match: mapper[match.group(0)], text)


def reorder_product_measures(product_name: str):
    pattern = r"\d+(?:[.,]\d+)?\s*(?:кг|г|kg|g|l|ml|л|мл|%)\s*"
    extracted_weights = []

    def extract_and_replace(match):
        # 1. Extract the found text and save it
        found_text = match.group(0).replace(" ", "")
        found_text = replace_substrings(found_text, STANDARD_MEASURES_MAPPER)
        extracted_weights.append(found_text)

        # 2. Return the replacement string
        return ""

    # re.sub calls the function for every match it finds
    modified_text = re.sub(pattern=pattern, repl=extract_and_replace,
                           string=product_name, flags=re.IGNORECASE)
    measures = " ".join(extracted_weights)
    return modified_text + " " + measures



def normalize_product_name(value: str) -> str:
    value = value.lower()

    # remove waste characters
    value = replace_substrings(value,mapper=WASTE_SUBSTR_MAPPER)

    # move all measures (kilo, liter, % to the end of string)
    value = reorder_product_measures(value)

    #remove extra space
    value = re.sub(r"\s+", " ", value)

    return value


def run_email_processing(messages: List[MailMessage]):
    counter = 0
    for message in messages:
        header = message.subject
        if "Лента" in header:
            parser = LentaParser()
        elif "МАГНИТ" in header:
            parser = MagnitParser()
        else:
            continue

        html = message.html

        parser_receipt = parser.get_parsed_receipt(html)

        new_receipt = Receipts(purchase_date=parser_receipt.purchase_datetime,
                               raw_html=html,
                               store_name=parser_receipt.store,
                               store_address=parser_receipt.address,
                               total_price=parser_receipt.total)
        products = parser_receipt.items

        with db_session() as db:

            stmt = select(Receipts).where(Receipts.purchase_date == parser_receipt.purchase_datetime,
                                          Receipts.store_name == parser_receipt.store).exists()  #
            is_exist = db.scalar(select(stmt))

            if not is_exist:
                db.add(new_receipt)
                db.commit()
                for product in products:
                    # get product id
                    new_receipt_item = ReceiptItem(
                        raw_product_name=normalize_product_name(product.name),
                        quantity=product.quantity,
                        price=product.total,
                        receipt_id=new_receipt.id)

                    db.add(new_receipt_item)
                db.commit()

                counter += 1

    return counter
