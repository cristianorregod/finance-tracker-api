def transform_chart_data(chart_type, data):
    if not isinstance(data, list) or len(data) == 0:
        return {"series": [], "categories": []}

    if chart_type == "pie":
        return {
            "series": [item["value"] for item in data],
            "categories": [item["label"] for item in data]
        }

    if chart_type in ("bar", "line"):
        keys = list(data[0].keys())
        category_key = "category"
        value_keys = [key for key in keys if key != category_key]

        categories = [item[category_key] for item in data]

        series = [
            {
                "name": key,
                "data": [item[key] for item in data]
            }
            for key in value_keys
        ]

        return {"series": series, "categories": categories}

    raise ValueError(f"Unsupported chart type: {chart_type}")