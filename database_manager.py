import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()


class DBManager:
    def __init__(self):
        self.connection = sqlite3.connect(os.getenv("DB_NAME"))
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS "messages" (
                    "id" INTEGER PRIMARY KEY,
                    "message" TEXT,
                    "active" BOOLEAN DEFAULT FALSE
                )
            """
        )

        self.connection.commit()

    def add_message(self, message: str) -> None:
        self.cursor.execute(
            """
            INSERT INTO "messages"
            (message) VALUES (?)
            """,
            (message,),
        )
        self.connection.commit()

    def get_all_messages(self) -> list[tuple[int, str, bool]]:
        all_messages = self.cursor.execute(
            """
            SELECT "id", "message", "active"
            FROM "messages"
            """
        ).fetchall()

        return all_messages

    def get_active_message(self) -> int:
        try:
            active_message = self.cursor.execute(
                """
                SELECT "id"
                FROM "messages"
                WHERE "active" = TRUE
                """
            ).fetchone()[0]
        except TypeError:
            return 0

        return active_message

    def get_active_message_text(self) -> str:
        try:
            active_message = self.cursor.execute(
                """
                SELECT "message"
                FROM "messages"
                WHERE "active" = TRUE
                """
            ).fetchone()[0]
        except TypeError:
            return "No active message"

        return active_message

    def set_active_message(self, message_pk: int) -> None:
        active_message = self.get_active_message()
        if not active_message:
            self.cursor.execute(
                """
                UPDATE "messages"
                SET "active" = TRUE
                WHERE "id" = ?
                """,
                (message_pk,)
            )

            self.connection.commit()
        else:
            self.cursor.execute(
                """
                UPDATE "messages"
                SET "active" = FALSE
                WHERE "id" = ?
                """,
                (active_message,),
            )

            self.connection.commit()

            self.cursor.execute(
                """
                UPDATE "messages"
                SET "active" = TRUE
                WHERE "id" = ?
                """,
                (message_pk,),
            )

            self.connection.commit()

    def get_message_text_by_pk(self, pk: int) -> str:

        message_text = self.cursor.execute(
            """
            SELECT "message"
            FROM "messages"
            WHERE id = ?
            """, (pk,)
        ).fetchone()[0]

        return message_text

    def delete_message_by_pk(self, pk: int) -> None:
        self.cursor.execute(
            """
            DELETE FROM "messages"
            WHERE "id" = ?
            """, (pk,)
        )

        self.connection.commit()


# --------- ⬇️ TEST ⬇️ ---------
if __name__ == "__main__":
    manager = DBManager()
    # manager.add_message("TEST 2 MESSAGE")
    # manager.set_active_message(2)
    # print(manager.get_all_messages())
    # print(manager.get_active_message())
    print(manager.get_message_text_by_pk(1))
