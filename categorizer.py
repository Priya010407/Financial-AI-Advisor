def categorize(text):
    """
    Categorize an expense based on extracted receipt text.
    """

    text = text.lower()

    categories = {
        "Food & Dining": [
            "restaurant",
            "cafe",
            "pizza",
            "burger",
            "food",
            "zomato",
            "swiggy",
            "coffee",
            "tea"
        ],

        "Groceries": [
            "mart",
            "supermarket",
            "grocery",
            "milk",
            "vegetables",
            "fruit",
            "rice",
            "wheat"
        ],

        "Shopping": [
            "mall",
            "shirt",
            "jeans",
            "clothes",
            "fashion",
            "amazon",
            "flipkart"
        ],

        "Transportation": [
            "uber",
            "ola",
            "petrol",
            "diesel",
            "fuel",
            "bus",
            "train"
        ],

        "Medical": [
            "hospital",
            "clinic",
            "pharmacy",
            "medicine",
            "tablet",
            "doctor"
        ],

        "Entertainment": [
            "movie",
            "cinema",
            "netflix",
            "spotify",
            "game"
        ]
    }

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "Other"