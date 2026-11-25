import sqlite3

DB_NAME = "library.db"


def init_db(db_path=DB_NAME):
    with sqlite3.connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY, title TEXT NOT NULL, author TEXT,
            category TEXT, copies INTEGER DEFAULT 1)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS members (
            member_id TEXT PRIMARY KEY, name TEXT NOT NULL,
            phone TEXT, email TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS issued (
            member_id TEXT, book_id TEXT)''')


def add_book(bid, title, author, category, copies, db_path=DB_NAME):
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT INTO books VALUES (?,?,?,?,?)",
                         (bid, title, author, category, int(copies)))
        return True, f"Book '{title}' added successfully!"
    except sqlite3.IntegrityError:
        return False, f"Error: Book with ID '{bid}' already exists."


def add_member(mid, name, phone, email, db_path=DB_NAME):
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT INTO members VALUES (?,?,?,?)",
                         (mid, name, phone, email))
        return True, f"Member {name} registered successfully!"
    except sqlite3.IntegrityError:
        return False, f"Error: Member with ID '{mid}' already exists."


def get_all_books(db_path=DB_NAME):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT * FROM books").fetchall()


def search_book(bid, db_path=DB_NAME):
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            "SELECT * FROM books WHERE book_id = ?", (bid,)
        ).fetchone()


def issue_book(mid, bid, db_path=DB_NAME):
    with sqlite3.connect(db_path) as conn:
        if not conn.execute(
            "SELECT 1 FROM members WHERE member_id=?", (mid,)
        ).fetchone():
            return False, "Member not found."

        book = conn.execute(
            "SELECT copies FROM books WHERE book_id=?", (bid,)
        ).fetchone()

        if not book:
            return False, "Book not found."
        if book[0] <= 0:
            return False, "No copies available."

        conn.execute(
            "UPDATE books SET copies = copies - 1 WHERE book_id=?", (bid,)
        )
        conn.execute("INSERT INTO issued VALUES (?,?)", (mid, bid))
        return True, "Book issued successfully."


def return_book(mid, bid, db_path=DB_NAME):
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM issued WHERE rowid = (SELECT rowid FROM issued "
            "WHERE member_id=? AND book_id=? LIMIT 1)", (mid, bid)
        )
        if cur.rowcount == 0:
            return False, "No such issue record."

        conn.execute(
            "UPDATE books SET copies = copies + 1 WHERE book_id=?", (bid,)
        )
        return True, "Book returned successfully."


def delete_book(bid, db_path=DB_NAME):
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("DELETE FROM books WHERE book_id = ?", (bid,))
        return (True, "Deleted successfully.") if cur.rowcount > 0 else (False, "Not found.")


def main():
    init_db()
    while True:
        print("=" * 45)
        print("      LIBRARY MANAGEMENT SYSTEM")
        print("=" * 45)
        print("1. Add Book 2. View Books 3. Add Member")
        print("4. Issue Book 5. Return Book 6. Exit")

        ch = input("Enter choice (1-6): ")

        if ch == "1":
            print(add_book(
                input("ID: "), input("Title: "), input("Author: "),
                input("Category: "), input("Copies: ")
            )[1])

        elif ch == "2":
            print("ID\tTitle\t\tAuthor\t\tCopies")
            for b in get_all_books():
                print(f"{b[0]}\t{b[1]}\t{b[2]}\t{b[4]}")

        elif ch == "3":
            print(add_member(
                input("ID: "), input("Name: "), input("Phone: "),
                input("Email: ")
            )[1])

        elif ch == "4":
            print(issue_book(
                input("Member ID: "), input("Book ID: ")
            )[1])

        elif ch == "5":
            print(return_book(
                input("Member ID: "), input("Book ID: ")
            )[1])

        elif ch == "6":
            break


if __name__ == "__main__":
    main()