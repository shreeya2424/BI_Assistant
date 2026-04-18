class ResponseFormatter:
    """
    Converts execution results into user-facing answers.
    """

    def format(self, intent, execution_result):
        if execution_result["status"] == "unsupported":
            return (
                f"I cannot answer that reliably because the uploaded dataset does not include "
                f"{execution_result['reason']}."
            )

        if execution_result["status"] == "unknown":
            return (
                "I cannot answer that reliably from the uploaded data. "
                "Please ask about product revenue, rankings, transactions, dates, or sales patterns."
            )

        intent_type = execution_result["type"]

        if intent_type == "total_revenue":
            return f"Total revenue is ₹{execution_result['value']:,.0f}."

        if intent_type == "total_transactions":
            return f"Total transactions are {execution_result['value']}."

        if intent_type == "average_sale":
            return f"Average sale value is ₹{execution_result['value']:,.0f}."

        if intent_type == "highest_revenue_product":
            return (
                f"The product that generated the highest revenue is {execution_result['product']}, "
                f"with revenue of ₹{execution_result['value']:,.0f}."
            )

        if intent_type == "lowest_revenue_product":
            return (
                f"The product with the lowest revenue is {execution_result['product']}, "
                f"with revenue of ₹{execution_result['value']:,.0f}."
            )

        if intent_type == "improve_priority":
            return (
                f"The product that should be improved first is {execution_result['product']}, "
                f"because it has the lowest revenue of ₹{execution_result['value']:,.0f}. "
                f"This indicates it is underperforming compared to the other products. "
                f"However, the exact reason for its lower performance cannot be determined from the available data."
            )

        if intent_type == "not_focus_priority":
            return (
                f"The product you should NOT prioritize for improvement is {execution_result['product']}, "
                f"because it already performs the best with a revenue of ₹{execution_result['value']:,.0f}. "
                f"It is already contributing strongly to the business, so improvement effort would be more impactful on weaker products."
            )

        if intent_type == "consistency_explanation":
            return (
                f"These answers are different because they refer to two different priorities. "
                f"{execution_result['lowest_product']} is the product to improve first because it has the lowest revenue "
                f"and is underperforming. {execution_result['top_product']} is the product not to prioritize for improvement "
                f"because it already has the highest revenue and is performing best. "
                f"So the logic is consistent: improve the weakest product, not the strongest one."
            )

        if intent_type == "best_sales_day":
            return f"The best sales day is {execution_result['day']}, with revenue of ₹{execution_result['value']:,.0f}."

        if intent_type == "worst_sales_day":
            return f"The lowest sales day is {execution_result['day']}, with revenue of ₹{execution_result['value']:,.0f}."

        if intent_type == "sales_on_date":
            if execution_result["value"] == 0:
                return f"No sales were found for {execution_result['date']} in the uploaded data."
            return f"Total sales on {execution_result['date']} are ₹{execution_result['value']:,.0f}."

        if intent_type == "top_products":
            lines = [f"{name}: ₹{value:,.0f}" for name, value in execution_result["items"]]
            return "Top products by revenue:\n" + "\n".join(lines)

        if intent_type == "product_revenue":
            if execution_result["value"] == 0:
                return f"No revenue was found for {execution_result['product']} in the uploaded data."
            return f"Revenue for {execution_result['product']} is ₹{execution_result['value']:,.0f}."

        if intent_type == "compare_products":
            items = execution_result["items"]
            lines = [f"{name}: ₹{value:,.0f}" for name, value in items]
            return "Revenue comparison:\n" + "\n".join(lines)

        if intent_type == "stock_inference":
            product = execution_result["product"]
            top_phrase = " and is the top-performing product" if execution_result["is_top_product"] else ""
            return (
                f"From a sales perspective, {product} appears important because it has generated strong revenue{top_phrase}. "
                f"So it would be reasonable to keep it available from a business perspective. "
                f"However, I cannot confirm actual stock sufficiency or reorder quantity because the uploaded dataset does not include inventory or remaining stock information."
            )

        if intent_type == "summary":
            metrics = execution_result["metrics"]
            return (
                f"Overall business summary: Total revenue is ₹{metrics['total_revenue']:,.0f}, "
                f"total transactions are {metrics['total_transactions']}, "
                f"average sale value is ₹{metrics['avg_sale']:,.0f}, "
                f"and the top product is {metrics['top_product']}."
            )

        return (
            "I cannot answer that reliably from the uploaded data. "
            "Please ask about product revenue, rankings, transactions, dates, or sales patterns."
        )