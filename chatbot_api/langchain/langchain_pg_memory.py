import json
from datetime import datetime
from langchain.schema import BaseChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, BaseMessage
from sqlalchemy.sql import text
from app import db
from ..utility import json_serializable, omit_data


class PostgresChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id

    @property
    def messages(self):
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT role, message FROM(
                    SELECT role, message, created_at FROM public.chat_history
                    WHERE session_id = :session_id
                    ORDER BY created_at DESC
                    LIMIT 10
                )
                AS recent_rows ORDER BY created_at ASC
            """), {"session_id": self.session_id})

            rows = result.fetchall()
            messages = []
            for role, message in rows:
                if role == "Human":
                    messages.append(HumanMessage(content=message))
                elif role == "AI":
                    messages.append(AIMessage(content=omit_data(json.loads(message))))
            return messages
        
    def get_all_messages(self, omit=True, limit=10):
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT role, message FROM(
                    SELECT role, message, created_at FROM public.chat_history
                    WHERE session_id = :session_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                )
                AS recent_rows ORDER BY created_at ASC
            """), {"session_id": self.session_id, "limit": limit})

            rows = result.fetchall()
            messages = []
            for role, message in rows:
                if role == "Human":
                    messages.append(HumanMessage(content=message))
                elif role == "AI":
                    messages.append(AIMessage(content=omit_data(json.loads(message)) if omit else json.loads(message)))
            return messages

    def add_message(self, message: BaseMessage):
        try:
            role = "Human" if isinstance(message, HumanMessage) else "AI"
            content = message.content
            # Dump content to JSON if it's an AI message with structured response
            if role == "AI" and isinstance(content, (dict, list)):
                content = json.dumps(content, default=json_serializable)

            chat_history = {
                "session_id": self.session_id,
                "role": role,
                "message": content,
                "created_at": datetime.now()
            }

            with db.engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO public.chat_history (session_id, role, message, created_at)
                    VALUES (:session_id, :role, :message, :created_at)
                """), chat_history)
        except Exception as e:
            print(f"Error in saving chat history: {e}")

    def clear(self):
        with db.engine.begin() as conn:
            conn.execute(text("DELETE FROM chat_history WHERE session_id = :session_id"),
                         {"session_id": self.session_id})
