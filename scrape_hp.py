import requests
from bs4 import BeautifulSoup
import time
import json
import os
from functools import wraps
import shutil

# TODO: EVENTS, SOURCES

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\n{'=' * 100}")
        print(f"Function '{func.__name__}' took {elapsed_time:.2f} seconds to complete")
        print(f"{'=' * 100}\n")
        return result
    return wrapper

class Scraper:
    def __init__(self, batch_size=20, store_callback=None, scraped_urls_file="scraped_urls.json"):
        self.base_url = "https://www.hp-lexicon.org"
        self.documents_scraped = 0
        self.batch_size = batch_size
        self.store_callback = store_callback
        self.alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.scraped_urls = set()  # Track scraped URLs in memory
        self.scraped_urls_file = scraped_urls_file
        self._load_scraped_urls()  # Load previously scraped URLs
    
    def increment_documents_scraped(self):
        """Increments the number of documents scraped and calls the store callback if the batch size is reached."""
        self.documents_scraped += 1
        
        if self.documents_scraped % self.batch_size == 0:
            self.store_callback()

    def get_documents_scraped(self):
        """Returns the number of documents scraped."""
        return self.documents_scraped
    
    def _load_scraped_urls(self):
        """Load previously scraped URLs from file if it exists."""
        if os.path.exists(self.scraped_urls_file):
            try:
                with open(self.scraped_urls_file, 'r') as f:
                    url_list = json.load(f)
                    self.scraped_urls = set(url_list)
                    print(f"Loaded {len(self.scraped_urls)} previously scraped URLs")
            except Exception as e:
                print(f"Could not load scraped URLs: {e}")
                self.scraped_urls = set()
        else:
            print("No previous scraping history found, starting fresh")
    
    def _save_scraped_urls(self):
        """Save scraped URLs to file for persistence."""
        try:
            with open(self.scraped_urls_file, 'w') as f:
                json.dump(list(self.scraped_urls), f, indent=2)
        except Exception as e:
            print(f"Could not save scraped URLs: {e}")
    
    def is_url_scraped(self, url):
        """Check if a URL has already been scraped."""
        return url in self.scraped_urls
    
    def mark_url_as_scraped(self, url):
        """Mark a URL as scraped and periodically save to disk."""
        self.scraped_urls.add(url)
        # Save to disk periodically (every 10 URLs)
        if len(self.scraped_urls) % 10 == 0:
            self._save_scraped_urls()
    
    def reset_scraped_urls(self):
        """Reset the scraped URLs tracker (use with caution!)."""
        self.scraped_urls = set()
        if os.path.exists(self.scraped_urls_file):
            os.remove(self.scraped_urls_file)
        print("Scraped URLs tracker has been reset")

    def scrape_raw_text(self, url, is_article=False, is_novel=False):
        """Scrapes all <p> and <li> elements in order of appearance after the navbar. If is_article is True, it scrapes the article opening paragraph. If is_novel is True, it scrapes links included in the chapter page."""
        # Check if URL has already been scraped
        if self.is_url_scraped(url):
            print(f"Skipping already scraped URL: {url}")
            return
        
        tries = 0
        while True:
            try:
                character_page = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(character_page.text, "html.parser")
                text_parts = []
                if is_article:
                    try:
                        opening = soup.select_one(".ArticleGambit_gambit__iDGnv.ArticleGambit_darkTheme__E0VQv.ArticleGambit_default__t_9Q_")
                        text_parts.append(opening.get_text())
                    except Exception as e:
                        print(f"No article opening found for {url}")
                
                # try to get h1 title
                try:
                    h1_title = soup.find('h1')
                    if h1_title:
                        text_parts.append(h1_title.get_text())
                except Exception as e:
                    print(f"No h1 title found for {url}")

                # get all paragraphs and lists in order of appearance
                section = soup.select_one('html > body > article > section')
                if not section:
                    print(f"No section found for {url}")
                    break
                elements = section.find_all(['p', 'li'])
                if is_novel:
                    links = section.find_all("a")
                    for link in links:
                        link_url = link.get("href")
                        if not link_url:
                            continue
                        print("Scraping link within chapter: ", link_url)
                        # only scrape links in current chapter
                        if "hapter" not in link_url and "attachment_id" not in link_url:
                            self.scrape_raw_text(link_url, is_novel=False)

                # try to get fact box content if it exists
                try:
                    fact_box = section.find('div', class_='fact_box')
                    if fact_box:
                        fact_box_text = fact_box.get_text()
                        text_parts.append(fact_box_text)
                except Exception as e:
                    pass  # ignore if no fact box found

                # get all paragraphs and lists in order of appearance
                for element in elements:
                    if element.name == 'p':
                        text_parts.append(element.get_text())
                    else:  # element is a ul
                        list_items = element.find_all('li')
                        for li in list_items:
                            text_parts.append(li.get_text())

                text = "\n".join(text_parts)

                # cut off text after "Tags" or "Editors" appears
                # find last occurrence of Tags/Editor to avoid cutting off content that happens to contain those words
                if "Tags" in text:
                    text = text.rsplit("Tags", 1)[0]
                if "Editor" in text:
                    text = text.rsplit("Editor", 1)[0]
                if "Copyright" in text:
                    text = text.rsplit("Copyright", 1)[0]

                filename = '_'.join(url.split('/')[-2:])
                with open(f"hp_data/{filename}.txt", "w") as f:
                    f.write(text)
                self.increment_documents_scraped()
                self.mark_url_as_scraped(url)  # Mark URL as scraped
                break
            except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                tries += 1
                if tries > 2:
                    break
                print(f"Connection error for {url}: {e}. Retrying in 10 seconds...")
                time.sleep(10)
            except Exception as e:
                break
    
    def scrape_alphabetical_catalog(self, heading, wizarding_world=False):
        """Scrapes alphabetical catalog of items. If wizarding_world is True, it only scrapes the last item."""
        if not heading:
            print("No heading found for scrape_alphabetical_catalog")
            return
        ul_sibling = heading.find_next_sibling("ul")
        if not ul_sibling:
            print(f"No ul sibling found for heading: {heading.get_text()}")
            return
        categories = ul_sibling.find_all("a")
        if wizarding_world:
            categories = categories[4:]
        for cat in categories:
            print("=" * 100)
            print(f"Retrieving category: {cat.get_text()}")
            print("=" * 100)
            cat_url = cat.get("href")
            if not cat_url:
                print(f"No href found for category: {cat.get_text()}")
                continue
            # go through each letter in catalog
            for letter in self.alphabet:
                while True:
                    try:
                        print("Retrieving letter: ", letter)
                        cur_cat_url = f"{cat_url}?letter={letter}"
                        cur_cat_page = requests.get(cur_cat_url, headers=self.headers)
                        letter_soup = BeautifulSoup(cur_cat_page.text, "html.parser")
                        middle_column = letter_soup.find_all("div", class_="col-md-12")[1]
                        cur_cat_items = middle_column.find_all("article")
                        for item in cur_cat_items:
                            link_elem = item.find("link")
                            if not link_elem:
                                continue
                            item_url = link_elem.get("href")
                            if not item_url:
                                continue
                            self.scrape_raw_text(item_url)
                            print("Finished scraping category: ", item_url)
                        break
                    except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                        print(f"Connection error retrieving letter {letter}: {e}. Retrying in 10 seconds...")
                        time.sleep(10)
                    except Exception as e:
                        break
    
    def scrape_quotes(self, url):
        """Scrapes a designated quote page."""
        # Check if URL has already been scraped
        if self.is_url_scraped(url):
            print(f"Skipping already scraped URL: {url}")
            return
        
        while True:
            try:
                quote_page = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(quote_page.text, "html.parser")
                quotes_list = soup.find_all("li")
                print(len(quotes_list))
                text = ""
                for quote in quotes_list:
                    text += quote.get_text() + "\n"
                filename = url.split('/')[-1]
                with open(f"hp_data/{filename}.txt", "w") as f:
                    f.write(text)
                self.mark_url_as_scraped(url)  # Mark URL as scraped
                break
            except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                print(f"Connection error for {url}: {e}. Retrying in 10 seconds...")
                time.sleep(10)
            except Exception as e:
                break

    # THIS DOES NOT RETRIEVE TIMELINES
    @timing_decorator
    def retrieve_characters(self):
        """Retrieves all characters from the characters page."""
        print("Retrieving characters...")
        url = "https://www.hp-lexicon.org/characters/"
        while True:
            try:
                characters_page = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(characters_page.text, "html.parser")
                break
            except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                print(f"Connection error retrieving characters page: {e}. Retrying in 10 seconds...")
                time.sleep(10)
        
        group_names = ["Notable Characters", "Families", "Groups and Related Resources"]

        for i, group_name in enumerate(group_names):
            heading = soup.find("h2", string=group_name)
            if not heading:
                print(f"No heading found for group: {group_name}")
                continue
            print("=" * 100)
            print("Retrieving group: ", group_name)
            print("=" * 100)
            group = heading.find_next_sibling("ul")
            if not group:
                print(f"No ul sibling found for group: {group_name}")
                continue
            for character in group.find_all("a"):
                char_url = character.get("href")
                if not char_url:
                    continue
                self.scrape_raw_text(char_url)
                print(f"Scraped character: {char_url}")

    @timing_decorator
    def retrieve_places(self):
        """Retrieves all places from the places page."""
        print("Retrieving places...")
        url = "https://www.hp-lexicon.org/places/"
        while True:
            try:
                places_page = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(places_page.text, "html.parser")
                break
            except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                print(f"Connection error retrieving places page: {e}. Retrying in 10 seconds...")
                time.sleep(10)
        
        group_names = ["Scotland", "London and Surrey", "The West Country", "Elsewhere in Britain", "Elsewhere in the World"]

        for i, group_name in enumerate(group_names):
            heading_tag = "h3"
            if i == 5:
                heading_tag = "h2"
            heading = soup.find(heading_tag, string=group_name)
            if not heading:
                print(f"No heading found for group: {group_name}")
                continue
            print("=" * 100)
            print("Retrieving group: ", group_name)
            print("=" * 100)
            group = heading.find_next_sibling("ul")
            if not group:
                print(f"No ul sibling found for group: {group_name}")
                continue
            for place in group.find_all("a"):
                place_url = place.get("href")
                if not place_url:
                    continue
                self.scrape_raw_text(place_url)
                print(f"Place: {place_url}")
        
        # types of places
        heading = soup.find("h2", string="Types of Places")
        self.scrape_alphabetical_catalog(heading)
    
    @timing_decorator
    def retrieve_magic(self):
        """Retrieves all magic from the magic page."""
        print("Retrieving magic...")
        url = "https://www.hp-lexicon.org/magic/"
        while True:
            try:
                magic_page = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(magic_page.text, "html.parser")
                break
            except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                print(f"Connection error retrieving magic page: {e}. Retrying in 10 seconds...")
                time.sleep(10)
        
        magic_groups_catalogs = ["Spells", "Potions", "Magical Items & Devices", "Magical and Mundane Plants"]
        for group_name in magic_groups_catalogs:
            if group_name != "Magical Items & Devices":
                heading = soup.find("h2", string=group_name)
            else:
                heading = soup.select_one("html > body > article > section > div > div > section > div > div:nth-of-type(1) > div:nth-of-type(1) > h2:nth-of-type(3)")
            self.scrape_alphabetical_catalog(heading)
        magic_groups = ["Miscellaneous Magic", "Fields of Magical Study", "Quotes from J.K. Rowling"]
        for group_name in magic_groups:
            if group_name == "Fields of Magical Study":
                heading = soup.select_one("#content > div > div > section > div > div:nth-of-type(1) > div:nth-of-type(1) > h2:nth-of-type(7)")
            else:
                heading = soup.find("h2", string=group_name)
            if not heading:
                print(f"No heading found for group: {group_name}")
                continue
            print("=" * 100)
            print("Retrieving group: ", group_name)
            print("=" * 100)
            group = heading.find_next_sibling("ul")
            if not group:
                print(f"No ul sibling found for group: {group_name}")
                continue
            for magic in group.find_all("a"):
                magic_url = magic.get("href")
                if not magic_url:
                    continue
                if (group_name != "Quotes from J.K. Rowling"):
                    self.scrape_raw_text(magic_url)
                else:
                    self.scrape_quotes(magic_url)
                print(f"Magic: {magic_url}")

    @timing_decorator
    def retrieve_things(self):
        """Retrieves all things from the things page."""
        url = "https://www.hp-lexicon.org/things/"
        while True:
            try:
                things_page = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(things_page.text, "html.parser")
                break
            except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                print(f"Connection error retrieving things page: {e}. Retrying in 10 seconds...")
                time.sleep(10)
        
        # scrape explore the wizarding world
        explore_wizarding_world = soup.find("h2", string="Explore the Wizarding World")
        self.scrape_alphabetical_catalog(explore_wizarding_world, wizarding_world=True)

        # raw text from each page
        if explore_wizarding_world:
            ww_list = explore_wizarding_world.find_next_sibling("ul")
            if ww_list:
                for i, item in enumerate(ww_list[:4].find_all("a")):
                    item_url = item.get("href")
                    if item_url:
                        self.scrape_raw_text(item_url)
        
        # scrape departments
        mom_url = "https://www.hp-lexicon.org/thing/ministry-of-magic/"
        mom_page = requests.get(mom_url, headers=self.headers)
        mom_soup = BeautifulSoup(mom_page.text, "html.parser")
        departments_list = mom_soup.select_one("html > body > article > section > div > div > section > div > div:nth-of-type(2) > div:nth-of-type(1) > ul")
        if departments_list:
            for department in departments_list.find_all("a"):
                department_url = department.get("href")
                if department_url:
                    self.scrape_raw_text(department_url)

        # scrape places and equipment, organizations
        quidditch_url = "https://www.hp-lexicon.org/thing/quidditch/"
        quidditch_page = requests.get(quidditch_url, headers=self.headers)
        quidditch_soup = BeautifulSoup(quidditch_page.text, "html.parser")
        places_and_equipment = quidditch_soup.find("h2", string="Quiddith places and equipment")
        if places_and_equipment:
            for p in places_and_equipment.find_next_siblings("p")[:10]:
                a_tag = p.find("a")
                if a_tag:
                    url = a_tag.get("href")
                    if url:
                        self.scrape_raw_text(url)
        organizations = quidditch_soup.find("h2", string="Other Quidditch organizations")
        if organizations:
            for p in organizations.find_next_siblings("p")[:4]:
                a_tag = p.find("a")
                if a_tag:
                    url = a_tag.get("href")
                    if url:
                        self.scrape_raw_text(url)

        # scrape daily prophet personnel
        dp_employees_url = "https://www.hp-lexicon.org/thing/daily-prophet/writers-employees-daily-prophet/"
        self.scrape_raw_text(dp_employees_url)
        dp_employees_page = requests.get(dp_employees_url, headers=self.headers)
        dp_employees_soup = BeautifulSoup(dp_employees_page.text, "html.parser")
        headline = dp_employees_soup.select_one("html > body > article > section > div > div > section > div > div:nth-of-type(1) > div:nth-of-type(1) > h2")
        if headline:
            for i, p in enumerate(headline.find_next_siblings("p")[:14]):
                if i == 5 or i == 9:
                    continue
                a_tags = p.find_all("a")
                if a_tags:
                    url = a_tags[0].get("href")
                    if url:
                        self.scrape_raw_text(url)
        
        # scrape daily prophet headlines and articles
        headlines_url = "https://www.hp-lexicon.org/thing/daily-prophet/headlines-articles-daily-prophet/"
        self.scrape_raw_text(headlines_url)
        headlines_page = requests.get(headlines_url, headers=self.headers)
        headlines_soup = BeautifulSoup(headlines_page.text, "html.parser")
        headlines = headlines_soup.find_all("p")
        for p in headlines:
            a_tag = p.find("a")
            if a_tag:
                url = a_tag.get("href")
                if url:
                    self.scrape_raw_text(url)

        # scrape Pottermore Hogwarts Express articles
        express_url = "https://www.hp-lexicon.org/thing/hogwarts-express/"
        express_page = requests.get(express_url, headers=self.headers)
        express_soup = BeautifulSoup(express_page.text, "html.parser")
        articles = express_soup.select_one("html > body > article > section > div > div > section > div > div:nth-of-type(3) > div:nth-of-type(2) > ul")
        if articles:
            for article in articles.find_all("a"):
                url = article.get("href")
                if url:
                    self.scrape_raw_text(url, is_article=True)

        # scrape rest of things
        css_selector = "html > body > article > section > div > div > section > div > div:nth-of-type(1) > div:nth-of-type(1) > p:nth-of-type({position})"
        positions = [3, 4, 5, 7, 8, 9, 10]
        for position in positions:
            heading = soup.select_one(css_selector.format(position=position))
            self.scrape_alphabetical_catalog(heading)

        # scrape quotes and essays
        quotes_heading = soup.find("h2", string="Quotes from Rowling")
        if quotes_heading:
            quotes = quotes_heading.find_next_sibling("ul")
            if quotes:
                for quote in quotes.find_all("a"):
                    quote_url = quote.get("href")
                    if quote_url:
                        self.scrape_quotes(quote_url)
        essays_heading = soup.find("h2", string="Essays")
        if essays_heading:
            essays = essays_heading.find_next_sibling("ul")
            if essays:
                for essay in essays.find_all("a"):
                    essay_url = essay.get("href")
                    if essay_url:
                        self.scrape_raw_text(essay_url)
            
    @timing_decorator
    def retrieve_creatures(self):
        """Retrieves all creatures from the creatures page."""
        url = "https://www.hp-lexicon.org/creatures-bestiary/"
        self.scrape_raw_text(url)
        creatures_page = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(creatures_page.text, "html.parser")
        sections = ["Well-Known Creatures", "Types of Creatures", "Characters who are Creatures", "Miscellaneous"]
        for section in sections:
            creatures = soup.find("h2", string=section)
            if not creatures:
                print(f"No heading found for section: {section}")
                continue
            creatures_list = creatures.find_next_sibling("ul")
            if not creatures_list:
                print(f"No ul sibling found for section: {section}")
                continue
            for creature in creatures_list.find_all("a"):
                creature_url = creature.get("href")
                if creature_url:
                    self.scrape_raw_text(creature_url)
        
        # scrape different dragon types
        dragon_types = ["romanian-longhorn", "antipodean-opaleye", "hebridean-black", "short-snout", "chinese_fireball", "ukrainian-ironbelly", "horntail", "peruvian-vipertooth", "catalonian-fireball", "portuguese-long-snout", "welsh-green", "norwegian-ridgeback"]
        for dragon_type in dragon_types:
            dragon_url = f"https://www.hp-lexicon.org/creature/reptiles-and-amphibians/dragon/{dragon_type}/"
            self.scrape_raw_text(dragon_url)
        
        # scrape different human-like creatures
        hlc_list = soup.select_one("html > body > article > section > div > div > section > div > div:nth-of-type(1) > div:nth-of-type(1) > ul")
        if hlc_list:
            for hlc in hlc_list.find_all("a"):
                hlc_url = hlc.get("href")
                if hlc_url:
                    self.scrape_raw_text(hlc_url)
    
    @timing_decorator
    def retrieve_novels(self):
        """Retrieves all novels from the novels page."""
        url = "https://www.hp-lexicon.org/source/the-harry-potter-novels/"
        # self.scrape_raw_text(url)
        novels_page = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(novels_page.text, "html.parser")
        temp = soup.select_one("html > body > article > section > div > div > section > div > div:nth-of-type(2) > div:nth-of-type(1) > hr:nth-of-type(1)")
        if not temp:
            print("No hr element found for novels")
            return
        books_list = temp.find_next_siblings("p")[:7]
        for i, book in enumerate(books_list):
            book_link = book.find("a")
            if not book_link:
                print(f"No link found for book {i}")
                continue
            print("Scraping book: ", book_link.get_text())
            url = book_link.get("href")
            if not url:
                continue
            book_page = requests.get(url, headers=self.headers)
            book_soup = BeautifulSoup(book_page.text, "html.parser")
            self.scrape_raw_text(url)
            chapters = book_soup.find_all("a", string=lambda text: text and "Chapter" in text and "-" in text )
            for chapter in chapters:
                chapter_url = chapter.get("href")
                if chapter_url:
                    self.scrape_raw_text(chapter_url, is_novel=True)
        
        # fantastic beasts and where to find them
        fb_url = "https://www.hp-lexicon.org/source/other-potter-books/fb/"
        print("Scraping fantastic beasts and where to find them...")
        self.scrape_raw_text(fb_url)

        # quidditch through the ages
        print("Scraping quidditch through the ages...")
        qa_url = "https://www.hp-lexicon.org/source/other-potter-books/qa/"
        self.scrape_raw_text(qa_url)
        qa_page = requests.get(qa_url, headers=self.headers)
        qa_soup = BeautifulSoup(qa_page.text, "html.parser")
        contents = qa_soup.find("h2", string="Contents")
        chapters = contents.find_next_siblings("p")[:10]
        for chapter in chapters:
            chapter_links = chapter.find_all("a")
            chapter_url = chapter_links[-1].get("href")
            if chapter_url:
                self.scrape_raw_text(chapter_url, is_novel=True)

    @timing_decorator
    def retrieve_all(self):
        """Retrieves all data from the website."""
        self.retrieve_characters()
        self.retrieve_places()
        self.retrieve_magic()
        self.retrieve_things()
        self.retrieve_creatures()
        # Save all scraped URLs at the end
        self._save_scraped_urls()
        print(f"Scraping complete! Total URLs scraped: {len(self.scraped_urls)}")

if __name__ == "__main__":
    try:
        # clear scraped_urls.json
        if os.path.exists("scraped_urls.json"):
            os.remove("scraped_urls.json")
            print("Cleared scraped_urls.json")
        # clear hp_data folder contents
        if os.path.exists("hp_data"):
            for file in os.listdir("hp_data"):
                os.remove(os.path.join("hp_data", file))
            print("Cleared hp_data folder contents")
        scraper = Scraper(batch_size=20, store_callback=lambda: print(f"Scraped {scraper.documents_scraped} documents"))
        scraper.retrieve_novels()
        # Save scraped URLs when done
        scraper._save_scraped_urls()
        print(f"Finished scraping {scraper.documents_scraped} documents")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Save scraped URLs even on error
        scraper._save_scraped_urls()