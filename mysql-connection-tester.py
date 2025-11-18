import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error, errorcode


# ------------------------
# Database Helpers
# ------------------------
def get_connection(
    host="localhost",
    user="root",
    password="[your password]",
    database="[your database name]",
):
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        return connection
    except Error as e:
        print(f"[ERROR] Could not connect: {e}")
        return None


def run_query(query, params=None):
    """
    Run a SQL query and return results as a list of dictionaries.

    Example:
        rows = run_query("SELECT * FROM expenses WHERE id=%s", (3,))
    """
    conn = get_connection()
    if conn is None:
        print("[ERROR] Query aborted: No database connection.")
        return []

    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, params or ())
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results


def test_connection_diagnostics(host, user, password, database):
    """
    Try to connect and return (ok: bool, diagnostics: str).
    Provides detailed diagnostics for GUI display.
    """
    lines = []
    conn = None

    lines.append("=== MySQL Connection Test ===")
    lines.append(f"Host: {host}")
    lines.append(f"User: {user}")
    lines.append(f"Database: {database}")
    lines.append("")

    try:
        lines.append("[INFO] Attempting to connect...")
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )

        if conn.is_connected():
            lines.append("[SUCCESS] Connected to MySQL server.")
            server_info = conn.get_server_info()
            lines.append(f"[INFO] Server version: {server_info}")

            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            lines.append(f"[INFO] Active database: {db_name}")

            cursor.execute("SHOW VARIABLES LIKE 'version_compile_os'")
            os_row = cursor.fetchone()
            if os_row:
                lines.append(f"[INFO] Server OS: {os_row[1]}")

            cursor.close()
            ok = True
        else:
            lines.append(
                "[FAIL] Connection object created but not marked as connected."
            )
            ok = False

    except Error as e:
        lines.append("[ERROR] Could not connect to MySQL.")
        lines.append(f"  - Error code: {e.errno}")
        lines.append(f"  - SQLState: {e.sqlstate}")
        lines.append(f"  - Message : {e.msg}")

        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            lines.append("")
            lines.append("Possible cause: Invalid username or password.")
            lines.append("Check:")
            lines.append("  - The 'user' and 'password' fields.")
            lines.append("  - That this user has permission on this host.")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            lines.append("")
            lines.append("Possible cause: Database does not exist.")
            lines.append("Check:")
            lines.append("  - Spelling of the 'database' name.")
            lines.append("  - That the DB has been created.")
        elif e.errno == errorcode.CR_CONN_HOST_ERROR:
            lines.append("")
            lines.append("Possible cause: MySQL server not reachable.")
            lines.append("Check:")
            lines.append("  - Is the MySQL service running?")
            lines.append("  - Is 'host' correct?")
            lines.append("  - Firewall or port (default 3306) issues?")
        else:
            lines.append("")
            lines.append("General tips:")
            lines.append("  - Verify MySQL is running.")
            lines.append("  - Confirm host/user/password/database.")
            lines.append("  - Test connection using a MySQL client.")
        ok = False

    except Exception as ex:
        lines.append("[UNEXPECTED ERROR]")
        lines.append(f"  - Type   : {type(ex).__name__}")
        lines.append(f"  - Details: {ex}")
        ok = False

    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            lines.append("")
            lines.append("[INFO] Connection closed cleanly.")

    diagnostics = "\n".join(lines)
    return ok, diagnostics


# ------------------------
# Tkinter GUI - Neon Cyberpunk
# ------------------------
class ConnectionTesterApp:
    """Tkinter GUI for testing MySQL connection with neon cyberpunk theme."""

    def __init__(self, root):
        self.root = root
        self.root.title("MySQL Connection Tester")

        # Neon-ish window size
        self.root.geometry("800x550")
        self.root.minsize(700, 450)

        # Colors for cyberpunk theme
        self.bg_main = "#050816"    # deep space
        self.bg_panel = "#0b1020"   # slightly lighter panel
        self.neon_cyan = "#00eaff"
        self.neon_pink = "#ff00ff"
        self.neon_green = "#39ff14"
        self.text_soft = "#a0aec0"

        self.host_var = tk.StringVar(value="localhost")
        self.user_var = tk.StringVar(value="root")
        self.password_var = tk.StringVar(value="root")
        self.database_var = tk.StringVar(value="expense_manager")

        self._apply_style()
        self._build_gui()

    def _apply_style(self):
        """Configure ttk styles to mimic a neon-cyberpunk terminal feel."""
        self.root.configure(bg=self.bg_main)

        style = ttk.Style()
        # Use 'clam' for better background control
        style.theme_use("clam")

        # Frames
        style.configure(
            "Neon.TFrame",
            background=self.bg_main,
        )
        style.configure(
            "Panel.TFrame",
            background=self.bg_panel,
        )

        # LabelFrames
        style.configure(
            "Neon.TLabelframe",
            background=self.bg_panel,
            foreground=self.neon_cyan,
            borderwidth=2,
            relief="solid",
        )
        style.configure(
            "Neon.TLabelframe.Label",
            background=self.bg_panel,
            foreground=self.neon_cyan,
            font=("Consolas", 11, "bold"),
        )

        # Labels
        style.configure(
            "Neon.TLabel",
            background=self.bg_panel,
            foreground=self.text_soft,
            font=("Consolas", 10),
        )

        style.configure(
            "Title.TLabel",
            background=self.bg_main,
            foreground=self.neon_pink,
            font=("Consolas", 16, "bold"),
        )

        style.configure(
            "Status.TLabel",
            background=self.bg_main,
            foreground=self.neon_cyan,
            font=("Consolas", 11, "bold"),
        )

        # Entries
        style.configure(
            "Neon.TEntry",
            fieldbackground="#060b1a",
            foreground=self.neon_cyan,
            insertcolor=self.neon_cyan,
            borderwidth=1,
        )

        # Buttons
        style.configure(
            "Neon.TButton",
            background="#111827",
            foreground=self.neon_cyan,
            borderwidth=1,
            focusthickness=3,
            focuscolor=self.neon_pink,
            font=("Consolas", 10, "bold"),
            padding=6,
        )
        style.map(
            "Neon.TButton",
            background=[("active", "#1f2937")],
            foreground=[("active", self.neon_green)],
        )

    def _build_gui(self):
        main_frame = ttk.Frame(self.root, padding=10, style="Neon.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title bar
        title_label = ttk.Label(
            main_frame,
            text="⫷ MySQL CONNECTION TESTER ⫸",
            style="Title.TLabel",
        )
        title_label.pack(pady=(0, 10))

        # Top: connection fields in a neon panel
        form_frame = ttk.LabelFrame(
            main_frame,
            text="Connection Settings",
            style="Neon.TLabelframe",
            padding=10,
        )
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Inner panel to give padding and a slight "frame" feel
        inner_form = ttk.Frame(form_frame, style="Panel.TFrame")
        inner_form.pack(fill=tk.X, expand=True)

        # Host
        ttk.Label(
            inner_form,
            text="Host:",
            style="Neon.TLabel",
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        host_entry = ttk.Entry(
            inner_form,
            textvariable=self.host_var,
            width=30,
            style="Neon.TEntry",
        )
        host_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # User
        ttk.Label(
            inner_form,
            text="User:",
            style="Neon.TLabel",
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        user_entry = ttk.Entry(
            inner_form,
            textvariable=self.user_var,
            width=30,
            style="Neon.TEntry",
        )
        user_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Password
        ttk.Label(
            inner_form,
            text="Password:",
            style="Neon.TLabel",
        ).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        password_entry = ttk.Entry(
            inner_form,
            textvariable=self.password_var,
            width=30,
            show="*",
            style="Neon.TEntry",
        )
        password_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Database
        ttk.Label(
            inner_form,
            text="Database:",
            style="Neon.TLabel",
        ).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        db_entry = ttk.Entry(
            inner_form,
            textvariable=self.database_var,
            width=30,
            style="Neon.TEntry",
        )
        db_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Button + status row
        button_frame = ttk.Frame(main_frame, style="Neon.TFrame")
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = ttk.Label(
            button_frame,
            text="Status: Not tested yet",
            style="Status.TLabel",
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        test_button = ttk.Button(
            button_frame,
            text="▶ TEST CONNECTION",
            style="Neon.TButton",
            command=self.on_test_connection,
        )
        test_button.pack(side=tk.RIGHT, padx=5)

        # Diagnostics area in a "terminal" window
        diag_frame = ttk.LabelFrame(
            main_frame,
            text="Diagnostics Console",
            style="Neon.TLabelframe",
            padding=5,
        )
        diag_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Text widget with neon terminal style
        self.diag_text = tk.Text(
            diag_frame,
            wrap=tk.NONE,
            bg="#050816",
            fg=self.neon_green,
            insertbackground=self.neon_green,  # cursor color
            relief=tk.FLAT,
            font=("Consolas", 10),
        )
        self.diag_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        y_scroll = ttk.Scrollbar(
            diag_frame,
            orient=tk.VERTICAL,
            command=self.diag_text.yview,
        )
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.diag_text.configure(yscrollcommand=y_scroll.set)

        x_scroll = ttk.Scrollbar(
            diag_frame,
            orient=tk.HORIZONTAL,
            command=self.diag_text.xview,
        )
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.diag_text.configure(xscrollcommand=x_scroll.set)

        self.set_diagnostics(
            ">> SYSTEM ONLINE...\n"
            ">> Click '▶ TEST CONNECTION' to run a diagnostic scan.\n"
        )

    def set_diagnostics(self, text):
        """Replace content of the diagnostics Text widget."""
        self.diag_text.configure(state=tk.NORMAL)
        self.diag_text.delete("1.0", tk.END)
        self.diag_text.insert(tk.END, text)
        self.diag_text.configure(state=tk.DISABLED)

    def on_test_connection(self):
        """Handle Test Connection button click."""
        host = self.host_var.get().strip()
        user = self.user_var.get().strip()
        password = self.password_var.get()
        database = self.database_var.get().strip()

        if not host or not user or not database:
            messagebox.showwarning(
                "Missing Fields",
                "Host, user, and database are required.",
            )
            return

        self.status_label.configure(
            text="Status: Running diagnostics...",
            foreground=self.neon_cyan,
        )
        self.root.update_idletasks()

        ok, diagnostics = test_connection_diagnostics(
            host=host,
            user=user,
            password=password,
            database=database,
        )

        self.set_diagnostics(diagnostics)

        if ok:
            self.status_label.configure(
                text="Status: Connection successful",
                foreground=self.neon_green,
            )
        else:
            self.status_label.configure(
                text="Status: Connection failed",
                foreground=self.neon_pink,
            )


# ------------------------
# Main Entry Point
# ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectionTesterApp(root)
    root.mainloop()


