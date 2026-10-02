"""
Application factory for the Flask app.
Registers blueprints for each module (user, product, cart, order, admin).
"""
import os
from flask import Flask, send_from_directory
from app.extensions import db, login_manager, cors
from app.modules.user.models import User
from app.modules.product.models import Product, Category
from app.modules.order.models import Order, OrderItem
from app.modules.cart.models import CartItem


def create_app(config_override=None):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path=""
    )
    app.config.from_object("app.config.Config")
    if config_override:
        app.config.update(config_override)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app, supports_credentials=True)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


    # Register blueprints
    from app.modules.user.routes import user_bp
    from app.modules.product.routes import product_bp
    from app.modules.cart.routes import cart_bp
    from app.modules.order.routes import order_bp
    from app.modules.admin.routes import admin_bp

    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(order_bp, url_prefix="/api/orders")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Serve static frontend pages
    @app.route("/")
    def index_page():
        return send_from_directory(os.path.join(frontend_dir, "pages"), "index.html")

    @app.route("/pages/<path:path>")
    def serve_pages(path):
        return send_from_directory(os.path.join(frontend_dir, "pages"), path)

    @app.route("/css/<path:path>")
    def serve_css(path):
        return send_from_directory(os.path.join(frontend_dir, "css"), path)

    @app.route("/js/<path:path>")
    def serve_js(path):
        return send_from_directory(os.path.join(frontend_dir, "js"), path)

    # Initialize database & seed data on startup
    with app.app_context():
        db.create_all()
        seed_database()

    return app


def seed_database():
    """Populate default seed data if database is empty."""
    cat_electronics = Category.query.filter_by(name="Electronics").first()
    if not cat_electronics:
        cat_electronics = Category(name="Electronics")
        db.session.add(cat_electronics)

    cat_clothing = Category.query.filter_by(name="Fashion & Clothing").first()
    if not cat_clothing:
        cat_clothing = Category(name="Fashion & Clothing")
        db.session.add(cat_clothing)

    cat_books = Category.query.filter_by(name="Books & Stationery").first()
    if not cat_books:
        cat_books = Category(name="Books & Stationery")
        db.session.add(cat_books)

    cat_home = Category.query.filter_by(name="Home & Living").first()
    if not cat_home:
        cat_home = Category(name="Home & Living")
        db.session.add(cat_home)

    db.session.commit()

    if Product.query.count() < 50:
        # Clear existing products to ensure clean, consistent 50 items
        Product.query.delete()
        db.session.commit()

        products_data = [
            # 1-13 Electronics
            {
                "name": "Wireless Ergonomic Mouse",
                "description": "High-precision 2.4GHz wireless optical mouse with ergonomic contour and whisper-quiet switches.",
                "price": 24.99,
                "stock_quantity": 45,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&auto=format&fit=crop"
            },
            {
                "name": "Noise-Canceling Headphones",
                "description": "Over-ear Bluetooth headphones with active hybrid noise cancellation and 30-hour battery life.",
                "price": 129.99,
                "stock_quantity": 25,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop"
            },
            {
                "name": "Mechanical Gaming Keyboard",
                "description": "RGB tactile mechanical keyboard with hot-swappable switches and aircraft-grade aluminum chassis.",
                "price": 79.99,
                "stock_quantity": 20,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&auto=format&fit=crop"
            },
            {
                "name": "Ultra-Wide 4K Gaming Monitor",
                "description": "34-inch curved IPS gaming display with 144Hz refresh rate and 1ms ultra-low response latency.",
                "price": 349.99,
                "stock_quantity": 12,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&auto=format&fit=crop"
            },
            {
                "name": "Portable Bluetooth Speaker",
                "description": "IPX7 waterproof rugged wireless speaker with 360-degree deep bass and 18-hour playback.",
                "price": 45.00,
                "stock_quantity": 35,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&auto=format&fit=crop"
            },
            {
                "name": "Smart Fitness Watch v4",
                "description": "Advanced health tracker featuring real-time heart rate, SpO2 sensor, sleep monitor, and GPS.",
                "price": 89.95,
                "stock_quantity": 30,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop"
            },
            {
                "name": "USB-C Dual Display Docking Station",
                "description": "12-in-1 multi-port hub with dual 4K HDMI, 100W Power Delivery, Gigabit Ethernet, and SD reader.",
                "price": 69.50,
                "stock_quantity": 40,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1544652478-6653e09f18a2?w=500&auto=format&fit=crop"
            },
            {
                "name": "High-Fidelity Studio Microphone",
                "description": "Cardioid condenser microphone with integrated pop filter and zero-latency audio monitoring.",
                "price": 119.00,
                "stock_quantity": 18,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop"
            },
            {
                "name": "1080p Full HD Pro Streaming Webcam",
                "description": "60fps wide-angle streaming camera with dual stereo microphones and autofocus facial tracking.",
                "price": 49.99,
                "stock_quantity": 50,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1588508065123-287b28e013da?w=500&auto=format&fit=crop"
            },
            {
                "name": "Fast Wireless Charging Pad",
                "description": "15W Qi-certified ultra-slim charging pad with intelligent heat dispersion and non-slip silicone.",
                "price": 19.99,
                "stock_quantity": 60,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1622445262464-84b14e0745b1?w=500&auto=format&fit=crop"
            },
            {
                "name": "20000mAh Power Delivery Power Bank",
                "description": "High-capacity external battery pack with 65W fast USB-C output suitable for laptops and tablets.",
                "price": 39.99,
                "stock_quantity": 45,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1609592426508-cc027993a57b?w=500&auto=format&fit=crop"
            },
            {
                "name": "Smart Home WiFi Security Camera",
                "description": "2K pan-tilt indoor security camera featuring motion detection alerts and infrared night vision.",
                "price": 54.50,
                "stock_quantity": 28,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=500&auto=format&fit=crop"
            },
            {
                "name": "True Wireless Earbuds with ANC",
                "description": "Compact wireless earbuds with active noise cancellation, ambient passthrough mode, and IPX5 rating.",
                "price": 59.00,
                "stock_quantity": 38,
                "category_id": cat_electronics.id,
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop"
            },

            # 14-26 Fashion & Clothing
            {
                "name": "Classic Denim Jacket",
                "description": "Timeless 100% heavyweight cotton denim jacket with reinforced button closure and modern taper.",
                "price": 59.95,
                "stock_quantity": 32,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=500&auto=format&fit=crop"
            },
            {
                "name": "Organic Cotton T-Shirt Pack",
                "description": "Pack of 3 breathable neutral color crewneck tees made from certified organic ring-spun cotton.",
                "price": 34.50,
                "stock_quantity": 55,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop"
            },
            {
                "name": "Urban Canvas Backpack",
                "description": "Water-resistant commuter backpack with reinforced leather accents and 15.6-inch laptop pocket.",
                "price": 49.99,
                "stock_quantity": 25,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop"
            },
            {
                "name": "Minimalist Leather Chronograph Watch",
                "description": "Brushed stainless steel timepiece with scratch-resistant sapphire crystal and Italian leather strap.",
                "price": 115.00,
                "stock_quantity": 16,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=500&auto=format&fit=crop"
            },
            {
                "name": "Waterproof Trail Running Shoes",
                "description": "All-terrain athletic shoes with Vibram lugged outsoles and responsive shock-absorbing midsoles.",
                "price": 88.00,
                "stock_quantity": 22,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop"
            },
            {
                "name": "Merino Wool Knit Sweater",
                "description": "Thermal regulating ultra-fine Australian merino wool sweater designed for lightweight comfort.",
                "price": 74.50,
                "stock_quantity": 19,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&auto=format&fit=crop"
            },
            {
                "name": "Slim-Fit Chino Pants",
                "description": "Stretch-cotton tailored casual trousers with stain-resistant weave and concealed zipper pocket.",
                "price": 44.95,
                "stock_quantity": 34,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500&auto=format&fit=crop"
            },
            {
                "name": "Polarized UV400 Aviator Sunglasses",
                "description": "Classic tear-drop metallic frame eyewear with anti-reflective polarized optical protection.",
                "price": 28.00,
                "stock_quantity": 42,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500&auto=format&fit=crop"
            },
            {
                "name": "Vintage Leather Bifold Wallet",
                "description": "Hand-stitched vegetable-tanned cowhide wallet with RFID-blocking security lining.",
                "price": 32.50,
                "stock_quantity": 50,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=500&auto=format&fit=crop"
            },
            {
                "name": "Breathable Athletic Joggers",
                "description": "Moisture-wicking technical fleece track pants with zippered ankle cuffs and elastic drawstring waistband.",
                "price": 38.00,
                "stock_quantity": 30,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=500&auto=format&fit=crop"
            },
            {
                "name": "Windproof All-Weather Trench Coat",
                "description": "Double-breasted stormproof coat with removable thermal vest liner and horn buttons.",
                "price": 120.00,
                "stock_quantity": 14,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=500&auto=format&fit=crop"
            },
            {
                "name": "Canvas Slip-On Sneakers",
                "description": "Minimalist vulcanized rubber skate sneakers with padded collar and cushioned insole.",
                "price": 42.00,
                "stock_quantity": 36,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500&auto=format&fit=crop"
            },
            {
                "name": "Genuine Full-Grain Leather Belt",
                "description": "Solid brass buckle with durable 1.5-inch full-grain leather strap engineered for longevity.",
                "price": 29.90,
                "stock_quantity": 48,
                "category_id": cat_clothing.id,
                "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop"
            },

            # 27-38 Books & Stationery
            {
                "name": "The Design of Everyday Things",
                "description": "Fundamental cognitive design manifesto by Don Norman on user experience and human-centered affordances.",
                "price": 18.99,
                "stock_quantity": 40,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop"
            },
            {
                "name": "Minimalist Hardcover Notebook",
                "description": "Numbered dot-grid journal bound in linen cloth with thick 120gsm fountain-pen safe paper.",
                "price": 14.50,
                "stock_quantity": 65,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=500&auto=format&fit=crop"
            },
            {
                "name": "Clean Code: Software Craftsmanship",
                "description": "Industry-standard handbook of agile software engineering and best refactoring principles by Robert C. Martin.",
                "price": 37.50,
                "stock_quantity": 25,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=500&auto=format&fit=crop"
            },
            {
                "name": "Brass Mechanical Drafting Pencil",
                "description": "Solid brass hexagonal mechanical drafting tool with knurled grip and 0.5mm precision lead mechanism.",
                "price": 22.00,
                "stock_quantity": 45,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1585336261026-77894a4c5a08?w=500&auto=format&fit=crop"
            },
            {
                "name": "Refillable Fountain Pen & Ink Set",
                "description": "Fine stainless-steel nib writing pen supplied with piston cartridge converter and rich black archival ink.",
                "price": 35.00,
                "stock_quantity": 30,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=500&auto=format&fit=crop"
            },
            {
                "name": "Atomic Habits by James Clear",
                "description": "Transformative practical framework for building constructive daily habits and breaking unwanted routines.",
                "price": 16.99,
                "stock_quantity": 55,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop"
            },
            {
                "name": "Executive Leather Desk Pad",
                "description": "36x18 inch smooth desk mat crafted with waterproof vegan leather providing ergonomic wrist resting.",
                "price": 29.95,
                "stock_quantity": 38,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=500&auto=format&fit=crop"
            },
            {
                "name": "Architectural Isometric Sketchbook",
                "description": "Heavyweight grid sketchbook featuring 60-degree isometric graph guides ideal for technical sketching.",
                "price": 19.50,
                "stock_quantity": 42,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=500&auto=format&fit=crop"
            },
            {
                "name": "Premium Calligraphy Brush Pen Set",
                "description": "Set of 6 flexible felt brush tips with pigment-rich waterproof black ink for lettering and illustration.",
                "price": 26.00,
                "stock_quantity": 35,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=500&auto=format&fit=crop"
            },
            {
                "name": "Deep Work by Cal Newport",
                "description": "Essential guide on focused success in a distracted world, emphasizing uninterrupted cognitive concentration.",
                "price": 17.50,
                "stock_quantity": 48,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop"
            },
            {
                "name": "Aluminum Ergonomic Book Stand",
                "description": "Foldable anodized aluminum document holder with adjustable dual reading angles and page clips.",
                "price": 24.99,
                "stock_quantity": 28,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?w=500&auto=format&fit=crop"
            },
            {
                "name": "Noise-Isolating Desk Reading Light",
                "description": "Clip-on warm LED book lamp with 3 color temperatures, stepless dimming, and rechargeable battery.",
                "price": 31.00,
                "stock_quantity": 52,
                "category_id": cat_books.id,
                "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&auto=format&fit=crop"
            },

            # 39-50 Home & Living
            {
                "name": "Smart Ceramic Coffee Mug",
                "description": "Temperature control ceramic mug that maintains your beverage at your selected heat level via app control.",
                "price": 89.00,
                "stock_quantity": 15,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&auto=format&fit=crop"
            },
            {
                "name": "Aroma Essential Oil Diffuser",
                "description": "Ultrasonic cool mist aromatherapy diffuser with 500ml reservoir, automatic shutoff, and 7 ambient LED lights.",
                "price": 29.99,
                "stock_quantity": 36,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1602928321679-560bb453f190?w=500&auto=format&fit=crop"
            },
            {
                "name": "Double-Walled French Press Coffee Maker",
                "description": "1000ml 18/10 stainless steel thermal coffee press with 4-level filtration system and cool-touch handle.",
                "price": 36.50,
                "stock_quantity": 25,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=500&auto=format&fit=crop"
            },
            {
                "name": "Memory Foam Ergonomic Seat Cushion",
                "description": "Orthopedic coccyx relief cushion with cooling gel layer and non-slip rubber bottom.",
                "price": 34.00,
                "stock_quantity": 40,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1580481077195-c3a821a5060f?w=500&auto=format&fit=crop"
            },
            {
                "name": "Minimalist Concrete Desk Organizer",
                "description": "Cast architectural concrete tray with modular compartments for stationary, phone, and keys.",
                "price": 21.50,
                "stock_quantity": 30,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?w=500&auto=format&fit=crop"
            },
            {
                "name": "Stainless Steel Insulated Water Flask",
                "description": "750ml vacuum insulated bottle keeping liquids icy cold for 24 hours or piping hot for 12 hours.",
                "price": 24.95,
                "stock_quantity": 48,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&auto=format&fit=crop"
            },
            {
                "name": "Bamboo Wood Bath & Vanity Tray",
                "description": "Water-resistant organic bamboo caddy with expandable arms and integrated wine glass / tablet holder.",
                "price": 27.00,
                "stock_quantity": 22,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500&auto=format&fit=crop"
            },
            {
                "name": "Dimmable LED Architect Desk Lamp",
                "description": "Adjustable multi-joint swing arm drafting lamp with eye-care diffuse illumination and USB output port.",
                "price": 48.00,
                "stock_quantity": 20,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1534349762230-e0cadf78f5da?w=500&auto=format&fit=crop"
            },
            {
                "name": "Cast Iron Pre-Seasoned Skillet 10-Inch",
                "description": "Heavy-duty cast iron pan with superior heat retention and natural non-stick seasoning.",
                "price": 39.99,
                "stock_quantity": 27,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=500&auto=format&fit=crop"
            },
            {
                "name": "Scandinavian Ceramic Vase Set",
                "description": "Set of 3 matte-finish minimalist ceramic decorative vases with modern geometric shapes.",
                "price": 32.00,
                "stock_quantity": 35,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=500&auto=format&fit=crop"
            },
            {
                "name": "Microfiber Hypoallergenic Throw Blanket",
                "description": "Plush double-sided fleece blanket offering lightweight thermal insulation and velvety texture.",
                "price": 28.50,
                "stock_quantity": 45,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=500&auto=format&fit=crop"
            },
            {
                "name": "Air Purifying HEPA Filter Machine",
                "description": "Three-stage True HEPA air filtration system capturing 99.97% of airborne pollen, dust, and smoke.",
                "price": 99.00,
                "stock_quantity": 18,
                "category_id": cat_home.id,
                "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500&auto=format&fit=crop"
            }
        ]

        for prod in products_data:
            db.session.add(Product(**prod))

        db.session.commit()

    if User.query.count() == 0:
        # Seed Customer
        user = User(name="Alex Johnson", phone="9876543210", email="user@example.com", role="customer")
        user.set_password("password123")
        db.session.add(user)

        # Seed Admin
        admin = User(name="Admin System", phone="9999999999", email="admin@example.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        db.session.commit()
