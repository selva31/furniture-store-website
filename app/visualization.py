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
from .models import *
from flask import Blueprint
import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

visualization = Blueprint('visualization', __name__, static_folder='static')

# Professional neutral color palettes
NEUTRAL_PALETTE = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F',
                   '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC']

PASTEL_PALETTE = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF',
                  '#FFFEA3', '#B9F2F0', '#C9C9C9', '#FFD1DF', '#8FD3FF']

SEQUENTIAL_PALETTE = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1',
                      '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']

# Create custom colormaps
neutral_cmap = LinearSegmentedColormap.from_list('neutral', NEUTRAL_PALETTE)
pastel_cmap = LinearSegmentedColormap.from_list('pastel', PASTEL_PALETTE)


def apply_style():
    """Apply consistent styling to all plots"""
    plt.style.use('seaborn-v0_8')
    plt.rcParams['figure.facecolor'] = '#F7F5F0'  # Match your cream background
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['grid.color'] = '#2A2A2A'  # Match your charcoal color
    plt.rcParams['axes.edgecolor'] = '#2A2A2A'
    plt.rcParams['axes.labelcolor'] = '#2A2A2A'
    plt.rcParams['text.color'] = '#2A2A2A'
    plt.rcParams['xtick.color'] = '#2A2A2A'
    plt.rcParams['ytick.color'] = '#2A2A2A'
    plt.rcParams['font.family'] = 'Montserrat'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.titleweight'] = '500'


@visualization.route('/')
def home():
    return render_template('visualization.html', chart_url=None)


@visualization.route('/roles_chart')
def roles_chart():
    apply_style()

    # Fetch user data for visualization
    roles = db.session.query(User.role, func.count(User.role)).group_by(User.role).all()
    roles_dict = {role: count for role, count in roles}

    # Generate data
    labels = list(roles_dict.keys())
    sizes = list(roles_dict.values())

    # Create figure with constrained layout
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

    # Create pie chart with improved aesthetics
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=NEUTRAL_PALETTE[:len(labels)],
        autopct=lambda p: f'{p:.1f}%\n({int(p / 100. * sum(sizes))})',
        startangle=140,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
        textprops={'fontsize': 10, 'color': '#2A2A2A'}
    )

    # Improve autotext appearance
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')

    # Equal aspect ratio and title
    ax.axis('equal')
    ax.set_title('User Role Distribution', pad=20, fontsize=14, weight='bold')

    # Add legend
    ax.legend(
        wedges,
        labels,
        title="Roles",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        frameon=False
    )

    # Save chart
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=120)
    img.seek(0)
    pie_chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    # Analytics Data
    total_users = sum(sizes)
    analytics_data = {
        "total_users": total_users,
        "role_distribution": roles_dict,
        "primary_role": max(roles_dict, key=roles_dict.get),
        "role_diversity": len(roles_dict)
    }

    return render_template(
        'roles.html',
        pie_chart_url=pie_chart_url,
        analytics_data=analytics_data,
        title='User Roles Analysis',
        side_title='Real Time Data',
        t1='Total Users:',
        t2='Role Breakdown'
    )


@visualization.route('/sales_by_city')
def sales_by_city():
    apply_style()

    # Query database to group users by city and calculate sales
    city_data = db.session.query(
        User.city,
        func.count(User.id).label('user_count'),
        func.sum(OrderDetails.grand_total).label('total_sales')
    ).join(OrderDetails, User.id == OrderDetails.user_id) \
        .group_by(User.city) \
        .order_by(func.sum(OrderDetails.grand_total).desc()) \
        .all()

    # Prepare data
    cities = [item[0] for item in city_data]
    sales = [float(item[2]) for item in city_data]
    customers = [item[1] for item in city_data]

    # Normalize for bubble sizes (min size 100, max size 1000)
    min_size, max_size = 100, 1000
    sizes = [min_size + (max_size - min_size) * (x - min(customers)) / (max(customers) - min(customers))
             for x in customers]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create scatter plot with bubbles sized by customer count
    scatter = ax.scatter(
        cities, sales,
        s=sizes,
        c=NEUTRAL_PALETTE[:len(cities)],
        alpha=0.7,
        edgecolors='white',
        linewidth=1
    )

    # Add value labels
    for i, (city, sale) in enumerate(zip(cities, sales)):
        ax.text(
            i, sale, f'₹{sale:,.0f}',
            ha='center', va='bottom',
            fontsize=9, weight='bold'
        )

    # Customize plot
    ax.set_title('Sales Performance by City', pad=20, fontsize=14, weight='bold')
    ax.set_xlabel('City', labelpad=10)
    ax.set_ylabel('Total Sales (₹)', labelpad=10)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')

    # Create legend for bubble sizes
    kw = dict(prop="sizes", num=5, color=NEUTRAL_PALETTE[0],
              fmt="{x:.0f}", func=lambda s: min(customers) + (max(customers) - min(customers)) * (s - min_size) / (
                    max_size - min_size))
    legend = ax.legend(*scatter.legend_elements(**kw), title="Customers", loc="upper right")

    # Save chart
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=120)
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Prepare analytics
    total_sales = sum(sales)
    avg_sale_per_city = total_sales / len(sales) if len(sales) > 0 else 0
    top_city = cities[0]

    analytics = {
        "total_sales": f"₹{total_sales:,.2f}",
        "avg_sale_per_city": f"₹{avg_sale_per_city:,.2f}",
        "top_performing_city": top_city,
        "cities_covered": len(cities),
        "sales_distribution": list(zip(cities, sales))
    }

    return render_template(
        'sales_city.html',
        chart_url=chart_url,
        analytics=analytics,
        title='Sales by City Analysis',
        side_title='Regional Performance',
        t1='Top City',
        t2='Sales Breakdown'
    )


@visualization.route('/revenue_trends')
def revenue_trends():
    apply_style()

    # Get current year and previous year
    current_year = datetime.now().year
    prev_year = current_year - 1

    # Query revenue data by category for current year
    revenue_data = db.session.query(
        Product.category,
        func.sum(OrderedProduct.order_amount).label('total_revenue')
    ).join(OrderedProduct, Product.id == OrderedProduct.product_id) \
        .join(OrderDetails, OrderedProduct.order_details_id == OrderDetails.id) \
        .filter(OrderDetails.order_date >= f'{current_year}-01-01') \
        .group_by(Product.category) \
        .order_by(func.sum(OrderedProduct.order_amount).desc()) \
        .all()

    # Query monthly revenue trends
    monthly_revenue = db.session.query(
        func.extract('month', OrderDetails.order_date).label('month'),
        func.sum(OrderedProduct.order_amount).label('monthly_revenue')
    ).join(OrderedProduct, OrderDetails.id == OrderedProduct.order_details_id) \
        .filter(OrderDetails.order_date >= f'{current_year}-01-01') \
        .group_by(func.extract('month', OrderDetails.order_date)) \
        .order_by('month') \
        .all()

    # Prepare data
    categories = [item[0] for item in revenue_data]
    revenues = [float(item[1]) for item in revenue_data]
    months = [int(item[0]) for item in monthly_revenue]
    monthly_totals = [float(item[1]) for item in monthly_revenue]

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Pie chart for category distribution
    wedges, texts, autotexts = ax1.pie(
        revenues,
        labels=categories,
        colors=NEUTRAL_PALETTE[:len(categories)],
        autopct=lambda p: f'{p:.1f}%\n(₹{p / 100. * sum(revenues):,.0f})',
        startangle=140,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
        textprops={'fontsize': 9}
    )

    ax1.set_title('Revenue by Category', pad=20, fontsize=12, weight='bold')

    # Line chart for monthly trends
    ax2.plot(
        months, monthly_totals,
        marker='o',
        color=NEUTRAL_PALETTE[0],
        linewidth=2,
        markersize=8
    )

    # Add value labels
    for month, total in zip(months, monthly_totals):
        ax2.text(
            month, total, f'₹{total:,.0f}',
            ha='center', va='bottom',
            fontsize=9, weight='bold'
        )

    ax2.set_title('Monthly Revenue Trend', pad=20, fontsize=12, weight='bold')
    ax2.set_xlabel('Month', labelpad=10)
    ax2.set_ylabel('Revenue (₹)', labelpad=10)
    ax2.set_xticks(months)
    ax2.grid(True, alpha=0.3)

    # Save chart
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.close()

    # Calculate analytics
    current_year_revenue = sum(revenues)
    prev_year_revenue = db.session.query(
        func.sum(OrderedProduct.order_amount)
    ).join(OrderDetails, OrderedProduct.order_details_id == OrderDetails.id) \
                            .filter(OrderDetails.order_date >= f'{prev_year}-01-01',
                                    OrderDetails.order_date <= f'{prev_year}-12-31') \
                            .scalar() or 0

    growth_rate = ((current_year_revenue - prev_year_revenue) / prev_year_revenue * 100) if prev_year_revenue else 0

    analytics = {
        "current_year": current_year,
        "prev_year": prev_year,
        "current_revenue": f"₹{current_year_revenue:,.2f}",
        "prev_revenue": f"₹{prev_year_revenue:,.2f}",
        "growth_rate": f"{growth_rate:.1f}%",
        "top_category": categories[0],
        "top_category_revenue": f"₹{revenues[0]:,.2f}",
        "monthly_trend": list(zip(months, monthly_totals))
    }

    return render_template(
        "revenue_trends.html",
        chart_data=chart_data,
        analytics=analytics,
        title='Revenue Analysis',
        side_title='Financial Performance'
    )


@visualization.route('/delivery_chart')
def delivery_chart():
    apply_style()

    # Query delivery performance data
    delivery_data = db.session.query(
        OrderDetails.status,
        func.count(OrderDetails.id).label('count'),
        func.avg(OrderDetails.delivered_date).label('avg_delivered_date')
    ).group_by(OrderDetails.status).all()

    # Prepare data
    statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    counts = {status: 0 for status in statuses}
    avg_times = {status: 0 for status in statuses}

    for status, count, avg_time in delivery_data:
        counts[status] = count
        avg_times[status] = avg_time if avg_time else 0

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Bar chart for status distribution
    bars = ax1.bar(
        statuses,
        [counts[status] for status in statuses],
        color=NEUTRAL_PALETTE[:len(statuses)],
        edgecolor='white',
        linewidth=1
    )

    ax1.set_title('Order Status Distribution', pad=20, fontsize=12, weight='bold')
    ax1.set_ylabel('Number of Orders', labelpad=10)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2., height,
            f'{height}',
            ha='center', va='bottom',
            fontsize=9, weight='bold'
        )

    # Line chart for average delivery time
    valid_statuses = [s for s in statuses if avg_times[s] > 0]
    valid_times = [avg_times[s] for s in valid_statuses]

    ax2.plot(
        valid_statuses, valid_times,
        marker='o',
        color=NEUTRAL_PALETTE[0],
        linewidth=2,
        markersize=8
    )

    ax2.set_title('Average Delivery Time', pad=20, fontsize=12, weight='bold')
    ax2.set_ylabel('Days', labelpad=10)

    # Add value labels
    for status, time in zip(valid_statuses, valid_times):
        ax2.text(
            status, time, f'{time:.1f}',
            ha='center', va='bottom',
            fontsize=9, weight='bold'
        )

    # Save chart
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.close()

    # Calculate analytics
    total_orders = sum(counts.values())
    delivered_percentage = (counts['Delivered'] / total_orders * 100) if total_orders else 0
    avg_delivered_date = avg_times['Delivered'] if 'Delivered' in avg_times else 0

    # Get recent orders
    recent_orders = db.session.query(
        OrderDetails.id,
        OrderDetails.user_name,
        OrderDetails.status,
        OrderDetails.order_date,
        OrderDetails.delivered_date
    ).order_by(OrderDetails.order_date.desc()).limit(5).all()

    analytics = {
        "total_orders": total_orders,
        "delivered_orders": counts['Delivered'],
        "delivered_percentage": f"{delivered_percentage:.1f}%",
        "avg_delivered_date": f"{avg_delivered_date:.1f} days",
        "recent_orders": recent_orders
    }

    return render_template(
        "delivery_chart.html",
        chart_data=chart_data,
        analytics=analytics,
        title='Delivery Performance',
        side_title='Logistics Analysis'
    )


# [Additional route functions with similar improvements...]

@visualization.route('/inventory_status')
def inventory_status():
    apply_style()

    # Query inventory data
    inventory_data = db.session.query(
        Product.category,
        func.sum(Product.quantity).label('total_quantity'),
        func.avg(Product.price).label('avg_price')
    ).group_by(Product.category).all()

    # Prepare data
    categories = [item[0] for item in inventory_data]
    quantities = [item[1] for item in inventory_data]
    avg_prices = [float(item[2]) if item[2] else 0 for item in inventory_data]

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Bar chart for inventory levels
    bars = ax1.bar(
        categories, quantities,
        color=NEUTRAL_PALETTE[:len(categories)],
        edgecolor='white',
        linewidth=1
    )

    ax1.set_title('Inventory Levels by Category', pad=20, fontsize=12, weight='bold')
    ax1.set_ylabel('Quantity', labelpad=10)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2., height,
            f'{height}',
            ha='center', va='bottom',
            fontsize=9, weight='bold'
        )

    # Scatter plot for value vs quantity
    scatter = ax2.scatter(
        quantities, avg_prices,
        s=[q * 10 for q in quantities],  # Size bubbles by quantity
        c=NEUTRAL_PALETTE[:len(categories)],
        alpha=0.7,
        edgecolors='white',
        linewidth=1
    )

    ax2.set_title('Inventory Value Analysis', pad=20, fontsize=12, weight='bold')
    ax2.set_xlabel('Quantity', labelpad=10)
    ax2.set_ylabel('Average Price (₹)', labelpad=10)

    # Add labels to bubbles
    for i, (category, q, p) in enumerate(zip(categories, quantities, avg_prices)):
        ax2.text(
            q, p, category,
            ha='center', va='center',
            fontsize=9
        )

    # Save chart
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.close()

    # Calculate analytics
    total_inventory = sum(quantities)
    low_stock = db.session.query(Product).filter(Product.quantity < 5).count()
    out_of_stock = db.session.query(Product).filter(Product.quantity == 0).count()

    analytics = {
        "total_inventory": total_inventory,
        "total_categories": len(categories),
        "low_stock_items": low_stock,
        "out_of_stock_items": out_of_stock,
        "highest_quantity_category": categories[quantities.index(max(quantities))],
        "highest_value_category": categories[avg_prices.index(max(avg_prices))]
    }

    return render_template(
        "inventory_status.html",
        chart_data=chart_data,
        analytics=analytics,
        title='Inventory Analysis',
        side_title='Stock Management'
    )