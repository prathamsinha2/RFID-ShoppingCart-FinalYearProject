from flask import Flask, request, jsonify
import logging
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Product class
class Product:
    def __init__(self, rfid_tag, name, price):
        self.rfid_tag = rfid_tag
        self.name = name
        self.price = price

    def to_dict(self):
      return {
          "rfid_tag": self.rfid_tag,
          "name": self.name,
          "price": self.price
      }

# Example product list
products = [
    Product("390094635F91", "BISCUIT", 50.0),
    Product("39009462804F", "BREAD", 20.0),
    Product("3900946DB070", "DETERGENT", 200.0),
    Product("3900947865B0", "SOAP", 100.0),
    Product("3900945B7F89", "MILK", 25.0),
    Product("2F00E1BCF381", "JUICE", 15.0),
    Product("350064F3B517", "TOOTHPASTE", 35.0)
]

# Global counters and data
total_amount = 0.0
item_count = 0
scanned_items = {}

def find_product(rfid):
    for product in products:
        if product.rfid_tag == rfid:
            return product
    return None

# Endpoint to handle RFID scans from ESP module
@app.route('/scan', methods=['POST'])
def scan():
    global total_amount, item_count, scanned_items
    rfid = request.form.get('rfid')
    if not rfid:
        logging.warning("No RFID provided")
        return "Error: No RFID provided", 400

    product = find_product(rfid)
    if product:
        total_amount += product.price
        item_count += 1
        if product.name not in scanned_items:
            scanned_items[product.name] = {
                "price": product.price,
                "quantity": 1,
                "rfid_tag": product.rfid_tag
            }
        else:
             scanned_items[product.name]["quantity"] +=1

        logging.info(f"Product scanned: {product.name}, Price: {product.price}")
        logging.info(f"sanned items: {scanned_items}")
        return f"{product.name}\n{product.price:.2f}"
    else:
        logging.warning(f"Unknown RFID: {rfid}")
        return f"Unknown Tag\n{rfid}"


# Endpoint to display total items and total amount
@app.route('/display', methods=['POST'])
def display():
    global total_amount, item_count
    logging.info(f"Total Items: {item_count}, Total Bill: {total_amount}")
    return f"{item_count}\n{total_amount:.2f}"


# Endpoint to get all available products
@app.route('/products', methods=['GET'])
def get_products():
    product_list = [product.to_dict() for product in products]
    return jsonify(product_list), 200

@app.route('/bill', methods=['GET'])
def bill():
    global total_amount, item_count, scanned_items
    return jsonify(scanned_items), 200

@app.route('/reduce_quantity', methods=['POST'])
def reduce_quantity():
    global total_amount, item_count, scanned_items
    data = request.get_json()
    
    if not data or 'product_id' not in data:
        return jsonify({'error': 'Product ID required'}), 400
        
    product_id = data['product_id']
    product= find_product(product_id)
    if product.name in scanned_items:
        if scanned_items[product.name]['quantity'] > 0:
            scanned_items[product.name]['quantity'] -= 1
            total_amount -= scanned_items[product.name]['price']
            item_count -= 1
            
            if scanned_items[product.name]['quantity'] == 0:
                del scanned_items[product.name]
                
            return jsonify({
                'message': 'Quantity reduced',
                'cart': scanned_items,
                'total': total_amount
            }), 200
    
    return jsonify({'error': 'Product not found in cart'}), 404


@app.route('/add_product', methods=['POST'])
def add_product():
    global total_amount, item_count, scanned_items
    data = request.get_json()
    
    if not data or 'product_id' not in data:
        return jsonify({'error': 'Product ID required'}), 400
        
    product_id = data['product_id']
    product = find_product(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    if product.name in scanned_items:
        scanned_items[product.name]['quantity'] += 1
    else:
        scanned_items[product.name] = {
            'quantity': 1,
            'price': product.price,
            'rfid_tag': product.rfid_tag
        }
    
    total_amount += product.price
    item_count += 1
    
    return jsonify({
        'message': 'Product added',
        'cart': scanned_items,
        'total': total_amount
    }), 200


@app.route('/drop_product', methods=['POST'])
def drop_product():
    global total_amount, item_count, scanned_items
    data = request.get_json()
    
    if not data or 'product_id' not in data:
        return jsonify({'error': 'Product ID required'}), 400
        
    product_id = data['product_id']
    product = find_product(product_id)
    
    if product.name in scanned_items:
        # Update total and count
        total_amount -= (scanned_items[product.name]['price'] * 
                        scanned_items[product.name]['quantity'])
        item_count -= scanned_items[product.name]['quantity']
        
        # Remove product
        del scanned_items[product.name]
        
        return jsonify({
            'message': 'Product removed',
            'cart': scanned_items,
            'total': total_amount
        }), 200
    
    return jsonify({'error': 'Product not found in cart'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)