import requests
from bs4 import BeautifulSoup
import csv
import os

URL = "https://books.toscrape.com"

def get_categories():
    
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    categories = []
    for link in soup.find_all('a', href=True):
        if 'catalogue/category/books' in link['href']:
            category_name = link.get_text(strip=True)
            if category_name and category_name.lower() != "books": 
                category_url = URL + '/' + link['href'].lstrip('/')
                categories.append((category_name, category_url))
    
    return categories

def get_books_from_category(category_url):
    
    books = []
    while category_url:
        response = requests.get(category_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for article in soup.find_all('article', class_='product_pod'):
            title = article.h3.a['title']
            book_url = article.h3.a['href']
            
            
            if book_url.startswith('../../../'):
                book_url = URL + '/catalogue/' + book_url[9:]
            elif book_url.startswith('../../'):
                book_url = URL + '/catalogue/' + book_url[6:]
            elif book_url.startswith('../'):
                book_url = URL + '/catalogue/' + book_url[3:]
            
            books.append({
                'title': title,
                'url': book_url
            })
        
        
        next_button = soup.select_one('li.next a')
        if next_button:
            next_url = next_button['href']
            if 'catalogue/category' in category_url:
                base_path = category_url.rsplit('/', 1)[0]
                category_url = base_path + '/' + next_url
            else:
                category_url = URL + '/catalogue/category/' + next_url
        else:
            category_url = None
    
    return books

def save_to_csv(data, filename):
    
    os.makedirs('Livre', exist_ok=True)
    filepath = os.path.join('Livre', filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Données sauvegardées dans {filepath}")

def main():
    categories = get_categories()
    print(f"{len(categories)} catégories trouvées")
    
    all_books = []
    
    
    for i, (category_name, category_url) in enumerate(categories, 1):
        print(f"\nTraitement de la catégorie {i}/{len(categories)}: {category_name}")
        books = get_books_from_category(category_url)
        all_books.extend(books)
        print(f"  {len(books)} livres trouvés")
    
    
    save_to_csv(all_books, 'all_books.csv')
    
    print(f"\nTotal: {len(all_books)} livres récupérés")

if __name__ == "__main__":
    main()