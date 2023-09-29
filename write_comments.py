import asyncio
import os
import random

import aiofiles
import httpx
from dotenv import load_dotenv
from pyrogram import Client

from database_manager import DBManager
from random_choise import random_choice

load_dotenv()


class CommentWriter:
    def __init__(self):
        self.client = Client(
            "account", api_id=int(os.getenv("API_ID")), api_hash=os.getenv("API_HASH")
        )
        self.started = False

    async def start_client(self):
        if not self.started:
            await self.client.start()
            self.started = True

    async def get_entity_id(self, url: str) -> int:
        """
        Get the entity ID from a given URL.

        Args:
            url (str): The URL to extract the entity ID from.

        Returns:
            int: The extracted entity ID.
        """
        chat_name = url.split("/")[-1]
        try:
            await self.start_client()
            chat_info = await self.client.get_chat(chat_name)
            return chat_info.id
        except Exception as ex:
            print(ex)

    @staticmethod
    def count_lines(filename) -> int:
        with open(filename, "r") as file:
            line_count = sum(1 for line in file)
        return line_count

    async def write_comments(self):
        db_manager = DBManager()
        message_to_send = db_manager.get_active_message_text()

        proxy_list = [
            "5.78.106.1:8080",
            "159.223.119.107:8080",
            "5.161.62.204:8080",
            "5.161.222.66:8080",
            "5.161.228.93:8080",
            "5.161.220.130:8080",
        ]

        max_messages_per_day = 8400
        max_chats_per_round = self.count_lines("channels_to_comment.txt")
        rounds_per_day = 4
        messages_sent = 0
        proxy_index = 0

        for current_round in range(1, rounds_per_day + 1):
            if messages_sent >= max_messages_per_day:
                break

            async with aiofiles.open("channels_to_comment.txt", "r") as chats:
                async for chat in chats:
                    if messages_sent >= max_messages_per_day:
                        break

                    proxy = proxy_list[proxy_index]
                    print(f"Working with proxy: {proxy}")

                    async with httpx.AsyncClient(
                            proxies=f"socks5://{proxy}"
                    ) as proxy_client:
                        try:
                            print(f"Commenting in chat : {chat}")

                            chat_id = await self.get_entity_id(chat)
                            comment_chat = None
                            comment_chat_found = False
                            history = self.client.get_chat_history(chat_id=chat_id)
                            async for message in history:
                                if comment_chat_found:
                                    break
                                try:
                                    replies = self.client.get_discussion_replies(chat_id=chat_id, message_id=message.id)
                                    async for reply in replies:
                                        try:
                                            comment_chat = reply.sender_chat.id
                                            comment_chat_found = True
                                            await self.client.send_message(chat_id=comment_chat, text=random_choice(message_to_send),
                                                                           reply_to_message_id=reply.id)
                                            break
                                        except Exception as e:
                                            print(e)
                                except Exception:
                                    continue

                            messages_sent += 1
                            print(
                                f"Messages sent: {messages_sent}/{max_messages_per_day}"
                            )

                            delay = random.uniform(2, 5)
                            await asyncio.sleep(delay)

                            if messages_sent % 5 == 0:
                                proxy_index = (proxy_index + 1) % len(proxy_list)
                                print("Changing proxy...")

                            if messages_sent % max_chats_per_round == 0:
                                delay = random.randint(7200, 10800)
                                print(
                                    f"Waiting for {delay} seconds before the next round."
                                )
                                await asyncio.sleep(delay)

                            if (
                                    messages_sent
                                    % (
                                    max_messages_per_day
                                    // rounds_per_day
                                    // max_chats_per_round
                            )
                                    == 0
                            ):
                                delay = random.randint(7200, 10800)
                                print(
                                    f"Waiting for {delay} seconds before the next round."
                                )
                                await asyncio.sleep(delay)
                        except httpx.RequestError:
                            print(
                                f"Error occurred while sending request through proxy: {proxy}"
                            )

    async def run(self):
        await self.write_comments()


if __name__ == "__main__":
    writer = CommentWriter()
    asyncio.run(writer.run())
