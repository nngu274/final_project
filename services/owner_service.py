import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import uuid
import logging

def format_price(value):
    return f"${value:,.2f}"


def product_option_label(product):
    return f"{product['name']} ({product['id'][:8]})"


def find_product_by_id(products, product_id):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def filter_products(products, search_text, category, shelf):
    filtered = []
    search_text = search_text.lower().strip()
    for product in products:
        if search_text:
            if search_text not in product["name"].lower() and search_text not in product["category"].lower():
                continue
        if category != "All" and product["category"] != category:
            continue
        if shelf != "All" and product["shelf"] != shelf:
            continue
        filtered.append(product)
    return filtered


def sort_products(products, sort_key, ascending=True):
    if sort_key == "Name":
        return sorted(products, key=lambda p: p["name"].lower(), reverse=not ascending)
    if sort_key == "Price":
        return sorted(products, key=lambda p: p["price"], reverse=not ascending)
    if sort_key == "Stock":
        return sorted(products, key=lambda p: p["stock"], reverse=not ascending)
    return products
