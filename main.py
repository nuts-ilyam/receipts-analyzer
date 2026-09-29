from fastapi import FastAPI, status
from starlette.responses import JSONResponse
from config import engine, settings
from db.models import Base
from imap.client import EmailClient
from utils import run_email_processing

# 1. Создаем экземпляр приложения
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/receipts/imap_sync",
          status_code=status.HTTP_200_OK,
          summary="Start sync process with imap")
def sync_imap_receipts():
    email_client = EmailClient(
        host=settings.mail.imap_host,
        username=settings.mail.imap_user,
        password=settings.mail.imap_password,
        folder=settings.mail.imap_folder,
    )
    messages = email_client.get_unread_messages()

    num_proc_mes = run_email_processing(messages)
    return JSONResponse(
        status_code=200,
        content={"message": f"Sync successfully finished. {num_proc_mes} processed. "},
    )


Base.metadata.create_all(engine)


