import pytest
from bs4 import BeautifulSoup
from src.Product import Product  # Replace 'your_module' with the actual module name
from brainboost_data_source_requests_package.TorRequest import TorRequest

def test_product_extraction():
    url = 'https://articulo.mercadolibre.com.co/MCO-888079705-camara-reversa-carro-vision-nocturna-180-grados-agua-broca-_JM'
    product_data = Product.product_from(url)

    # Check if the product_data is not None
    assert product_data is not None, "Failed to fetch product data"

    # Check if the required keys are present in the returned dictionary
    assert 'Product Title' in product_data, "Product title is missing"
    assert 'Stars' in product_data, "Stars information is missing"
    assert 'Price' in product_data, "Price information is missing"
    assert 'Amount Sold' in product_data, "Amount sold information is missing"
    assert 'Seller' in product_data, "Seller information is missing"
    assert 'Shipping' in product_data, "Shipping information is missing"
    assert 'Returns' in product_data, "Returns information is missing"
    assert 'Additional Info' in product_data, "Additional information is missing"

    # Check that the values are not default 'not found' messages
    assert product_data['Product Title'] != 'Product title not found', "Failed to extract product title"
    assert product_data['Stars'] != 'Rating not found', "Failed to extract rating"
    assert product_data['Price'] != 'Price not found', "Failed to extract price"
    assert product_data['Amount Sold'] != 'Amount sold not found', "Failed to extract amount sold"
    assert product_data['Seller'] != 'Seller information not found', "Failed to extract seller information"
    assert product_data['Shipping'] != 'Shipping information not found', "Failed to extract shipping information"
    assert product_data['Returns'] != 'Returns information not found', "Failed to extract returns information"
    assert product_data['Additional Info'] != 'Additional information not found', "Failed to extract additional information"

# To run the tests, execute the following command in your terminal:
# pytest test_product.py
