import streamlit as st
import requests

# ------------------------------------------------
# Configuration: Update if your API endpoint differs.
# ------------------------------------------------
BASE_URL = "http://localhost:5000"

# ------------------------------------------------
# Helper function: Safe rerun to avoid AttributeError if not available
# ------------------------------------------------
def safe_rerun():
    try:
        st.experimental_rerun()
    except AttributeError:
        # If st.experimental_rerun() is not available, do nothing.
        pass

# ------------------------------------------------
# Helper functions to call the Flask API endpoints
# ------------------------------------------------
def fetch_products():
    """Fetch the list of available products from the API."""
    try:
        response = requests.get(f"{BASE_URL}/products")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []

def fetch_cart():
    """Fetch the current cart (bill) from the API."""
    try:
        response = requests.get(f"{BASE_URL}/bill")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching cart: {e}")
        return {}

def add_product(product_id):
    """Add a product to the cart via the API."""
    try:
        response = requests.post(f"{BASE_URL}/add_product", json={"product_id": product_id})
        response.raise_for_status()
        st.success("Product added to cart!")
        return response.json()
    except Exception as e:
        st.error(f"Error adding product: {e}")
        return None

def reduce_quantity(product_id):
    """Reduce the quantity of a product in the cart via the API."""
    try:
        response = requests.post(f"{BASE_URL}/reduce_quantity", json={"product_id": product_id})
        response.raise_for_status()
        st.success("Reduced product quantity!")
        return response.json()
    except Exception as e:
        st.error(f"Error reducing product quantity: {e}")
        return None

def drop_product(product_id):
    """Remove a product completely from the cart via the API."""
    try:
        response = requests.post(f"{BASE_URL}/drop_product", json={"product_id": product_id})
        response.raise_for_status()
        st.success("Product removed from cart!")
        return response.json()
    except Exception as e:
        st.error(f"Error dropping product: {e}")
        return None

def calculate_total(cart):
    """Calculate the total bill from the cart items."""
    total = 0.0
    for item in cart.values():
        total += item["price"] * item["quantity"]
    return total

# ------------------------------------------------
# Page Definitions
# ------------------------------------------------
def products_page():
    st.header("Available Products")
    st.write("Click **+** to add a product to your cart.")

    products = fetch_products()
    if products:
        for product in products:
            cols = st.columns([3, 2, 1])
            # Display product name and price
            cols[0].markdown(f"**{product['name']}**")
            cols[1].write(f"₹{product['price']}")
            # **+** button to add product to the cart
            if cols[2].button("➕", key=f"prod_{product['rfid_tag']}"):
                add_product(product["rfid_tag"])
                safe_rerun()  # Refresh the page to update changes
            st.markdown("---")
    else:
        st.info("No products available at the moment.")

def cart_page():
    st.header("Your Cart")
    st.write("Manage your cart using the buttons below:")

    cart = fetch_cart()
    if cart:
        for prod_name, details in cart.items():
            # Use the stored RFID tag (or product name as fallback) as the identifier.
            product_id = details.get("rfid_tag", prod_name)
            cols = st.columns([3, 2, 1, 1, 1])
            # Display product details: name, quantity, unit price
            cols[0].markdown(f"**{prod_name}**")
            cols[1].write(f"Qty: {details['quantity']}")
            cols[2].write(f"₹{details['price']}")
            # **+** button to add one more unit
            if cols[3].button("➕", key=f"cart_plus_{product_id}"):
                add_product(product_id)
                safe_rerun()
            # **–** button to reduce the quantity by one
            if cols[4].button("➖", key=f"cart_minus_{product_id}"):
                reduce_quantity(product_id)
                safe_rerun()
            # A separate button for the drop (🗑️) action
            if st.button("🗑️", key=f"cart_drop_{product_id}"):
                drop_product(product_id)
                safe_rerun()
            st.markdown("---")
        total_bill = calculate_total(cart)
        st.subheader(f"Total Bill: ₹{total_bill:.2f}")
    else:
        st.info("Your cart is empty.")

# ------------------------------------------------
# Main App: Navigation via Sidebar
# ------------------------------------------------
def main():
    st.title("Shopping Cart Webapp")

    # Sidebar Navigation: Select the page to view.
    page = st.sidebar.radio("Navigation", ["Products", "Cart"])

    if page == "Products":
        products_page()
    elif page == "Cart":
        cart_page()

if __name__ == "__main__":
    main()
