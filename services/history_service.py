from firebase_admin import firestore
from datetime import datetime
from models.models import WalletHistoryItem
from google.cloud.firestore_v1.base_query import FieldFilter

db = firestore.client()

class HistoryService:
    @staticmethod
    def add_wallet_history(wallet_history_item: WalletHistoryItem) -> dict:
        try:
            history_ref = db.collection("history", "wallets", "entries")
            doc_ref = history_ref.add({})
            generated_id = doc_ref[1].id
            wallet_history_item.id = generated_id
            history_ref.document(wallet_history_item.id).set(wallet_history_item.to_dict())
            return wallet_history_item.to_dict()
        except Exception as e:
            raise e
            raise RuntimeError(f"Failed to store wallet history: {str(e)}")


    @staticmethod
    def get_wallet_history(wallet_id: str) -> list:
        try:
            history_ref = db.collection("history", "wallets", "entries")
            query = history_ref.where(filter=FieldFilter("wallet_id", "==", wallet_id)).order_by("time", direction=firestore.Query.DESCENDING)
            history_docs = query.stream()
            return [doc.to_dict() for doc in history_docs]
        except Exception as e:
            raise RuntimeError(f"Failed to fetch wallet history: {str(e)}")
    
    def get_driver_financial_history(driver_id: str) -> list:
        try:
            history_ref = db.collection("history", "wallets", "entries")
            query = history_ref.where(filter=FieldFilter("shuttle.driver.id", "==", driver_id)).order_by("time", direction=firestore.Query.DESCENDING)
            history_docs = query.stream()
            return [doc.to_dict() for doc in history_docs]
        except Exception as e:
            raise e
            raise RuntimeError(f"Failed to fetch history: {str(e)}")
