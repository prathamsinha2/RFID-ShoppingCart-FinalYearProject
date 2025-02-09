import streamlit as st
import requests

# ------------------------------------------------
# Custom CSS to style only the "View Store Layout" button.
# ------------------------------------------------
st.markdown(
    """
    <style>
    /* Style the button only within the container that has the "store-layout-container" class */
    .store-layout-container button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-size: 14px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------
# Configuration: Update if your API endpoint differs.
# ------------------------------------------------
BASE_URL = "http://localhost:5000"

# ------------------------------------------------
# Helper function: Attempt a rerun if supported
# ------------------------------------------------
import time

def safe_rerun():
    try:
        # Force a change in the query parameters to trigger a rerun.
        st.st.query_params(_refresh=str(time.time()))
        st.experimental_rerun()
        # If execution continues past st.experimental_rerun(), force an exception.
        raise RuntimeError("Rerun did not interrupt execution.")
    except Exception as e:
        return None


# ------------------------------------------------
# Helper function: Get expander widget with fallback options.
# ------------------------------------------------
def get_expander(label, key=None):
    """
    Returns an expander widget.
    - First, tries to use st.expander with the key.
    - If that raises a TypeError (due to unsupported key parameter), 
      then falls back to st.beta_expander (if available) or st.expander without a key.
    """
    if hasattr(st, "expander"):
        try:
            if key is not None:
                return st.expander(label, key=key)
            else:
                return st.expander(label)
        except TypeError:
            if hasattr(st, "beta_expander"):
                return st.beta_expander(label)
            else:
                return st.expander(label)
    elif hasattr(st, "beta_expander"):
        return st.beta_expander(label)
    else:
        raise Exception("No expander widget available in your Streamlit version.")

# ------------------------------------------------
# API Helper Functions
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
    # "View Store Layout" button on the top right using a column layout.
    # We wrap it in a div with a custom class for styling.
    st.markdown('<div class="store-layout-container">', unsafe_allow_html=True)
    header_cols = st.columns([8, 2])
    if header_cols[1].button("View Store Layout", key="view_layout_products"):
        st.session_state["page"] = "Store Layout"
        safe_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.header("Available Products")
    st.write("Click **+** to add a product to your cart.")
    
    # Define a mapping for product images (update image paths as needed)
    product_images = {
        "BISCUIT": "images/biscuit.jpg",
        "BREAD": "images/bread.jpg",
        "DETERGENT": "images/detergent.jpg",
        "SOAP": "images/soap.jpg",
        "MILK": "images/milk.jpg"
    }
    
    products = fetch_products()
    if products:
        for product in products:
            # Display product details in three columns: name, price, and add button.
            cols = st.columns([3, 2, 1])
            cols[0].markdown(f"**{product['name']}**")
            cols[1].write(f"₹{product['price']}")
            if cols[2].button("➕", key=f"prod_{product['rfid_tag']}"):
                add_product(product["rfid_tag"])
                safe_rerun()
            
            # Add a dropdown (expander) to view in-store location.
            image_path = product_images.get(product['name'])
            if image_path:
                with get_expander("View in-store location", key=f"expander_{product['rfid_tag']}"):
                    st.image(image_path,
                             caption=f"{product['name']} in-store location",
                             use_container_width=True)
            st.markdown("---")
    else:
        st.info("No products available at the moment.")

def cart_page():
    # "View Store Layout" button on the top right (wrapped in our custom container)
    st.markdown('<div class="store-layout-container">', unsafe_allow_html=True)
    header_cols = st.columns([8, 2])
    if header_cols[1].button("View Store Layout", key="view_layout_cart"):
        st.session_state["page"] = "Store Layout"
        safe_rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("Your Cart")
    st.write("Manage your cart using the buttons below:")

    if "cart" not in st.session_state:
        st.session_state["cart"] = fetch_cart()
    
    cart = st.session_state["cart"]
    updated = False

    for prod_name, details in cart.items():
        product_id = details.get("rfid_tag", prod_name)
        cols = st.columns([4, 1, 1, 1])
        cols[0].markdown(
            f"**{prod_name}**  \nQty: {details['quantity']}  \nPrice: ₹{(details['price'])*details['quantity']:.2f}"
        )
        if cols[1].button("➕", key=f"cart_plus_{product_id}"):
            add_product(product_id)
            updated = True
        if cols[2].button("➖", key=f"cart_minus_{product_id}"):
            reduce_quantity(product_id)
            updated = True
        if cols[3].button("🗑️", key=f"cart_drop_{product_id}"):
            drop_product(product_id)
            updated = True
        st.markdown("---")
    
    if updated:
        st.session_state["cart"] = fetch_cart()
        safe_rerun()
    
    total_bill = calculate_total(cart)
    st.subheader(f"Total Bill: ₹{total_bill:.2f}")

def store_layout_page():
    # "Back" button on the top right to return to Products page.
    st.markdown('<div class="store-layout-container">', unsafe_allow_html=True)
    header_cols = st.columns([8, 2])
    if header_cols[1].button("Back", key="back_from_layout"):
        st.session_state["page"] = "Products"
        safe_rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("Store Layout")
    st.image("images/store_layout.jpg",
             caption="Store Layout",
             use_container_width=True)

# ------------------------------------------------
# Main App with Navigation
# ------------------------------------------------
def main():
    st.title("Shopping Cart Webapp")
    
    # Initialize or update navigation.
    if "page" not in st.session_state:
        st.session_state["page"] = st.sidebar.radio("Navigation", ["Products", "Cart"])
    else:
        # Allow sidebar navigation to update the page if not in Store Layout mode.
        nav = st.sidebar.radio("Navigation", ["Products", "Cart"])
        if st.session_state["page"] != "Store Layout":
            st.session_state["page"] = nav

    page = st.session_state["page"]
    
    if page == "Products":
        products_page()
    elif page == "Cart":
        cart_page()
    elif page == "Store Layout":
        store_layout_page()

if __name__ == "__main__":
    main()
