def build_knowledge_chunks(results):
    chunks = []

    metrics = results["metrics"]
    insights = results["insights"]
    forecast = results["forecast"]

    chunks.append(
        f"Total revenue is ₹{metrics['total_revenue']:,.0f}. "
        f"Total transactions are {metrics['total_transactions']}. "
        f"Average sale value is ₹{metrics['avg_sale']:,.0f}. "
        f"Top product is {metrics['top_product']}. "
        f"Data covers from {metrics['date_start']} to {metrics['date_end']}."
    )

    for insight in insights:
        if "explanation" in insight:
            chunks.append(insight["explanation"])
        elif "text" in insight:
            chunks.append(insight["text"])
        elif "title" in insight:
            chunks.append(insight["title"])

    if forecast:
        forecast_text = "Next 7 day forecast: "
        forecast_lines = []

        for item in forecast:
            if "predicted" in item:
                forecast_lines.append(
                    f"{item['day']} ({item['date'].strftime('%Y-%m-%d')}) sales may be around ₹{item['predicted']:,.0f}."
                )
            elif "predicted_sales" in item:
                forecast_lines.append(
                    f"{item['day']} ({item['date']}) sales may be around ₹{item['predicted_sales']:,.0f}."
                )

        forecast_text += " ".join(forecast_lines)
        chunks.append(forecast_text)

    return chunks