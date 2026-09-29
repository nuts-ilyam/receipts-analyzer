from sqlalchemy import MetaData, Column, Integer, String, DateTime, Float, Text, text, ForeignKey, func
from sqlalchemy.orm import declarative_base


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=naming_convention)

Base = declarative_base(metadata=metadata)


class Receipts(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True)
    purchase_date = Column(DateTime)
    created_date = Column(DateTime, server_default=func.now())
    raw_html = Column(Text)
    store_name = Column(String, nullable=False)
    store_address = Column(String)
    total_price = Column(Float)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String)
    # brand

class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    raw_product_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    # unit_price

