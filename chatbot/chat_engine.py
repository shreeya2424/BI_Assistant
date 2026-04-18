def is_deterministic_question(question):
    q = question.lower()

    keywords = [
        "total revenue",
        "total sales",
        "top product",
        "best product",
        "average sale",
        "average transaction",
        "total transactions",
        "how many transactions",
        "forecast",
        "predicted sales",
        "date range",
        "analysis period"
    ]

    return any(keyword in q for keyword in keywords)


def answer_deterministic(question, results):
    q = question.lower()
    metrics = results["metrics"]
    forecast = results["forecast"]

    if "total revenue" in q or "total sales" in q:
        return f"Total revenue is ₹{metrics['total_revenue']:,.0f}."

    if "top product" in q or "best product" in q:
        return f"The top product is {metrics['top_product']}."

    if "average sale" in q or "average transaction" in q:
        return f"Average sale value is ₹{metrics['avg_sale']:,.0f}."

    if "total transactions" in q or "how many transactions" in q:
        return f"Total transactions are {metrics['total_transactions']}."

    if "date range" in q or "analysis period" in q:
        return f"The data ranges from {metrics['date_start']} to {metrics['date_end']}."

    if "forecast" in q or "predicted sales" in q:
        lines = []
        for item in forecast:
            if "predicted" in item:
                lines.append(
                    f"{item['day']} ({item['date'].strftime('%Y-%m-%d')}): ₹{item['predicted']:,.0f}"
                )
            elif "predicted_sales" in item:
                lines.append(
                    f"{item['day']} ({item['date']}): ₹{item['predicted_sales']:,.0f}"
                )

        return "Next 7-day forecast:\n" + "\n".join(lines)

    return None