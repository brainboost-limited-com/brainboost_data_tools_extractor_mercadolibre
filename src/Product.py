from bs4 import BeautifulSoup
from brainboost_data_source_requests_package.Request import Request



class Product:
    def __init__(self) -> None:
        pass

    @staticmethod
    def product_from(url=None, soup=None):
        if url:
            try:
                product_data_request = Request()
                response = product_data_request.get(page=url, data={})
                response.raise_for_status()  # Raise an HTTPError on bad status
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                print(f"Error fetching the URL: {e}")
                return None
        elif soup is None:
            print("No URL or BeautifulSoup object provided.")
            return None
        return Product.extract_all_info(soup)

    @staticmethod
    def extract_category_path(soup):
        nav_section = soup.find('nav', {'aria-label': ' '})
        if not nav_section:
            return {'category_names': [], 'category_links': []}  # Return empty lists if nav section is not found

        category_names = []
        category_links = []
        for li_tag in nav_section.find_all('li', class_='andes-breadcrumb__item'):
            link_tag = li_tag.find('a', class_='andes-breadcrumb__link')
            if link_tag and link_tag.get('href'):
                category_names.append(link_tag.text.strip())
                category_links.append(link_tag.get('href'))

        return {'category_names': category_names, 'category_links': category_links}

    @staticmethod
    def extract_product_info(soup):
        product_info = {}

        try:
            title_tag = soup.find('h1', class_='ui-pdp-title')
            product_info['Product Title'] = title_tag.text.strip() if title_tag else 'Product title not found'

            rating_tag = soup.find('span', class_='ui-pdp-review__rating')
            product_info['Stars'] = float(rating_tag.text.strip()) if rating_tag else 'Rating not found'

            price_tag = soup.find('span', class_='andes-money-amount__fraction')
            if price_tag:
                price_text = price_tag.text.strip()
                product_info['Price'] = float(price_text.replace('.', '').replace(',', '.'))
            else:
                product_info['Price'] = 'Price not found'

            amount_sold_tag = soup.find('span', class_='ui-pdp-subtitle')
            product_info['Amount Sold'] = amount_sold_tag.text.strip() if amount_sold_tag else 'Amount sold not found'

            badges = soup.find_all('div', class_='ui-pdp-promotions-pill-label__trigger')
            for badge in badges:
                if 'MÁS VENDIDO' in badge.text:
                    product_info['Best Seller'] = True
                if '1º en' in badge.text:
                    product_info['Category Badge'] = badge.text

            color_label = soup.find('p', id='picker-label-COLOR_SECONDARY_COLOR')
            product_info['Color'] = color_label.text.strip() if color_label else 'Color not found'

            seller_info = soup.find('span', class_='ui-pdp-seller__label-sold')
            if seller_info:
                seller_span = seller_info.find('span', class_='ui-pdp-color--BLUE')
                product_info['Seller'] = seller_span.text.strip() if seller_span else 'Seller information not found'
            else:
                product_info['Seller'] = 'Seller information not found'

            shipping_info = soup.find('p', class_='ui-pdp-media__title', text='Envío a nivel nacional')
            product_info['Shipping'] = shipping_info.text.strip() if shipping_info else 'Shipping information not found'

            returns_info = soup.find('p', class_='ui-pdp-media__title', text='Devolución gratis')
            product_info['Returns'] = returns_info.text.strip() if returns_info else 'Returns information not found'

            additional_info = soup.find('div', class_='ui-pdp-buybox__quantity')
            product_info['Additional Info'] = additional_info.text.strip() if additional_info else 'Additional information not found'

        except AttributeError as e:
            print(f"Error extracting product information: {e}")
            # Log the error and proceed with partial information

        return product_info

    @staticmethod
    def extract_payment_methods(soup):
        payment_methods = {}
        payment_section = soup.find('div', class_='ui-vip-payment_methods')
        if payment_section:
            payment_titles = payment_section.find_all('p', class_='ui-vip-payment_methods__title')
            payment_icons = payment_section.find_all('img', class_='ui-pdp-payment-icon')
            for title, icon in zip(payment_titles, payment_icons):
                payment_methods[title.text.strip()] = icon['src']
        return {'payment_methods': payment_methods}

    @staticmethod
    def extract_product_characteristics(soup):
        product_characteristics = {}
        highlighted_specs_section = soup.find('section', id='highlighted_specs_attrs')
        if highlighted_specs_section:
            tables = highlighted_specs_section.find_all('table', class_='andes-table')
            for table in tables:
                category_name = table.find('h3', class_='ui-vpp-striped-specs__header').text.strip()
                rows = table.find_all('tr', class_='andes-table__row ui-vpp-striped-specs__row')
                for row in rows:
                    key = row.find('th', class_='andes-table__header').text.strip()
                    value = row.find('td', class_='andes-table__column--value').text.strip()
                    product_characteristics[key] = value
        return {'product_characteristics': product_characteristics}

    @staticmethod
    def extract_product_description(soup):
        description_section = soup.find('div', {'id': 'description'})
        if description_section:
            description_content = description_section.find('p', {'class': 'ui-pdp-description__content'})
            if description_content:
                return {'product_description': description_content.get_text(separator='\n').strip()}
        return {'product_description': None}

    @staticmethod
    def extract_product_rating_info(soup):
        average_rating_elem = soup.find('p', {'class': 'ui-review-capability__rating__average'})
        average_rating = float(average_rating_elem.get_text().strip()) if average_rating_elem else None

        total_ratings_elem = soup.find('p', {'class': 'ui-review-capability__rating__label'})
        total_ratings = int(total_ratings_elem.get_text().split()[0]) if total_ratings_elem else None

        rating_distribution = {}
        rating_levels = soup.find_all('li', {'class': 'ui-review-capability-rating__level'})
        for level in rating_levels:
            star_level = int(level.find('span').get_text().strip())
            progress_bar = level.find('div', {'class': 'ui-review-capability-rating__level__progress-bar__fill-background'})
            if progress_bar:
                percentage_str = progress_bar['style']
                percentage = float(percentage_str.split(':')[1].strip('%'))
                num_people = int(percentage * total_ratings / 100)
                rating_distribution[star_level] = num_people

        return {
            'average_rating': average_rating,
            'total_ratings': total_ratings,
            'rating_distribution': rating_distribution
        }

    @staticmethod
    def extract_product_characteristics_ratings(soup):
        characteristic_ratings = {}
        rows = soup.find_all('tr', class_='ui-review-capability-categories__desktop--row')
        for row in rows:
            characteristic_name = row.find('td').get_text().strip()
            rating_stars = len(row.find_all('svg', class_='ui-review-capability-categories__rating__star'))
            rating_half_star = len(row.find_all('svg', class_='ui-review-capability-categories__rating__star--half'))
            total_rating = rating_stars + 0.5 * rating_half_star
            characteristic_ratings[characteristic_name] = total_rating
        return {'characteristic_ratings': characteristic_ratings}

    @staticmethod
    def extract_reviews_data(soup):
        reviews_data = []
        review_elements = soup.find_all('article', class_='ui-review-capability-comments__comment')
        for review in review_elements:
            rating_element = review.find('div', class_='ui-review-capability-comments__comment__rating')
            stars_filled = len(rating_element.find_all('svg', class_='ui-review-capability-comments__comment__rating__star'))
            stars_empty = len(rating_element.find_all('svg', class_='ui-review-capability-comments__comment__rating__star-empty'))
            rating = stars_filled + 0.5 * stars_empty

            date_element = review.find('span', class_='ui-review-capability-comments__comment__date')
            date = date_element.text.strip()

            review_text_element = review.find('p', class_='ui-review-capability-comments__comment__content')
            review_text = review_text_element.text.strip()

            image_elements = review.find_all('img', class_='ui-review-capability-carousel__img')
            image_links = [img['src'] for img in image_elements] if image_elements else []

            reviews_data.append({
                'rating': rating,
                'date': date,
                'review_text': review_text,
                'image_links': image_links
            })
        return {'reviews_data': reviews_data}

    @staticmethod
    def extract_all_info(soup):
        all_info = {
            'category_path': Product.extract_category_path(soup),
            'product_info': Product.extract_product_info(soup),
            'payment_methods': Product.extract_payment_methods(soup),
            'product_characteristics': Product.extract_product_characteristics(soup),
            'product_description': Product.extract_product_description(soup),
            'product_rating_info': Product.extract_product_rating_info(soup),
            'product_characteristics_ratings': Product.extract_product_characteristics_ratings(soup),
            'reviews_data': Product.extract_reviews_data(soup)
        }
        return all_info
