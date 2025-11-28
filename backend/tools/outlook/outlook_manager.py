from collections import defaultdict
import logging
from datetime import datetime, timedelta
from typing import List
import win32com.client as win32
from pydantic import BaseModel, Field

class MessageFilter(BaseModel):

    sender_email: str = Field(default='')
    user_id: int = Field(default=0)
    sender_name: str = Field(default='')
    body: str = Field(default='')
    subject: str = Field(default='')
    received_at: datetime = Field(default=None, 
                                  description="Date and time when the email was received", 
                                  default_factory=datetime.now)
    attachments: List[str] = Field(default_factory=list,
                                  description="List of attachment file names")


class OutlookEmailManager:
    """
    A class to manage Outlook email operations such as drafting, sending, and filtering emails. It uses the win32com client to interact with Outlook.
    It has the following methods:
    - init_mail_item: Initializes a new mail item in Outlook.
    - push_to_outlook: Pushes a drafted email to Outlook as a new email draft.
    - execute_email_send: Sends the initialized email item.
    - filter_messages: Retrieves recent messages from a specific sender in Outlook based on various filters.
    """

    def __init__(self):

        self.outlook = win32.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        self.inbox = self.namespace.GetDefaultFolder(6)  # 6 = Inbox

    def init_mail_item(self):
        self.__main_mail_item = self.outlook.CreateItem(0)  # 0 = Mail item

    def push_to_outlook(self, subject: str, body: str, to: str = "", cc: str = "", bcc: str = "", send=False):
        """
        This module pushes the drafted email to Outlook as a new email draft.
        """

        try:
            self.init_mail_item()

            self.__main_mail_item.Subject = subject
            self.__main_mail_item.To = to
            self.__main_mail_item.CC = cc
            self.__main_mail_item.BCC = bcc
            self.__main_mail_item.BodyFormat = 2  # 2 = HTML format
            self.__main_mail_item.HTMLBody = body
            self.__main_mail_item.Display()  # opens the email draft window
        
        except Exception as e:
            logging.error(f"Error pushing email to Outlook: {e}")

    def execute_email_send(self):
        if self.__main_mail_item:
            self.__main_mail_item.Send()
            logging.info("Email sent successfully via Outlook.")
        else:
            logging.error("No email item initialized to send.")


    def filter_messages(
            self, 
            **kwargs
            ) -> List[MessageFilter]:
        """
        Get recent messages from a specific sender in Outlook based on various filters specified in kwargs.
        Supported kwargs:
        - sender_email: str
        - user_id: int
        - max_results: int
        - days_back: int
        - keywords: list of str
        """

        sender_email = kwargs.get("sender_email", "")
        user_id = kwargs.get("user_id", 0)
        max_results = kwargs.get("max_results", 50)
        days_back = kwargs.get("days_back", 180)
        keywords = kwargs.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [keywords]

        logging.info(f"Filtering messages with the following criteria: "
                     f"Sender Email: {sender_email}, User ID: {user_id}, "
                     f"Max Results: {max_results}, Days Back: {days_back}, "
                     f"Keywords: {keywords}")

        try:
            outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)  # 6 = Inbox
            messages = inbox.Items

            ref_date = datetime.now() - timedelta(days=days_back)

        except Exception as e:
            logging.error(f"Error accessing Outlook inbox: {e}")
            return
        
        DCT_MESSAGES = defaultdict(dict)
        if user_id:

            str_user_id = str(user_id).lower()
            for msg in messages:
                
                try:
                    python_dt = datetime.fromtimestamp(msg.ReceivedTime.timestamp())
                    if ((msg.SenderEmailAddress).lower().endswith(str_user_id) or str_user_id in str(
                        msg.SenderEmailAddress).lower()) and python_dt >= ref_date:

                         DCT_MESSAGES.setdefault(
                            f"{msg.SenderName}-{python_dt.strftime('%Y-%m-%d %H%M%S')}", {}).update(
                                MessageFilter(
                                    **{"subject": msg.Subject, "sender": msg.SenderName, 
                                       "received_at": python_dt, 
                                       "user_id": user_id, 
                                       "sender_name": msg.SenderName or "N/A", 
                                       "sender_email": msg.SenderEmailAddress, 
                                       "body": msg.Body,
                                       "attachments": [att.FileName for att in msg.Attachments] if msg.Attachments else []
                                    }))
                         
                except Exception:
                    pass

        elif sender_email:

            str_sender_email = sender_email.lower()
            DCT_MESSAGES = defaultdict(dict)
            for msg in messages:
                
                try:
                    python_dt = datetime.fromtimestamp(msg.ReceivedTime.timestamp())
                    if (str_sender_email in str(msg.SenderEmailAddress).lower()) and python_dt >= ref_date:

                        DCT_MESSAGES.setdefault(
                            f"{msg.SenderName}-{python_dt.strftime('%Y-%m-%d %H%M%S')}", {}).update(
                                MessageFilter(**{"subject": msg.Subject,
                                 "sender_name": msg.SenderName or "N/A", 
                                  "received_at": python_dt, 
                                  "user_id": user_id or 0, 
                                  "user_email": msg.SenderEmailAddress,
                                  "body": msg.Body or "N/A",
                                  "attachments": [att.FileName for att in msg.Attachments] if msg.Attachments else []
                                  }))

                except Exception:
                    pass
        
        if keywords:
            for kywrd in keywords:
                DCT_MESSAGES = {
                    k: v for k, v in DCT_MESSAGES.items()
                    if kywrd.lower() in v.subject.lower()
                    or kywrd.lower() in v.body.lower()
                }
        
        DCT_MESSAGES = sorted(
            [
                (k, v) for k, v in DCT_MESSAGES.items()
                if "received_at" in v and isinstance(v.received_at, datetime)
            ],
            key=lambda x: x[1]["received_at"],
            reverse=True
        )

        messages_count = len(DCT_MESSAGES)
        logging.info(f"Found {messages_count} messages from sender '{sender_email or user_id}' in the last {days_back} days.")

        with open("outlook_filtered_messages.log", "w", encoding="utf-8") as log_file:

            for dt_key, msgobj in DCT_MESSAGES[:max_results]:

                body_preview = msgobj.body
                #Clean up body from HTML tags for preview, and empty lines
                body_preview = ''.join(body_preview.splitlines()).strip()

                log_file.write(f"{dt_key}:\n-------\n{body_preview}\n")
                log_file.write("-" * 50 + "\n")


if __name__ == "__main__":
    OutlookEmailManager().filter_messages(user_id=3649533, max_results=20)