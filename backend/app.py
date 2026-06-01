from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection, execute_query, fetch_all, fetch_one, init_database, DATABASE_URL
import sqlite3
import os

app = Flask(__name__)

# Configure CORS - Allow all origins (simplest for now)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add CORS headers after every request
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

# Initialize database when app starts
init_database()

# Helper function to convert row to dict
def row_to_dict(row, is_postgres):
    if is_postgres:
        return dict(row) if row else None
    else:
        return dict(row) if row else None

# ============ PRODUCTS APIs ============

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    conn = get_db_connection()
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY id DESC')
        products = cursor.fetchall()
        cursor.close()
    else:
        products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    """Get single product by ID"""
    conn = get_db_connection()
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
        product = cursor.fetchone()
        cursor.close()
    else:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    if product:
        return jsonify(dict(product))
    return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
def create_product():
    """Create new product"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'sku', 'price', 'quantity']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate quantity is not negative
    if data['quantity'] < 0:
        return jsonify({'error': 'Product quantity cannot be negative'}), 400
    
    # Validate price is not negative
    if data['price'] < 0:
        return jsonify({'error': 'Price cannot be negative'}), 400
    
    conn = get_db_connection()
    try:
        if DATABASE_URL:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO products (name, sku, price, quantity) VALUES (%s, %s, %s, %s) RETURNING id',
                (data['name'], data['sku'], data['price'], data['quantity'])
            )
            new_id = cursor.fetchone()['id']
            cursor.execute('SELECT * FROM products WHERE id = %s', (new_id,))
            new_product = cursor.fetchone()
            conn.commit()
            cursor.close()
        else:
            cursor = conn.execute(
                'INSERT INTO products (name, sku, price, quantity) VALUES (?, ?, ?, ?)',
                (data['name'], data['sku'], data['price'], data['quantity'])
            )
            conn.commit()
            new_product = conn.execute('SELECT * FROM products WHERE id = ?', (cursor.lastrowid,)).fetchone()
        conn.close()
        return jsonify(dict(new_product)), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        if 'UNIQUE' in str(e) or 'unique' in str(e):
            return jsonify({'error': 'SKU already exists'}), 400
        return jsonify({'error': str(e)}), 400

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    """Update product details"""
    data = request.json
    conn = get_db_connection()
    
    # Check if product exists
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
        product = cursor.fetchone()
        cursor.close()
    else:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    
    if not product:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    # Update fields
    name = data.get('name', product['name'])
    sku = data.get('sku', product['sku'])
    price = data.get('price', product['price'])
    quantity = data.get('quantity', product['quantity'])
    
    if quantity < 0:
        conn.close()
        return jsonify({'error': 'Quantity cannot be negative'}), 400
    
    if price < 0:
        conn.close()
        return jsonify({'error': 'Price cannot be negative'}), 400
    
    try:
        if DATABASE_URL:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE products SET name = %s, sku = %s, price = %s, quantity = %s WHERE id = %s',
                (name, sku, price, quantity, id)
            )
            conn.commit()
            cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
            updated_product = cursor.fetchone()
            cursor.close()
        else:
            conn.execute(
                'UPDATE products SET name = ?, sku = ?, price = ?, quantity = ? WHERE id = ?',
                (name, sku, price, quantity, id)
            )
            conn.commit()
            updated_product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
        conn.close()
        return jsonify(dict(updated_product))
    except Exception as e:
        conn.rollback()
        conn.close()
        if 'UNIQUE' in str(e) or 'unique' in str(e):
            return jsonify({'error': 'SKU already exists'}), 400
        return jsonify({'error': str(e)}), 400

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """Delete product"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
        product = cursor.fetchone()
        if not product:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
        cursor.execute('DELETE FROM products WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
    else:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
        if not product:
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
    
    conn.close()
    return jsonify({'message': 'Product deleted successfully'}), 200

# ============ CUSTOMERS APIs ============

@app.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    conn = get_db_connection()
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY id DESC')
        customers = cursor.fetchall()
        cursor.close()
    else:
        customers = conn.execute('SELECT * FROM customers ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(c) for c in customers])

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    """Get single customer by ID"""
    conn = get_db_connection()
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = %s', (id,))
        customer = cursor.fetchone()
        cursor.close()
    else:
        customer = conn.execute('SELECT * FROM customers WHERE id = ?', (id,)).fetchone()
    conn.close()
    if customer:
        return jsonify(dict(customer))
    return jsonify({'error': 'Customer not found'}), 404

@app.route('/customers', methods=['POST'])
def create_customer():
    """Create new customer"""
    data = request.json
    
    required_fields = ['name', 'email', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    conn = get_db_connection()
    try:
        if DATABASE_URL:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s) RETURNING id',
                (data['name'], data['email'], data['phone'])
            )
            new_id = cursor.fetchone()['id']
            cursor.execute('SELECT * FROM customers WHERE id = %s', (new_id,))
            new_customer = cursor.fetchone()
            conn.commit()
            cursor.close()
        else:
            cursor = conn.execute(
                'INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
                (data['name'], data['email'], data['phone'])
            )
            conn.commit()
            new_customer = conn.execute('SELECT * FROM customers WHERE id = ?', (cursor.lastrowid,)).fetchone()
        conn.close()
        return jsonify(dict(new_customer)), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        if 'UNIQUE' in str(e) or 'unique' in str(e):
            return jsonify({'error': 'Email already exists'}), 400
        return jsonify({'error': str(e)}), 400

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """Delete customer"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = %s', (id,))
        customer = cursor.fetchone()
        if not customer:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404
        cursor.execute('DELETE FROM customers WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
    else:
        customer = conn.execute('SELECT * FROM customers WHERE id = ?', (id,)).fetchone()
        if not customer:
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404
        conn.execute('DELETE FROM customers WHERE id = ?', (id,))
        conn.commit()
    
    conn.close()
    return jsonify({'message': 'Customer deleted successfully'}), 200

# ============ ORDERS APIs ============

@app.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders with customer and product details"""
    conn = get_db_connection()
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*, c.name as customer_name, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN products p ON o.product_id = p.id
            ORDER BY o.created_at DESC
        ''')
        orders = cursor.fetchall()
        cursor.close()
    else:
        orders = conn.execute('''
            SELECT o.*, c.name as customer_name, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN products p ON o.product_id = p.id
            ORDER BY o.created_at DESC
        ''').fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])

@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    """Get single order by ID"""
    conn = get_db_connection()
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*, c.name as customer_name, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN products p ON o.product_id = p.id
            WHERE o.id = %s
        ''', (id,))
        order = cursor.fetchone()
        cursor.close()
    else:
        order = conn.execute('''
            SELECT o.*, c.name as customer_name, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN products p ON o.product_id = p.id
            WHERE o.id = ?
        ''', (id,)).fetchone()
    conn.close()
    if order:
        return jsonify(dict(order))
    return jsonify({'error': 'Order not found'}), 404

@app.route('/orders', methods=['POST'])
def create_order():
    """Create new order and automatically reduce stock"""
    data = request.json
    
    required_fields = ['customer_id', 'product_id', 'quantity']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    conn = get_db_connection()
    
    # Check if product exists and has enough stock
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = %s', (data['product_id'],))
        product = cursor.fetchone()
        cursor.close()
    else:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (data['product_id'],)).fetchone()
    
    if not product:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    if product['quantity'] < data['quantity']:
        conn.close()
        return jsonify({'error': f'Insufficient stock. Available: {product["quantity"]}'}), 400
    
    # Check if customer exists
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = %s', (data['customer_id'],))
        customer = cursor.fetchone()
        cursor.close()
    else:
        customer = conn.execute('SELECT * FROM customers WHERE id = ?', (data['customer_id'],)).fetchone()
    
    if not customer:
        conn.close()
        return jsonify({'error': 'Customer not found'}), 404
    
    # Calculate total amount
    total_amount = product['price'] * data['quantity']
    
    # Create order and reduce stock (all in one transaction)
    try:
        if DATABASE_URL:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO orders (customer_id, product_id, quantity, total_amount) VALUES (%s, %s, %s, %s) RETURNING id',
                (data['customer_id'], data['product_id'], data['quantity'], total_amount)
            )
            new_id = cursor.fetchone()['id']
            
            # Reduce product quantity
            cursor.execute(
                'UPDATE products SET quantity = quantity - %s WHERE id = %s',
                (data['quantity'], data['product_id'])
            )
            
            conn.commit()
            
            cursor.execute('''
                SELECT o.*, c.name as customer_name, p.name as product_name, p.price as product_price
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                JOIN products p ON o.product_id = p.id
                WHERE o.id = %s
            ''', (new_id,))
            new_order = cursor.fetchone()
            cursor.close()
        else:
            cursor = conn.execute(
                'INSERT INTO orders (customer_id, product_id, quantity, total_amount) VALUES (?, ?, ?, ?)',
                (data['customer_id'], data['product_id'], data['quantity'], total_amount)
            )
            
            # Reduce product quantity
            conn.execute(
                'UPDATE products SET quantity = quantity - ? WHERE id = ?',
                (data['quantity'], data['product_id'])
            )
            
            conn.commit()
            
            new_order = conn.execute('''
                SELECT o.*, c.name as customer_name, p.name as product_name, p.price as product_price
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                JOIN products p ON o.product_id = p.id
                WHERE o.id = ?
            ''', (cursor.lastrowid,)).fetchone()
        
        conn.close()
        return jsonify(dict(new_order)), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    """Cancel/Delete an order"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = %s', (id,))
        order = cursor.fetchone()
        if not order:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Order not found'}), 404
        
        # Restore product quantity
        cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s',
                       (order['quantity'], order['product_id']))
        cursor.execute('DELETE FROM orders WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
    else:
        order = conn.execute('SELECT * FROM orders WHERE id = ?', (id,)).fetchone()
        if not order:
            conn.close()
            return jsonify({'error': 'Order not found'}), 404
        
        conn.execute('UPDATE products SET quantity = quantity + ? WHERE id = ?',
                     (order['quantity'], order['product_id']))
        conn.execute('DELETE FROM orders WHERE id = ?', (id,))
        conn.commit()
    
    conn.close()
    return jsonify({'message': 'Order cancelled successfully'}), 200

# ============ DASHBOARD API ============

@app.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM products')
        total_products = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM customers')
        total_customers = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM orders')
        total_orders = cursor.fetchone()['count']
        cursor.close()
    else:
        total_products = conn.execute('SELECT COUNT(*) as count FROM products').fetchone()['count']
        total_customers = conn.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count']
        total_orders = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders
    })

@app.errorhandler(Exception)
def handle_error(e):
    print("=" * 50)
    print("ERROR OCCURRED:")
    print(str(e))
    import traceback
    traceback.print_exc()
    print("=" * 50)
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)