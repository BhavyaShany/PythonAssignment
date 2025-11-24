
## `library_manager/book.py`
#Book class: represents a single book in the library.
from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    isbn: str
    status: str = "available"  # 'available' or 'issued'

    def __post_init__(self):
        # normalize small things
        self.title = self.title.strip()
        self.author = self.author.strip()
        self.isbn = self.isbn.strip()
        if self.status not in ("available", "issued"):
            self.status = "available"

    def __str__(self) -> str:
        return f"{self.title} — {self.author} (ISBN: {self.isbn}) [{self.status}]"

    def to_dict(self) -> dict:
        return {"title": self.title, "author": self.author, "isbn": self.isbn, "status": self.status}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data.get("title", "").strip(),
            author=data.get("author", "").strip(),
            isbn=data.get("isbn", "").strip(),
            status=data.get("status", "available").strip(),
        )

    def is_available(self) -> bool:
        return self.status == "available"

    def issue(self) -> bool:
        if self.is_available():
            self.status = "issued"
            return True
        return False

    def return_book(self) -> bool:
        if not self.is_available():
            self.status = "available"
            return True
        return False

## `library_manager/inventory.py`
# LibraryInventory: maintains a list of Book objects and persists them to JSON."""
import json
import logging
from pathlib import Path
from typing import List, Optional

from .book import Book


logger = logging.getLogger(__name__)


class LibraryInventory:
    def __init__(self, catalog_path: Path):
        self.catalog_path = Path(catalog_path)
        self.books: List[Book] = []

    def load(self) -> None:
        try:
            if not self.catalog_path.exists():
                logger.info("Catalog file not found — creating empty catalog.")
                self.books = []
                return

            with self.catalog_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Catalog JSON root must be a list")

            self.books = [Book.from_dict(entry) for entry in data]
            logger.info(f"Loaded {len(self.books)} books from catalog.")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse catalog: {e}")
            # decide to start with an empty catalog rather than crash
            self.books = []
        except Exception as e:
            logger.error(f"Unhandled error while loading catalog: {e}")
            self.books = []

    def save(self) -> None:
        try:
            # ensure parent dir exists
            if not self.catalog_path.parent.exists():
                self.catalog_path.parent.mkdir(parents=True, exist_ok=True)

            with self.catalog_path.open("w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.books], f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.books)} books to catalog.")
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")

    def add_book(self, book: Book) -> None:
        # avoid duplicate ISBNs
        if self.search_by_isbn(book.isbn) is not None:
            logger.error(f"Attempted to add book with duplicate ISBN: {book.isbn}")
            raise ValueError("A book with this ISBN already exists.")
        self.books.append(book)
        logger.info(f"Added book: {book}")

    def search_by_title(self, title_query: str) -> List[Book]:
        q = title_query.strip().lower()
        return [b for b in self.books if q in b.title.lower()]

    def search_by_isbn(self, isbn: str) -> Optional[Book]:
        s = isbn.strip()
        for b in self.books:
            if b.isbn == s:
                return b
        return None

    def display_all(self) -> List[str]:
        return [str(b) for b in self.books]

    def issue_book_by_isbn(self, isbn: str) -> bool:
        book = self.search_by_isbn(isbn)
        if book is None:
            logger.error(f"Issue failed — ISBN not found: {isbn}")
            return False
        result = book.issue()
        if result:
            logger.info(f"Issued book: {isbn}")
        else:
            logger.info(f"Book already issued: {isbn}")
        return result

    def return_book_by_isbn(self, isbn: str) -> bool:
        book = self.search_by_isbn(isbn)
        if book is None:
            logger.error(f"Return failed — ISBN not found: {isbn}")
            return False
        result = book.return_book()
        if result:
            logger.info(f"Returned book: {isbn}")
        else:
            logger.info(f"Book already available: {isbn}")
        return result

# Simple menu-driven CLI for the library inventory.
import logging
from pathlib import Path

from library_manager.inventory import LibraryInventory
from library_manager.book import Book


LOG_FILE = Path("library.log")
CATALOG = Path("catalog.json")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ]
    )


def prompt_non_empty(prompt_text: str) -> str:
    while True:
        val = input(prompt_text).strip()
        if val:
            return val
        print("Input cannot be empty. Please try again.")


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    inventory = LibraryInventory(CATALOG)
    try:
        inventory.load()
    except Exception as e:
        logger.error(f"Failed to load inventory: {e}")

    try:
        while True:
            print("\n=== Library Inventory Manager ===")
            print("1. Add Book")
            print("2. Issue Book")
            print("3. Return Book")
            print("4. View All Books")
            print("5. Search")
            print("6. Exit")

            choice = input("Enter choice (1-6): ").strip()
            if choice == "1":
                title = prompt_non_empty("Title: ")
                author = prompt_non_empty("Author: ")
                isbn = prompt_non_empty("ISBN: ")
                try:
                    book = Book(title=title, author=author, isbn=isbn)
                    inventory.add_book(book)
                    inventory.save()
                    print("Book added successfully.")
                except ValueError as ve:
                    print(f"Error: {ve}")

            elif choice == "2":
                isbn = prompt_non_empty("ISBN to issue: ")
                success = inventory.issue_book_by_isbn(isbn)
                inventory.save()
                print("Book issued." if success else "Issue failed (not found or already issued).")

            elif choice == "3":
                isbn = prompt_non_empty("ISBN to return: ")
                success = inventory.return_book_by_isbn(isbn)
                inventory.save()
                print("Book returned." if success else "Return failed (not found or already available).")

            elif choice == "4":
                books = inventory.display_all()
                if not books:
                    print("No books in catalog.")
                else:
                    print("\nCatalog:")
                    for line in books:
                        print(line)

            elif choice == "5":
                print("Search by:\n 1) Title  2) ISBN")
                sub = input("Choose 1 or 2: ").strip()
                if sub == "1":
                    q = prompt_non_empty("Title query: ")
                    results = inventory.search_by_title(q)
                    if not results:
                        print("No matches found.")
                    else:
                        for b in results:
                            print(b)
                elif sub == "2":
                    q = prompt_non_empty("ISBN: ")
                    result = inventory.search_by_isbn(q)
                    if result:
                        print(result)
                    else:
                        print("No book with that ISBN.")
                else:
                    print("Invalid selection.")

            elif choice == "6":
                print("Exiting — saving catalog.")
                break
            else:
                print("Invalid choice. Choose 1-6.")

    except KeyboardInterrupt:
        print("\nInterrupted by user — exiting.")
    finally:
        try:
            inventory.save()
        except Exception as e:
            logger.error(f"Failed to save on exit: {e}")


if __name__ == "__main__":
    main()

