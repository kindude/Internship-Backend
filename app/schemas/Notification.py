from datetime import datetime
from typing import List

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id:int
    timestamp:datetime
    text:str
    status:str
    quiz_id:int


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]