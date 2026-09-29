import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from bs4 import BeautifulSoup


@dataclass
class Item:
    name: str
    quantity: Decimal
    unit_price: Decimal
    total: Decimal


@dataclass
class ParsedReceipt:
    store: str
    address: str
    purchase_datetime: datetime
    total: Decimal
    items: list[Item]


class Parser:
    def __init__(self):
        self.store_name = "Base"

    @staticmethod
    def _get_rows(soup: BeautifulSoup) -> list:
        return soup.find_all("tr")

    def _get_text(self, soup) -> str:
        return soup.get_text(" ", strip=True)

    def _get_store_name(self):
        return "Default Store"

    def _get_store_address(self):
        return "Default address"

    @staticmethod
    def _get_receipt_items(soup: BeautifulSoup) -> list[Item]:
        pass

    def _get_total(self, soup: BeautifulSoup) -> Decimal:
        pass

    def _get_purchase_datetime(self, soup: BeautifulSoup) -> datetime:
        pass

    def get_parsed_receipt(self, html: str):
        soup = BeautifulSoup(html, "html.parser")

        return ParsedReceipt(
            store=self._get_store_name(),
            address=self._get_store_address(),
            purchase_datetime=self._get_purchase_datetime(soup),
            total=self._get_total(soup),
            items=self._get_receipt_items(soup)
        )


class LentaParser(Parser):

    def _get_store_name(self) -> str:
        return "Lenta"

    def _get_purchase_datetime(self, soup: BeautifulSoup) -> datetime:
        text = self._get_text(soup)
        match = re.search(
            r"КАССОВЫЙ ЧЕК №:\s*\d+\s+"
            r"(\d{2}\.\d{2}\.\d{2}\s+\d{2}:\d{2})",
            text,
        )

        if not match:
            return None

        return datetime.strptime(
            match.group(1),
            "%d.%m.%y %H:%M",
        )

    def _get_total(self, soup: BeautifulSoup) -> Decimal:
        text = self._get_text(soup)
        match = re.search(r"ИТОГО: (\d+(?:\.\d+)?)", text)
        if not match:
            return None
        return Decimal(match.group(1))

    @staticmethod
    def _get_receipt_items(soup: BeautifulSoup) -> list[Item]:
        items = []

        for hr in soup.find_all("hr"):
            block = hr.find_parent("div")

            if not block:
                continue

            tables = block.find_all("table", recursive=False)

            if len(tables) < 2:
                continue

            # Первая таблица блока содержит название
            name = tables[0].get_text(" ", strip=True)

            # Ищем таблицу с quantity x unit_price | total
            for table in tables[1:]:
                cells = table.find_all("td", recursive=True)

                if len(cells) != 2:
                    continue

                left = cells[0].get_text(" ", strip=True)
                right = cells[1].get_text(" ", strip=True)

                match = re.fullmatch(
                    r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)",
                    left,
                )

                if not match:
                    continue

                items.append(Item(name=name,
                                  quantity=Decimal(match.group(1)),
                                  unit_price=Decimal(match.group(2)),
                                  total=Decimal(right)))

                break

        return items


class MagnitParser(Parser):
    def _get_store_name(self) -> str:
        return "Magnit"

    def _get_purchase_datetime(self, soup: BeautifulSoup) -> datetime | None:

        rows = self._get_rows(soup)
        for row in rows:
            text = self._get_text(row)

            try:
                return datetime.strptime(
                    text,
                    "%d.%m.%Y %H:%M",
                )
            except ValueError:
                continue

        return None

    def _get_store_address(self):
        return "Magnit address"

    def _get_total(self, soup: BeautifulSoup) -> Decimal:
        # same as for Lenta
        text = self._get_text(soup)
        match = re.search(r"ИТОГО: (\d+(?:\.\d+)?)", text)
        if not match:
            return None
        return Decimal(match.group(1))


    def _get_receipt_items(self, soup: BeautifulSoup) -> list[Item]:

        products = []

        for row in soup.find_all("tr"):
            cells = row.find_all("td", recursive=False)

            if len(cells) != 4:
                continue

            values = [
                cell.get_text(" ", strip=True)
                for cell in cells
            ]

            name, quantity, unit_price, total = values

            try:
                quantity = Decimal(quantity)
                unit_price = Decimal(unit_price)
                total = Decimal(total)
            except Exception:
                continue

            products.append(Item(name=name,
                                 quantity=quantity,
                                 unit_price=unit_price,
                                 total=total))

        return products

