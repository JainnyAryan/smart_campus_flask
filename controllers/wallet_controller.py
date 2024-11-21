from flask import Blueprint, request, jsonify
from models.models import Wallet, WalletHistoryItem, Shuttle
from utils.decorators import protected_route
from utils.error_handler import handle_error
from firebase_admin import firestore
from datetime import datetime, timedelta, timezone
from services.history_service import HistoryService


wallet_bp = Blueprint('wallet_bp', __name__, url_prefix='/wallets')
db = firestore.client()

WALLET_FREQUENCY_SECONDS = 30

def get_fare_value():
    fare = db.collection('values').document('fare').get().get('value')
    return fare


@wallet_bp.route('/get-fare', methods=['GET'])
@protected_route
def get_fare():
    try:
        fare = get_fare_value()
        return jsonify({"fare": fare}), 200
    except Exception as e:
        handle_error(e)
        
@wallet_bp.route('/modify-fare', methods=['PUT'])
@protected_route
def modify_fare():
    data: dict = request.json
    if set(['new_value']) != set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400
    try:
        fare_value_ref = db.collection('values').document('fare')
        new_value = float(data['new_value'])
        fare_value_ref.update({'value': new_value})
        return jsonify({"message": "Fare updated successfully!"}), 200
    except Exception as e:
        handle_error(e)


@wallet_bp.route('/', methods=['GET'])
@protected_route
def get_all_wallets():
    try:
        wallets_ref = db.collection('wallets')
        docs = wallets_ref.stream()

        wallets = []
        for doc in docs:
            wallets.append(doc.to_dict())
        if not wallets:
            return jsonify({"message": "No wallets found"}), 404
        return jsonify({"wallets": wallets}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Create Wallet


@wallet_bp.route('/create', methods=['POST'])
def create_wallet():
    data: dict = request.json
    if not set(['user_id']) == set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400

    try:
        db_ref = db.collection('wallets')
        update_time, doc_ref = db_ref.add({})
        doc_id = doc_ref.id

        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        oldest_date = datetime(1970, 1, 1, tzinfo=ist_timezone)

        wallet = Wallet(
            id=doc_id,
            amount=0,
            lastUsed=oldest_date
        )

        db_ref.document(doc_id).set(wallet.to_dict())
        db.collection('users').document(data['user_id']).update(
            {"student.wallet_id": wallet.id})
        return jsonify(wallet.to_dict()), 201
    except Exception as e:
        return handle_error(e)

# Get Wallet


@wallet_bp.route('/<wallet_id>', methods=['GET'])
def get_wallet(wallet_id):
    try:
        wallet_ref = db.collection('wallets').document(wallet_id).get()
        if not wallet_ref.exists:
            return jsonify({"message": "Wallet not found"}), 404
        return jsonify( wallet_ref.to_dict()), 200
    except Exception as e:
        return handle_error(e)

# Update Wallet


@wallet_bp.route('/update-amount', methods=['PUT'])
def update_amount():
    data: dict = request.get_json()
    if not set(['id', 'trips', 'addition', 'shuttle']) == set(data.keys()):
        return jsonify({"error": "Invalid input data"}), 400
    if not data.get('addition') and data.get('shuttle') is None:
        return jsonify({"error": "Shuttle details not provided while deduction"}), 400

    wallet_id = data.get('id')
    trips = data.get('trips')
    amount_to_add = trips * get_fare_value()
    addition = data.get('addition')
    shuttle = data.get('shuttle')
    if not addition:
        amount_to_add = -amount_to_add

    try:
        wallet_ref = db.collection('wallets').document(wallet_id)
        wallet = wallet_ref.get()
        if wallet.exists:
            wallet_data = wallet.to_dict()
            current_amount = wallet_data.get('amount', 0)
            if not addition and current_amount < get_fare_value():
                return jsonify({"error": "Not enough amount in wallet!"}), 403
            last_used = wallet_data.get('lastUsed')

            if last_used:
                IST = timezone(timedelta(hours=5, minutes=30))
                last_used_dt = datetime.fromisoformat(last_used)
                time_diff = datetime.now(IST) - last_used_dt
                if not addition and time_diff.total_seconds() < WALLET_FREQUENCY_SECONDS:
                    return jsonify({"error": f"Try again in {WALLET_FREQUENCY_SECONDS - time_diff.seconds} seconds!"}), 403

            new_amount = current_amount + amount_to_add
            wallet_ref.update({
                'amount': new_amount,
                'lastUsed': datetime.now(IST).isoformat(),
            })
            updated_wallet = Wallet(wallet_id, new_amount)
            HistoryService.add_wallet_history(
                wallet_history_item=WalletHistoryItem(
                    addition=addition,
                    amount=abs(amount_to_add),
                    time=datetime.now(IST),
                    wallet_id=wallet_id,
                    shuttle=Shuttle.from_dict(
                        shuttle) if shuttle is not None else None
                )
            )
            return jsonify(updated_wallet.to_dict()), 200
        else:
            return jsonify({"error": "Wallet not found"}), 404

    except Exception as e:
        raise e
        return jsonify({"error": str(e)}), 500


@wallet_bp.route('/<wallet_id>', methods=['DELETE'])
def delete_wallet(wallet_id):
    try:
        wallet_ref = db.collection('wallets').document(wallet_id)
        if not wallet_ref.get().exists:
            return jsonify({"message": "Wallet not found"}), 404

        wallet_ref.delete()
        return jsonify({"message": "Wallet deleted successfully"}), 200
    except Exception as e:
        return handle_error(e)
