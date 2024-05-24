from brainboost_data_source_requests_package.Request import Request
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from src.Product import Product
from tinydb import TinyDB, Query
from collections import deque
from configuration import storage_local_mercadolibre_colombia_visited_links
import re

# Initialize TinyDB to persist visited links
db = TinyDB(storage_local_mercadolibre_colombia_visited_links)

def process_product_page(url):
    product_code_pattern = r"/p/([A-Z0-9]+)\?"
    if re.search(product_code_pattern, url):
        product_id = re.search(product_code_pattern, url).group(1)
        return {
            'type': 'product_page',
            'productId': product_id,
            'productName': " ".join(product_id.split("_")).capitalize()  # Capitalizing product name
        }
    return None

def process_category_page(url):
    split_url = urlparse(url).path.split('/')
    if len(split_url) >= 5:
        return {
            'type': 'category_page',
            'categoryName': split_url[4].split("#")[0]
        }
    return None

def process_deal_page(url):
    if "listado.mercadolibre.com.co/_Deal_" in url:
        return {
            'type': 'deal_page',
            'dealName': url.split("_Deal_")[1].split("#")[0]
        }
    return None

def process_filtered_search_results(url):
    if "listado.mercadolibre.com.co/" in url and "_" in url:
        return {
            'type': 'filtered_search_results',
            'searchTerm': url.split("/")[4].split("_")[0],
            'filters': "_".join(url.split("_")[1:]).split("#")[0]
        }
    return None

def process_home_page(url):
    if url == "https://www.mercadolibre.com.co/":
        return {'type': 'home_page'}
    return None

def process_url(url):
    result = {}

    # Check if the URL is from a known domain
    if "mercadolibre.com.co" not in url:
        return {'type': "unknown"}

    # Try each specific URL processor
    result = process_product_page(url)
    if result:
        return result

    result = process_category_page(url)
    if result:
        return result

    result = process_deal_page(url)
    if result:
        return result

    result = process_filtered_search_results(url)
    if result:
        return result

    result = process_home_page(url)
    if result:
        return result

    # If none of the specific processors matched, return unknown
    return {'type': 'unknown'}



def is_internal_link(url, base_url):
    # Check if the URL belongs to the same domain
    return urlparse(url).netloc == urlparse(base_url).netloc

def mark_as_visited(url):
    db.insert({'url': url})

def is_visited(url):
    Link = Query()
    return db.search(Link.url == url)

def traverse_website(root_url):
    to_visit_categories = deque([root_url])
    to_visit_products = deque()
    classified_links = []
    product_data_list = []

    while to_visit_categories or to_visit_products:
        if to_visit_products:
            current_url = to_visit_products.popleft()
        else:
            current_url = to_visit_categories.popleft()

        if is_visited(current_url):
            continue

        mark_as_visited(current_url)
        print(f"Visiting: {current_url}")

        try:
            visit_page_request = Request()
            response = visit_page_request.get(current_url)
            soup = BeautifulSoup(response[1], 'html.parser')
        except Exception as e:
            print(f"Failed to fetch {current_url}: {e}")
            continue

        for link in soup.find_all('a', href=True):
            full_url = urljoin(current_url, link['href'])
            if is_internal_link(full_url, root_url) and not is_visited(full_url):
                classified_link = process_url(full_url)
                if classified_link['type'] == "product_page":
                    to_visit_products.append(full_url)
                elif classified_link['type'] in ["category_page", "filtered_search_results", "deal_page"]:
                    to_visit_categories.append(full_url)
                classified_link['url'] = full_url
                classified_links.append(classified_link)

        if process_url(current_url)['type'] == "product_page":
            product_data = Product.product_from(soup=soup)  # Fetch product data using the URL
            if product_data:
                product_data_list.append(product_data)

    return classified_links, product_data_list

# Test process_url function
url = "https://articulo.mercadolibre.com.co/MCO-1234-product-name_12345"
print(process_url(url))

# Example usage
root_url = "https://www.mercadolibre.com.co/"
classified_links, product_data_list = traverse_website(root_url)
for link in classified_links:
    print(link)

for product_data in product_data_list:
    print(product_data)
