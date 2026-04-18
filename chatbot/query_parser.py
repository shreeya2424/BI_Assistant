import re
from typing import Dict, List, Optional


class QueryParser:
    """
    Converts user questions into structured query intents.
    """

    def __init__(self):
        pass

    def _normalize(self, text: str) -> str:
        return text.strip().lower()

    def _extract_top_n(self, text: str) -> Optional[int]:
        match = re.search(r"\btop\s+(\d+)\b", text)
        if match:
            return int(match.group(1))
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
        if match:
            return match.group(0)
        return None

    def _extract_product(self, text: str, products: List[str]) -> Optional[str]:
        text_lower = text.lower()
        sorted_products = sorted(products, key=len, reverse=True)
        for product in sorted_products:
            if product.lower() in text_lower:
                return product
        return None

    def parse(self, question: str, data) -> Dict:
        q = self._normalize(question)
        products = data["Product"].dropna().astype(str).unique().tolist()

        # unsupported domains
        unsupported_keywords = {
            "profit": "profit or cost/margin data",
            "margin": "profit or cost/margin data",
            "customer satisfaction": "customer satisfaction data",
            "review": "review data",
            "sentiment": "sentiment data",
            "inventory": "inventory data",
            "stock left": "inventory data",
            "remaining stock": "inventory data",
            "reorder": "inventory data",
        }
        for keyword, reason in unsupported_keywords.items():
            if keyword in q:
                return {"type": "unsupported", "reason": reason}

        # exact metric queries
        if "total revenue" in q or "total sales" in q:
            return {"type": "total_revenue"}

        if "total transactions" in q or "how many transactions" in q:
            return {"type": "total_transactions"}

        if "average sale" in q or "average transaction" in q:
            return {"type": "average_sale"}

        if (
            "highest revenue" in q
            or "generated highest revenue" in q
            or "top product" in q
            or "best product" in q
        ):
            return {"type": "highest_revenue_product"}

        if (
            "lowest revenue" in q
            or "least revenue" in q
            or "product with lowest revenue" in q
            or "worst product" in q
        ):
            return {"type": "lowest_revenue_product"}

        # strategy questions
        if "improve" in q and "product" in q:
            return {"type": "improve_priority"}

        if "not focus" in q or "not prioritize" in q or "avoid focusing" in q:
            return {"type": "not_focus_priority"}

        if (
            "why are these different" in q
            or "why are they different" in q
            or "how are these different" in q
            or "is your logic consistent" in q
            or "how is that consistent" in q
        ):
            return {"type": "consistency_explanation"}

        # date/day questions
        if "best day" in q or "highest sales day" in q:
            return {"type": "best_sales_day"}

        if "worst day" in q or "lowest sales day" in q:
            return {"type": "worst_sales_day"}

        date_value = self._extract_date(q)
        if date_value and ("sales on" in q or "revenue on" in q or "total on" in q):
            return {"type": "sales_on_date", "date": date_value}

        # top N products
        top_n = self._extract_top_n(q)
        if top_n and "product" in q:
            return {"type": "top_products", "limit": top_n}

        # product-specific revenue
        product = self._extract_product(q, products)
        if product and (
            "revenue for" in q
            or "sales for" in q
            or "revenue of" in q
            or "sales of" in q
        ):
            return {"type": "product_revenue", "product": product}

        # compare products
        if "compare" in q:
            matched = []
            for p in products:
                if p.lower() in q:
                    matched.append(p)
            if len(matched) >= 2:
                return {"type": "compare_products", "products": matched[:2]}

        # stock/inventory style: sales-based inference only
        if "stock" in q or "inventory" in q or "reorder" in q:
            product = self._extract_product(q, products)
            return {"type": "stock_inference", "product": product}

        # summary question
        if (
            "summarize" in q
            or "summary" in q
            or "business performance" in q
            or "sales trend" in q
            or "forecast" in q
        ):
            return {"type": "summary"}

        return {"type": "unknown"}