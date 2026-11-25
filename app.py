
import sqlite3
from contextlib import contextmanager

DB_NAME = "library.db"


@contextmanager
def db_connection(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path=DB_NAME):
    with db_connection(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            category TEXT,
            copies INTEGER DEFAULT 1
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS members (
            member_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS issued (
            member_id TEXT,
            book_id TEXT
        )''')


def add_book(bid, title, author, category, copies, db_path=DB_NAME):
    try:
        with db_connection(db_path) as conn:
            conn.execute(
                "INSERT INTO books VALUES (?,?,?,?,?)",
                (bid, title, author, category, int(copies))
            )
        return True, f"Book '{title}' added successfully!"
    except sqlite3.IntegrityError:
        return False, f"Error: Book with ID '{bid}' already exists."


def add_member(mid, name, phone, email, db_path=DB_NAME):
    try:
        with db_connection(db_path) as conn:
            conn.execute(
                "INSERT INTO members VALUES (?,?,?,?)",
                (mid, name, phone, email)
            )
        return True, f"Member {name} registered successfully!"
    except sqlite3.IntegrityError:
        return False, f"Error: Member with ID '{mid}' already exists."


def get_all_books(db_path=DB_NAME):
    with db_connection(db_path) as conn:
        return conn.execute("SELECT * FROM books").fetchall()


def search_book(bid, db_path=DB_NAME):
    with db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM books WHERE book_id = ?", (bid,)
        ).fetchone()


def issue_book(mid, bid, db_path=DB_NAME):
    with db_connection(db_path) as conn:
        member = conn.execute(
            "SELECT 1 FROM members WHERE member_id=?", (mid,)
        ).fetchone()

        if not member:
            return False, "Member not found."

        book = conn.execute(
            "SELECT copies FROM books WHERE book_id=?", (bid,)
        ).fetchone()

        if not book:
            return False, "Book not found."

        if book[0] <= 0:
            return False, "No copies available."

        conn.execute(
            "UPDATE books SET copies = copies - 1 WHERE book_id=?",
            (bid,)
        )

        conn.execute(
            "INSERT INTO issued VALUES (?,?)", (mid, bid)
        )

        return True, "Book issued successfully."


def return_book(mid, bid, db_path=DB_NAME):
    with db_connection(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM issued WHERE rowid = "
            "(SELECT rowid FROM issued "
            "WHERE member_id=? AND book_id=? LIMIT 1)",
            (mid, bid)
        )

        if cur.rowcount == 0:
            return False, "No such issue record."

        conn.execute(
            "UPDATE books SET copies = copies + 1 WHERE book_id=?",
            (bid,)
        )

        return True, "Book returned successfully."


def delete_book(bid, db_path=DB_NAME):
    with db_connection(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM books WHERE book_id = ?", (bid,)
        )

        if cur.rowcount > 0:
            return True, "Deleted successfully."

        return False, "Not found."


def main():
    init_db()

    while True:
        print("\n" + "=" * 45)
        print("      LIBRARY MANAGEMENT SYSTEM")
        print("=" * 45)
        print("1. Add Book")
        print("2. View Books")
        print("3. Add Member")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. Search Book")
        print("7. Delete Book")
        print("8. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            bid = input("Enter Book ID: ")
            title = input("Enter Title: ")
            author = input("Enter Author: ")
            category = input("Enter Category: ")
            copies = input("Enter Number of Copies: ")

            try:
                ok, message = add_book(
                    bid, title, author, category, copies
                )
                print(message)
            except ValueError:
                print("Please enter a valid number of copies.")

        elif choice == "2":
            books = get_all_books()

            if not books:
                print("No books available.")
            else:
                print("\nBook ID | Title | Author | Category | Copies")
                for book in books:
                    print(" | ".join(map(str, book)))

        elif choice == "3":
            mid = input("Enter Member ID: ")
            name = input("Enter Member Name: ")
            phone = input("Enter Phone: ")
            email = input("Enter Email: ")

            ok, message = add_member(mid, name, phone, email)
            print(message)

        elif choice == "4":
            mid = input("Enter Member ID: ")
            bid = input("Enter Book ID: ")

            ok, message = issue_book(mid, bid)
            print(message)

        elif choice == "5":
            mid = input("Enter Member ID: ")
            bid = input("Enter Book ID: ")

            ok, message = return_book(mid, bid)
            print(message)

        elif choice == "6":
            bid = input("Enter Book ID to search: ")
            book = search_book(bid)

            if book:
                print("Book Details:", book)
            else:
                print("Book not found.")

        elif choice == "7":
            bid = input("Enter Book ID to delete: ")
            ok, message = delete_book(bid)
            print(message)

        elif choice == "8":
            print("Thank you for using Library Management System!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
