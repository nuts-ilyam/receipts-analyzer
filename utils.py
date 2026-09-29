import re
from typing import List

from imap_tools import MailMessage
from sqlalchemy import select

from config import db_session
from db.models import Receipts, ReceiptItem
from parser import LentaParser, MagnitParser


def normalize_text(value: str) -> str:
    mapping = {"ё" : "е",
              ";": ""}
    value = value.lower()
    table = str.maketrans(mapping)

    value = value.translate(table)

    # value = re.sub(r"[^а-яa-z0-9]+", " ", value)
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
                        raw_product_name=normalize_text(product.name),
                        quantity=product.quantity,
                        price=product.total,
                        receipt_id=new_receipt.id)

                    db.add(new_receipt_item)
                db.commit()

                counter += 1

    return counter
