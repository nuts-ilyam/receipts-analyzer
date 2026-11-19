from ml.category_classifier import ProductClassifier
from ml.constants import CATEGORY_KEYWORDS, MODEL_PATH, MIN_CONFIDENCE


def get_category_by_rules(product_name: str) -> str | None:
    name = product_name.casefold()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.casefold() in name:
                return category

    return None


def get_category_by_lr_clf(product_name: str):
    """

    :param product_name:
    :return:
    """
    classifier = ProductClassifier(MODEL_PATH, min_confidence=MIN_CONFIDENCE)
    cat, conf = classifier.predict_category(product_name)
    print(f"{product_name} -> {cat} ({conf:.2f})")
    return cat


def get_category(product_name: str) -> str|None:
    """

    :param product_name:
    :return:
    """
    cat_ml = get_category_by_lr_clf(product_name)
    cat_rule = get_category_by_rules(product_name)
    if (cat_ml == cat_rule) | (cat_rule is None):
        return cat_ml
    else:
        return None