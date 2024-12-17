from flask import Blueprint, Flask, request, redirect, jsonify
from datetime import datetime
import hashlib
import hmac
import urllib.parse

payment_blueprint = Blueprint("payment", __name__)
# Configurations (replace with your real VNPAY configurations)
VNPAY_TMN_CODE = "DEXN209R" #for testing only
VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
VNPAY_HASH_SECRET_KEY = "PDBGSF700IA65NESBHT4K2B3EGDNYNM9" #for testing only
VNPAY_RETURN_URL = "https://<publicdomain_using_ngrok>/payment/test"

# Helper function to get client IP
def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR']
    else:
        return request.environ['REMOTE_ADDR']

# VNPAY helper class
class VNPAY:
    def __init__(self):
        self.request_data = {}

    def build_payment_url(self, payment_url, secret_key):
        sorted_data = sorted(self.request_data.items())
        query_string = urllib.parse.urlencode(sorted_data)
        hash_value = hmac.new(
            secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        return f"{payment_url}?{query_string}&vnp_SecureHash={hash_value}"

@payment_blueprint.route('/create_payment', methods=['POST'])
def payment():
    if request.method == 'POST':
        data = request.json
        order_type = data.get('order_type')
        order_id = data.get('order_id')
        amount = data.get('amount')
        order_desc = data.get('order_desc')
        ipaddr = get_client_ip()

        # Validate required fields
        if not all([order_type, order_id, amount, order_desc]):
            return jsonify({"error": "Missing required fields"}), 400

        # Build VNPAY request
        vnp = VNPAY()
        vnp.request_data['vnp_Version'] = '2.1.0'
        vnp.request_data['vnp_Command'] = 'pay'
        vnp.request_data['vnp_TmnCode'] = VNPAY_TMN_CODE
        vnp.request_data['vnp_Amount'] = int(amount) * 100
        vnp.request_data['vnp_CurrCode'] = 'VND'
        vnp.request_data['vnp_TxnRef'] = "190000"
        vnp.request_data['vnp_OrderInfo'] = order_desc
        vnp.request_data['vnp_OrderType'] = order_type
        vnp.request_data['vnp_Locale'] = "vn"
        vnp.request_data['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.request_data['vnp_IpAddr'] = ipaddr
        vnp.request_data['vnp_ReturnUrl'] = VNPAY_RETURN_URL

        #vnp.request_data['vnp_BankCode'] = "VNPAYQR"

        # Generate payment URL
        payment_url = vnp.build_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
        print(f"Redirecting to payment URL: {payment_url}")

        return redirect(payment_url)
    else:
        return jsonify({"error": "Method not allowed"}), 405
    
@payment_blueprint.route('/test', methods=['GET'])
def test_payment():
    vnp_response = request.args.to_dict()
    vnp_secure_hash = vnp_response.pop('vnp_SecureHash', None)  # Lấy chữ ký

    # Sắp xếp các tham số còn lại theo thứ tự alphabet
    sorted_params = sorted(vnp_response.items())
    query_string = urllib.parse.urlencode(sorted_params)

    # Tính toán lại chữ ký bằng hash
    hmac_obj = hmac.new(
        VNPAY_HASH_SECRET_KEY.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha512
    )
    calculated_hash = hmac_obj.hexdigest()

    # So sánh chữ ký đã tính toán với chữ ký từ VNPAY
    if calculated_hash == vnp_secure_hash:
        # Nếu chữ ký hợp lệ, kiểm tra mã phản hồi
        response_code = vnp_response.get("vnp_ResponseCode")
        if response_code == "00":
            return jsonify({"message": "Thanh toán thành công", "data": vnp_response})
        else:
            return jsonify({"message": "Thanh toán thất bại", "data": vnp_response}), 400
    else:
        return jsonify({"error": "Chữ ký không hợp lệ"}), 400