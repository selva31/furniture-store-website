def test_homepage(client):
    """Test the homepage route."""
    response = client.get('/')
    


def test_gender_route(client):
    """Test the gender-based product filtering."""
    response = client.get('/gender/Male')
    


def test_category_route(client):
    """Test the category-based product filtering."""
    response = client.get('/category/Dress')
    

def test_product_details_route(client):
    """Test the product details route."""
    response = client.get('/1')  # Assuming product ID 1 exists in the DB
    
        


def test_404_not_found(client):
    """Test that a non-existent route returns 404."""
    response = client.get('/nonexistent')
    


def test_homepage_content(client):
    """Test the content of the homepage."""
    response = client.get('/')
    

def test_cart_page(client):
    """Test the cart page route."""
    response = client.get('/cartpage')
    



def test_male_fashion_category(client):
    """Test the Men's Fashion category route."""
    response = client.get('/gender/Male')
    


def test_female_fashion_category(client):
    """Test the Women's Fashion category route."""
    response = client.get('/gender/Female')
    


def test_kids_fashion_category(client):
    """Test the Kids' Fashion category route."""
    response = client.get('/category/Kids')
    

def test_Dresses_category(client):
    """Test the Dresses category route."""
    response = client.get('/category/Dresses')
    

def test_accessory_category(client):
    """Test the Accessories category route."""
    response = client.get('/category/Accessory')
    


def test_Shoes_category(client):
    """Test the Shoes category route."""
    response = client.get('/category/Shoes')
   

def test_product_details_valid(client):
    """Test product details for a valid product."""
    response = client.get('/1')  # Assuming product ID 1 exists
    


def test_search_results(client):
    """Test valid search queries."""
    response = client.get('/search?q=shoes')
    
def test_account_dropdown_links(client):
    """Test the links in the account dropdown menu."""
    response = client.get('/')
   


def test_empty_search_query(client):
    """Test search functionality with an empty query."""
    response = client.get('/search?q=')
    


def test_invalid_method_on_cart(client):
    """Test using an invalid HTTP method on the cart route."""
    response = client.put('/cartpage', data={'product_id': 1})
    

def test_homepage_redirection(client):
    """Test redirection to the homepage if accessing invalid paths."""
    response = client.get('/invalid-path')
    


def test_account_dropdown_visibility(client):
    """Test the account dropdown visibility on the homepage."""
    response = client.get('/')
    

def test_checkout_empty_cart(client):
    """Test attempting to checkout with an empty cart."""
    response = client.post('/checkout')
   

def test_checkout_invalid_payment(client):
    """Test checkout with invalid payment details."""
    response = client.post('/checkout', data={'payment_method': 'invalid_method'})
     

