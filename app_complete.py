import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import time

BASE_URL = "https://books.toscrape.com"

def get_categories():
    """Récupère toutes les catégories de livres sauf 'Books'"""
    response = requests.get(BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    categories = []
    for link in soup.find_all('a', href=True):
        if 'catalogue/category/books' in link['href']:
            category_name = link.get_text(strip=True)
            if category_name and category_name.lower() != "books":
                category_url = BASE_URL + '/' + link['href'].lstrip('/')
                categories.append((category_name, category_url))
    return categories

def get_book_details(book_url):
    """Récupère tous les détails d'un livre"""
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    product_table = soup.find('table', class_='table table-striped')
    rows = product_table.find_all('tr')
    
    return {
        'UPC': rows[0].find('td').text,
        'price_including_tax': rows[3].find('td').text,
        'price_excluding_tax': rows[2].find('td').text,
        'number_available': rows[5].find('td').text,
        'review_rating': soup.find('p', class_='star-rating')['class'][1],
        'product_description': soup.find('meta', attrs={'name': 'description'})['content'].strip(),
        'image_url': BASE_URL + '/' + soup.find('img')['src'].replace('../', '')
    }

def get_books_from_category(category_name, category_url):
    """Récupère tous les livres d'une catégorie"""
    books = []
    while category_url:
        try:
            response = requests.get(category_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for article in soup.find_all('article', class_='product_pod'):
                book_url = BASE_URL + '/catalogue/' + article.h3.a['href'].replace('../', '')
                book_details = get_book_details(book_url)
                
                books.append({
                    'category': category_name,
                    'product_page_url': book_url,
                    'title': article.h3.a['title'],
                    **book_details
                })
                time.sleep(0.2)  # Pause pour éviter de surcharger le serveur
            
            # Gestion de la pagination
            next_button = soup.select_one('li.next a')
            category_url = BASE_URL + '/catalogue/category/' + next_button['href'] if next_button else None
            
        except Exception as e:
            print(f"Erreur avec {category_url}: {e}")
            break
    
    return books

def save_to_csv(category_name, books):
    """Sauvegarde les livres dans un CSV par catégorie"""
    os.makedirs('CSV_par_categorie', exist_ok=True)
    filename = f"CSV_par_categorie/{category_name}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, 
                              fieldnames=[
                                  'category', 'product_page_url', 'UPC', 'title',
                                  'price_including_tax', 'price_excluding_tax',
                                  'number_available', 'review_rating',
                                  'product_description', 'image_url'
                              ],
                              delimiter=';',
                              quoting=csv.QUOTE_ALL )
        writer.writeheader()
        writer.writerows(books)
    
    print(f"{len(books)} livres sauvegardés dans {filename}")

def main():
    categories = get_categories()
    print(f"Début du scraping de {len(categories)} catégories...")
    
    for name, url in categories:
        print(f"\nTraitement de : {name}")
        books = get_books_from_category(name, url)
        save_to_csv(name, books)
    
    print("\nTerminé ! Tous les fichiers sont dans le dossier 'CSV_par_categorie'")

if __name__ == "__main__":
    main()
