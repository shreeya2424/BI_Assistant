import pandas as pd


class QueryExecutor:
    """
    Executes structured intents on the dataframe/results.
    """

    def __init__(self):
        pass

    def _product_sales_desc(self, data):
        return data.groupby("Product")["Total"].sum().sort_values(ascending=False)

    def _product_sales_asc(self, data):
        return self._product_sales_desc(data).sort_values()

    def _day_sales(self, data):
        temp = data.copy()
        temp["Date"] = pd.to_datetime(temp["Date"], errors="coerce")
        temp = temp.dropna(subset=["Date"])
        temp["DayOfWeek"] = temp["Date"].dt.day_name()
        ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return temp.groupby("DayOfWeek")["Total"].sum().reindex(ordered_days).dropna()

    def execute(self, intent, results, data):
        intent_type = intent["type"]

        if intent_type == "unsupported":
            return {
                "status": "unsupported",
                "reason": intent["reason"]
            }

        if intent_type == "total_revenue":
            return {
                "status": "ok",
                "type": intent_type,
                "value": float(results["metrics"]["total_revenue"])
            }

        if intent_type == "total_transactions":
            return {
                "status": "ok",
                "type": intent_type,
                "value": int(results["metrics"]["total_transactions"])
            }

        if intent_type == "average_sale":
            return {
                "status": "ok",
                "type": intent_type,
                "value": float(results["metrics"]["avg_sale"])
            }

        if intent_type == "highest_revenue_product":
            ps = self._product_sales_desc(data)
            return {
                "status": "ok",
                "type": intent_type,
                "product": ps.index[0],
                "value": float(ps.iloc[0])
            }

        if intent_type == "lowest_revenue_product":
            ps = self._product_sales_asc(data)
            return {
                "status": "ok",
                "type": intent_type,
                "product": ps.index[0],
                "value": float(ps.iloc[0])
            }

        if intent_type == "improve_priority":
            ps = self._product_sales_asc(data)
            return {
                "status": "ok",
                "type": intent_type,
                "product": ps.index[0],
                "value": float(ps.iloc[0])
            }

        if intent_type == "not_focus_priority":
            ps = self._product_sales_desc(data)
            return {
                "status": "ok",
                "type": intent_type,
                "product": ps.index[0],
                "value": float(ps.iloc[0])
            }

        if intent_type == "consistency_explanation":
            top_ps = self._product_sales_desc(data)
            low_ps = self._product_sales_asc(data)
            return {
                "status": "ok",
                "type": intent_type,
                "top_product": top_ps.index[0],
                "top_value": float(top_ps.iloc[0]),
                "lowest_product": low_ps.index[0],
                "lowest_value": float(low_ps.iloc[0])
            }

        if intent_type == "best_sales_day":
            ds = self._day_sales(data)
            return {
                "status": "ok",
                "type": intent_type,
                "day": ds.idxmax(),
                "value": float(ds.max())
            }

        if intent_type == "worst_sales_day":
            ds = self._day_sales(data)
            return {
                "status": "ok",
                "type": intent_type,
                "day": ds.idxmin(),
                "value": float(ds.min())
            }

        if intent_type == "sales_on_date":
            date_value = intent["date"]
            value = float(data[data["Date"].astype(str) == date_value]["Total"].sum())
            return {
                "status": "ok",
                "type": intent_type,
                "date": date_value,
                "value": value
            }

        if intent_type == "top_products":
            limit = int(intent["limit"])
            ps = self._product_sales_desc(data).head(limit)
            return {
                "status": "ok",
                "type": intent_type,
                "items": [(idx, float(val)) for idx, val in ps.items()]
            }

        if intent_type == "product_revenue":
            product = intent["product"]
            value = float(data[data["Product"].astype(str).str.lower() == product.lower()]["Total"].sum())
            return {
                "status": "ok",
                "type": intent_type,
                "product": product,
                "value": value
            }

        if intent_type == "compare_products":
            products = intent["products"]
            output = []
            for product in products:
                value = float(data[data["Product"].astype(str).str.lower() == product.lower()]["Total"].sum())
                output.append((product, value))
            return {
                "status": "ok",
                "type": intent_type,
                "items": output
            }

        if intent_type == "stock_inference":
            ps = self._product_sales_desc(data)
            product = intent.get("product")
            if not product:
                product = ps.index[0]
            value = float(ps.get(product, 0))
            top_product = ps.index[0]
            return {
                "status": "ok",
                "type": intent_type,
                "product": product,
                "value": value,
                "is_top_product": product == top_product
            }

        if intent_type == "summary":
            return {
                "status": "ok",
                "type": intent_type,
                "metrics": results["metrics"],
                "insights": results["insights"],
                "forecast": results["forecast"]
            }

        return {
            "status": "unknown",
            "type": intent_type
        }