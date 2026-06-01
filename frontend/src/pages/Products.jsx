import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Products() {
  const [products, setProducts] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    price: '',
    quantity: ''
  });
  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/api/products');
      setProducts(response.data);
    } catch (error) {
      showMessage('Error fetching products', 'error');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await axios.put(`/api/products/${editingId}`, formData);
        showMessage('Product updated successfully', 'success');
        setEditingId(null);
      } else {
        await axios.post('/api/products', formData);
        showMessage('Product created successfully', 'success');
      }
      setFormData({ name: '', sku: '', price: '', quantity: '' });
      fetchProducts();
    } catch (error) {
      showMessage(error.response?.data?.error || 'Error saving product', 'error');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await axios.delete(`/api/products/${id}`);
        showMessage('Product deleted successfully', 'success');
        fetchProducts();
      } catch (error) {
        showMessage('Error deleting product', 'error');
      }
    }
  };

  const handleEdit = (product) => {
    setEditingId(product.id);
    setFormData({
      name: product.name,
      sku: product.sku,
      price: product.price,
      quantity: product.quantity
    });
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 3000);
  };

  return (
    <div>
      <h2>Products</h2>
      
      {message.text && (
        <div className={`message ${message.type}`}>{message.text}</div>
      )}
      
      <div className="form-container">
        <h3>{editingId ? 'Edit Product' : 'Add New Product'}</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Product Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>SKU/Code</label>
            <input
              type="text"
              value={formData.sku}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                required
              />
            </div>
            <div className="form-group">
              <label>Quantity in Stock</label>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                required
              />
            </div>
          </div>
          <button type="submit">{editingId ? 'Update' : 'Create'} Product</button>
          {editingId && (
            <button type="button" onClick={() => {
              setEditingId(null);
              setFormData({ name: '', sku: '', price: '', quantity: '' });
            }} style={{ marginLeft: '1rem', backgroundColor: '#95a5a6' }}>
              Cancel
            </button>
          )}
        </form>
      </div>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>SKU</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id}>
              <td>{product.id}</td>
              <td>{product.name}</td>
              <td>{product.sku}</td>
              <td>${product.price}</td>
              <td>{product.quantity}</td>
              <td>
                <button className="edit" onClick={() => handleEdit(product)}>Edit</button>
                <button className="delete" onClick={() => handleDelete(product.id)} style={{ marginLeft: '0.5rem' }}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Products;