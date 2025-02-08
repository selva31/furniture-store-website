from flask import Flask, render_template, jsonify, request
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from sqlalchemy import func
import io 
from datetime import datetime, timedelta
from io import BytesIO
import base64
from . import db
from . models import *
from flask import Blueprint
visualization = Blueprint('visualization',__name__,static_folder='static')


@visualization.route('/')
def home():
    # Render the home page without any chart data
    return render_template('visualization.html', chart_url=None)
@visualization.route('/roles_chart')
def roles_chart():
    # Fetch user data for visualization
    roles = db.session.query(User.role, db.func.count(User.role)).group_by(User.role).all()
    roles_dict = {role: count for role, count in roles}

    # Generate Pie Chart
    labels = roles_dict.keys()
    sizes = roles_dict.values()
    colors = ['#A3D8F4', '#FFCF9F', '#B8F0D3', '#F9D5E5', '#FFE4C4']  # Subtle colors
    explode = [0.1 if max(sizes) == size else 0 for size in sizes]  # Highlight the largest segment

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    # Save the chart to a PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    pie_chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    # Analytics Data
    total_users = sum(sizes)
    analytics_data = {
        "total_users": total_users,
        "role_distribution": roles_dict
    }

    return render_template('roles.html', pie_chart_url=pie_chart_url, analytics_data=analytics_data,title='Roles Chart',side_title='Real Time data',t1='Total Users:',t2='Role breakdown')


@visualization.route('/sales_by_city')
def sales_by_city():
    # Query database to group users by city and calculate sales (mock data below)
    city_sales = db.session.query(User.city, db.func.count(User.id)).group_by(User.city).all()

    # Data preparation for visualization
    cities = [item[0] for item in city_sales]
    sales = [item[1] * 100 for item in city_sales]  # Assuming each user contributes $100 to sales

    # Create bar chart with three basic colors
    fig = Figure()
    ax = fig.subplots()
    colors = ['#FF9999', '#99CCFF', '#FFCC99']  # Three basic colors (light red, blue, and orange)
    ax.bar(cities, sales, color=colors[:len(cities)])
    ax.set_title('Sales by City', fontsize=16)
    ax.set_xlabel('City', fontsize=12)
    ax.set_ylabel('Sales ($)', fontsize=12)
    ax.set_xticklabels(cities, rotation=45, ha='right')

    # Save chart to BytesIO object
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    # Pass chart URL and data to the template
    return render_template('sales_city.html', chart_url=chart_url, city_sales=city_sales,title='sales by city',side_title='Real Time data',t1='City',t2='Sales')

@visualization.route('/revenue_trends')
def revenue_trends():
    from sqlalchemy.orm import aliased
    from sqlalchemy import func

    # Get revenue per category dynamically
    product_alias = aliased(Product)
    revenue_per_category = (
        db.session.query(
            product_alias.category,
            func.sum(OrderedProduct.order_amount).label("total_revenue")
        )
        .join(product_alias, OrderedProduct.product_id == product_alias.id)
        .group_by(product_alias.category)
        .all()
    )

    # Extracting categories and revenue values
    categories = [row[0] for row in revenue_per_category]
    revenues = [row[1] for row in revenue_per_category]

    # Total revenue and orders
    total_orders = db.session.query(func.count(OrderDetails.id)).scalar()
    current_year_revenue = sum(revenues)

    # Fetch previous year's revenue dynamically
    previous_year_revenue = (
        db.session.query(func.sum(OrderedProduct.order_amount))
        .join(OrderDetails, OrderedProduct.order_details_id == OrderDetails.id)
        .filter(OrderDetails.order_date.between("2024-01-01", "2024-12-31"))
        .scalar() or 0
    )

    # Projected revenue for 2030
    growth_rate = 0.1  # Assuming 10% growth rate
    years = 2030 - 2025
    expected_revenue_2030 = current_year_revenue * ((1 + growth_rate) ** years)

    # Analytics data
    analytics = {
        "Total Orders": f"{total_orders}",
        "Total Revenue (INR)": f"{current_year_revenue:,}",
        "Expected Revenue in 2030 (INR)": f"{expected_revenue_2030:,.2f}",
        "Previous Year Revenue (INR)": f"{previous_year_revenue:,}",
        "Current Year Revenue (INR)": f"{current_year_revenue:,}",
        "Top Category": categories[revenues.index(max(revenues))] if revenues else "N/A",
        "Least Category": categories[revenues.index(min(revenues))] if revenues else "N/A",
        "Categories": list(zip(categories, revenues)),
    }

    # Create a pie chart with subtle colors
    plt.figure(figsize=(8, 6))
    colors = ['#5E81AC', '#81A1C1', '#88C0D0', '#A3BE8C', '#EBCB8B']
    plt.pie(
        revenues,
        labels=categories,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        textprops={'color': '#333', 'fontsize': 12}
    )
    plt.title("Revenue by Category (INR)", fontsize=16, color="#2E3440")

    # Save chart as base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.close()

    return render_template(
        "revenue_trends.html",
        chart_data=chart_data,
        analytics=analytics,
        previous_year_revenue=previous_year_revenue,
        current_year_revenue=current_year_revenue
    )

@visualization.route('/delivery_chart')
def delivery_chart():
    # Query order statuses and count occurrences
    order_status_counts = (
        db.session.query(OrderDetails.status, func.count(OrderDetails.id))
        .group_by(OrderDetails.status)
        .all()
    )

    # Convert query results into a dictionary
    status_dict = {status: count for status, count in order_status_counts}

    # Define standard categories and fill missing ones with 0
    categories = ["Pending", "In Transit", "Delivered", "Failed"]
    values = [status_dict.get(status, 0) for status in categories]

    # Define color scheme
    colors = ['#f4a261', '#a8dadc', '#2a9d8f', '#e63946']  # Orange, Teal, Green, Red

    # Create a horizontal bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(categories, values, color=colors)
    ax.set_xlabel("Number of Orders", fontsize=12)
    ax.set_title("Order Status Distribution", fontsize=16)
    ax.grid(alpha=0.3)

    # Save chart as a base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    # Analytics Data
    total_orders = sum(values)
    analytics = {
        "Pending Orders": values[0],
        "Shipped Orders": values[1],
        "Delivered Orders": values[2],
        "Failed Orders": values[3],
        "Total Orders": total_orders,
    }

    # Fetch latest orders dynamically
    orders = (
        db.session.query(OrderDetails.id, OrderDetails.user_name, OrderDetails.status, OrderDetails.order_date)
        .order_by(OrderDetails.order_date.desc())
        .limit(5)
        .all()
    )

    # Convert orders into a list of dictionaries
    orders_data = [
        {
            "id": order.id,
            "user": order.user_name,
            "status": order.status,
            "order_date": order.order_date.strftime("%Y-%m-%d"),
        }
        for order in orders
    ]

    return render_template(
        "delivery_chart.html", chart_data=chart_data, analytics=analytics, orders=orders_data
    )


@visualization.route("/customer_trends") 
def customer_trends():
    today = datetime.today()
    days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(12)]  # Last 12 days

    # Fetch users who made their first order more than 12 days ago
    past_customers = (
        db.session.query(OrderDetails.user_id)
        .group_by(OrderDetails.user_id)
        .having(db.func.min(OrderDetails.order_date) < today - timedelta(days=12))  # At least one old order
        .subquery()
    )

    # Fetch new customers (users created in last 12 days)
    new_customers_data = (
        db.session.query(User.dob, db.func.count(User.id))
        .filter(User.dob >= today - timedelta(days=12))
        .group_by(User.dob)
        .all()
    )

    # Fetch returning customers: Users from past_customers who ordered in last 12 days
    returning_customers_data = (
        db.session.query(OrderDetails.order_date, db.func.count(db.distinct(OrderDetails.user_id)))
        .filter(OrderDetails.user_id.in_(db.session.query(past_customers.c.user_id)))  # Ensure previous orders exist
        .filter(OrderDetails.order_date >= today - timedelta(days=12))  # Count their new orders
        .group_by(OrderDetails.order_date)
        .all()
    )

    # Convert data to dictionaries
    new_customers = {str(date): count for date, count in new_customers_data}
    returning_customers = {str(date): count for date, count in returning_customers_data}

    # Fill missing days with zeros
    new_customers_list = [new_customers.get(day, 0) for day in days]
    returning_customers_list = [returning_customers.get(day, 0) for day in days]

    # Generate the line graph using Matplotlib
    plt.figure(figsize=(10, 5))
    
    plt.plot(days, new_customers_list, marker="o", linestyle="-", label="New Customers", color="#6a89cc")
    plt.plot(days, returning_customers_list, marker="o", linestyle="-", label="Returning Customers", color="#82ccdd")

    plt.title("New and Returning Customers Trends", fontsize=14)
    plt.xlabel("Days")
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the chart to a buffer and encode it as a base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    # Fetch latest new customers details
    new_customers_details = (
        db.session.query(User.username, User.city, User.dob)
        .order_by(User.dob.desc())
        .limit(5)
        .all()
    )
    new_customers_details = [
        {"name": user.username, "location": user.city, "date_joined": user.dob} for user in new_customers_details
    ]

    # Total counts
    total_new_customers = sum(new_customers_list)
    total_returning_customers = sum(returning_customers_list)

    return render_template(
        "Customer_trends.html",
        chart_base64=chart_base64,
        new_customers_details=new_customers_details,
        total_new_customers=total_new_customers,
        total_returning_customers=total_returning_customers,
    )

import random
@visualization.route("/financial_health")
def financial_health():
    # Fetch financial data from the database
    orders = OrderDetails.query.all()
    
    today = datetime.today()
    days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]
    revenue, expenses, profit = [], [], []
    
    for day in days:
        day_orders = [order for order in orders if order.order_date.strftime('%Y-%m-%d') == day]
        day_revenue = sum(order.grand_total if order.grand_total is not None else 0 for order in day_orders)
        day_expenses = sum(order.delivery_charges if order.delivery_charges is not None else random.randint(50, 500) for order in day_orders)

        day_profit = day_revenue - day_expenses
        
        revenue.append(day_revenue)
        expenses.append(day_expenses)
        profit.append(day_profit)
    
    financial_data = [
        {
            "customer": order.user_name, 
            "product": ", ".join([product.name for product in order.products]),
            "quantity": sum([product.quantity for product in order.orders]),
            "total": order.grand_total,
            "expenses": order.delivery_charges,
            "profit": order.grand_total - order.delivery_charges
        } for order in orders[:5]
    ]
    
    real_time_analytics = {
        "Current Revenue": f"Rs {revenue[-1]:,.2f}",
        "Current Expenses": f"Rs {expenses[-1]:,.2f}",
        "Current Profit": f"Rs {profit[-1]:,.2f}",
    }
    
    # Financial Performance Graph
    plt.figure(figsize=(10, 5))
    pastel_colors = {"Revenue": "#a8dadc", "Expenses": "#f4a261", "Profit": "#e76f51"}
    plt.plot(days, revenue, marker='o', label="Revenue", color=pastel_colors["Revenue"], linewidth=2)
    plt.plot(days, expenses, marker='o', label="Expenses", color=pastel_colors["Expenses"], linewidth=2)
    plt.plot(days, profit, marker='o', label="Profit", color=pastel_colors["Profit"], linewidth=2)
    plt.title("Financial Performance Over Time", fontsize=16)
    plt.xlabel("Days", fontsize=12)
    plt.ylabel("Amount ($)", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(alpha=0.3)
    
    img_line = io.BytesIO()
    plt.savefig(img_line, format='png', bbox_inches='tight')
    img_line.seek(0)
    img_line_base64 = base64.b64encode(img_line.getvalue()).decode('utf-8')
    plt.close()
    
    return render_template("financial_health.html", 
                           img_line_base64=img_line_base64, 
                           real_time_analytics=real_time_analytics, 
                           days=days, 
                           revenue=revenue, 
                           expenses=expenses, 
                           profit=profit,
                           financial_data=financial_data)

def generate_chart(data):
    
    if not data:
        
        return None  

    product_names = [item["name"] for item in data]
    stock = [item["stock"] for item in data]

  

    plt.figure(figsize=(8, 6))
    plt.bar(product_names, stock, color="skyblue")
    plt.title("Product Stock Chart")
    plt.xlabel("Products")
    plt.ylabel("Stock")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    
    return chart_data



@visualization.route('/visualization/<category>')
def category_page(category):
    
    
    page = request.args.get('page', default=1, type=int)
    has_next = True  # Example logic for pagination
    products = Product.query.all()
    for product in products:
        print(f"Product Name: {product.name}, Category: {product.category}, Stock: {product.quantity}")
    # Fetch products for the selected category
    products_query = Product.query.filter_by(category=category).paginate(page=page, per_page=10, error_out=False)
    total_stock = db.session.query(db.func.sum(Product.quantity)).filter_by(category=category).scalar()
    total_stock = total_stock if total_stock else 0  # Ensure it doesn't return None

    
    if products_query.items:  # Check if there are products
        products = [{"name": product.name, "stock": product.quantity} for product in products_query.items]
      
        chart_data = generate_chart(products)
    else:
       
        products = []
        chart_data = None  

    return render_template(
        "category_page.html", 
        category=category, 
        title=category.capitalize(), 
        products=products, 
        chart_data=chart_data, 
        page=page,total_stock=total_stock, 
        has_next=has_next
    )




@visualization.route('/inventory_status')
def inventory_status():
    # Static data for pagination logic
    page = request.args.get('page', default=1, type=int)

    has_next = True  # Example logic for pagination

    # Query the Product table to get the categories and total stock
    categories_query = db.session.query(Product.category, db.func.sum(Product.quantity).label('total_stock')) \
        .group_by(Product.category).all()

    # Prepare category data for visualization
    category_labels = [category[0] for category in categories_query]
    category_stock = [category[1] for category in categories_query]

    # Analytics Data
    total_stock = sum(category_stock)
    max_stock_category = category_labels[category_stock.index(max(category_stock))]
    min_stock_category = category_labels[category_stock.index(min(category_stock))]

    low_stock_threshold = 5
    low_stock_products = Product.query.filter(Product.quantity < low_stock_threshold).all()

    # Out of Stock Items
    out_of_stock_items = Product.query.filter(Product.quantity == 0).all()

    # Total number of products
    total_products = Product.query.count()

    analytics = {
        "Total Stock": total_stock,
        "Category with Max Stock": max_stock_category,
        "Category with Min Stock": min_stock_category,
        "Low Stock Alerts": len(low_stock_products),
        "Out of Stock Items": len(out_of_stock_items),
        "Total Products": total_products
    }

    # Default stock value
    default_stock = 2

    # Create a bar chart with a default stock line
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(category_labels, category_stock, color=plt.cm.Pastel1.colors)
    ax.axhline(y=default_stock, color='red', linestyle='--', linewidth=1.5, label=f"Default Stock: {default_stock}")
    ax.set_title("Stock Analytics by Category", fontsize=14)
    ax.set_xlabel("Categories")
    ax.set_ylabel("Total Stock (Quantity)")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(loc='upper right')

    # Save chart as a base64 string
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    # Fetch static product details for display
    products_query = Product.query.all()
    products = [{"id": product.id, "name": product.name, "category": product.category, "quantity": product.quantity} for product in products_query]

    return render_template(
        "inventory_status.html",
        page=page,
        chart_data=chart_data,
        has_next=has_next,
        analytics=analytics,
        products=products,
    )