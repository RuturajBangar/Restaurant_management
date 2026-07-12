from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from restaurant.models import Category, MenuItem, Table, Customer, StaffProfile


class Command(BaseCommand):
    help = 'Populates the database with sample restaurant data for testing.'

    def handle(self, *args, **options):
        # Staff user (skip if already exists)
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            StaffProfile.objects.create(user=admin, role='manager', phone='555-0100')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))

        # Categories & menu items
        starters, _ = Category.objects.get_or_create(name='Starters')
        mains, _ = Category.objects.get_or_create(name='Main Course')
        desserts, _ = Category.objects.get_or_create(name='Desserts')
        drinks, _ = Category.objects.get_or_create(name='Beverages')

        items = [
            (starters, 'Garlic Bread', 5.99, 'Toasted bread with garlic butter'),
            (starters, 'Bruschetta', 6.99, 'Tomato, basil, and olive oil on toast'),
            (mains, 'Margherita Pizza', 12.99, 'Classic tomato, mozzarella, basil'),
            (mains, 'Grilled Chicken', 14.99, 'Served with roasted vegetables'),
            (mains, 'Spaghetti Carbonara', 13.49, 'Pasta with egg, pancetta, parmesan'),
            (desserts, 'Tiramisu', 6.49, 'Classic Italian coffee dessert'),
            (desserts, 'Chocolate Lava Cake', 7.49, 'Warm cake with molten center'),
            (drinks, 'Sparkling Water', 2.99, ''),
            (drinks, 'Fresh Lemonade', 3.99, ''),
        ]
        for category, name, price, desc in items:
            MenuItem.objects.get_or_create(
                name=name, category=category,
                defaults={'price': price, 'description': desc},
            )

        # Tables
        for num, cap in [(1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 8)]:
            Table.objects.get_or_create(number=num, defaults={'capacity': cap})

        # Sample customer
        Customer.objects.get_or_create(
            name='John Doe', defaults={'phone': '555-1234', 'email': 'john@example.com'}
        )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully.'))
