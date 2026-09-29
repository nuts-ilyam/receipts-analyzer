from typing import List

from imap_tools import MailBox, AND, MailMessage


class EmailClient:
    def __init__(self,
                 host: str,
                 username: str,
                 password: str,
                 folder: str = "INBOX"):
        self.host = host
        self.username = username
        self.password = password
        self.folder = folder

    def get_unread_messages(self):

        with MailBox(self.host).login(
                    self.username,
                    self.password,
                    initial_folder=self.folder) as mailbox:
            messages = mailbox.fetch(
                AND(seen=False),
                mark_seen=False,
            )

            return list(messages)

    def get_messages_from(self, sender: str) -> List[MailMessage]:
        with MailBox(self.host).login(
                self.username,
                self.password,
                initial_folder=self.folder,
        ) as mailbox:
            messages = mailbox.fetch(
                AND(
                    seen=False,
                    from_=sender,
                ),
                mark_seen=False,
            )

            return list(messages)