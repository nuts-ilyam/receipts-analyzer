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
    def __init__(self, html):
        self.soup = BeautifulSoup(html, "html.parser")

    def _get_text(self) -> str:
        return self.soup.get_text(" ", strip=True)

    def _get_store_name(self):
        return "Default Store"

    def _get_store_address(self):
        return "Default address"

    def _get_receipt_items(self) -> list[Item]:
        pass

    def _get_total(self) -> Decimal:
        pass

    def _get_purchase_datetime(self) -> datetime:
        pass

    def get_parsed_receipt(self):

        return ParsedReceipt(
            store=self._get_store_name(),
            address=self._get_store_address(),
            purchase_datetime=self._get_purchase_datetime(),
            total=self._get_total(),
            items=self._get_receipt_items()
        )


class LentaParser(Parser):

    def _get_store_name(self) -> str:
        return "Lenta"

    def _get_purchase_datetime(self) -> datetime:
        text = self._get_text()
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

    def _get_total(self) -> Decimal:
        text = self._get_text()
        match = re.search(r"ИТОГО: (\d+(?:\.\d+)?)", text)
        if not match:
            return None
        return Decimal(match.group(1))

    def _get_receipt_items(self) -> list[Item]:
        items = []

        for hr in self.soup.find_all("hr"):
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

    def _get_purchase_datetime(self) -> datetime | None:

        rows = self.soup.find_all("tr")
        for row in rows:
            text = row.get_text(" ", strip=True)

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

    def _get_total(self) -> Decimal:
        # same as for Lenta
        text = self._get_text()
        match = re.search(r"ИТОГО: (\d+(?:\.\d+)?)", text)
        if not match:
            return None
        return Decimal(match.group(1))


    def _get_receipt_items(self) -> list[Item]:

        products = []

        for row in self.soup.find_all("tr"):
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


class VkusvillParser(Parser):
    def _get_store_name(self) -> str:
        return "Vkusvill"

    def _get_total(self) -> Decimal | None:
        #the same --> need to refactor (input total pattern )
        text = self._get_text()

        match = re.search(r"ИТОГ (\d+(?:\.\d+)?)", text)
        if not match:
            return None
        return Decimal(match.group(1))

    def _get_purchase_datetime(self) -> datetime:
        text = self._get_text()
        match = re.search(
            r"ДАТА ВЫДАЧИ (\d{2}\.\d{2}\.\d{2}\s+\d{2}:\d{2})",
            text,
        )

        if not match:
            return None

        return datetime.strptime(
            match.group(1),
            "%d.%m.%y %H:%M",
        )

    def _get_receipt_items(self) -> list[Item]:
        products = []

        # В чеке название товара находится внутри <b>.
        for element in self.soup.find_all("b"):
            name = element.get_text(" ", strip=True)

            # Ищем строку таблицы, содержащую название и цены.
            row = element.find_parent("tr")
            if not row:
                continue

            row_text = row.get_text(" ", strip=True)

            # В товарной строке цена указана в формате:
            # количество X цена за единицу.
            price_match = re.search(
                r"(?<![\d.,])"
                r"(\d+(?:[.,]\d+)?)\s*[xх×]\s*"
                r"(\d+(?:[.,]\d+)?)",
                row_text,
                flags=re.IGNORECASE,
            )

            # Отсекаем заголовки и служебные элементы.
            if not price_match:
                continue

            quantity = Decimal(price_match.group(1))
            unit_price = Decimal(price_match.group(2))

            total_match = re.search(
                r"=\s*(\d+(?:[.,]\d+)?)",
                row_text,
            )

            if total_match:
                total = Decimal(
                    total_match.group(1)
                )
            else:
                total = quantity * unit_price

            # Убираем служебную маркировку и единицу учета
            # из конца названия, сохраняя остальные характеристики.
            name = re.sub(r"^\[M\]\s*", "", name)
            name = re.sub(
                r"\s*,\s*шт\.?\s*$",
                "",
                name,
                flags=re.IGNORECASE,
            ).strip()


            products.append(Item(name=name,
                                 quantity=quantity,
                                 unit_price=unit_price,
                                 total=total))

        return products