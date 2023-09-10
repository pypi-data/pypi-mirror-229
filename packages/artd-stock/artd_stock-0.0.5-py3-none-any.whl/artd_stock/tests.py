from django.test import TestCase
from artd_stock.models import Stock, StockLog
from artd_stock.utils.generators import (
    generate_random_string,
    generate_random_email,
    generate_random_decimal,
    generate_random_date,
)
from artd_partner.models import Partner, Headquarter, Coworker, Position
from artd_product.models import Product
from artd_location.models import City, Country, Region
from artd_product.models import Tax, Brand, RootCategory, Category, Product
from artd_product.data.taxes import TAXES


class TestPriceList(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            spanish_name=generate_random_string(),
            english_name=generate_random_string(),
            nom=generate_random_string(),
            iso2=generate_random_string(),
            phone_code=generate_random_string(),
        )
        self.region = Region.objects.create(
            name=generate_random_string(),
            country=self.country,
        )
        self.city = City.objects.create(
            name=generate_random_string(),
            name_in_capital_letters=generate_random_string(),
            code=generate_random_string(),
            region=self.region,
        )
        for tax in TAXES:
            Tax.objects.create(
                name=tax[0],
                percentage=tax[1],
            )
        self.tax = Tax.objects.first()
        self.brand = Brand.objects.create(
            name="Test Brand",
            status=True,
            url_key="test-brand",
            meta_title="Test Brand",
            meta_description="Test Brand",
            meta_keywords="Test Brand",
        )
        self.root_category = RootCategory.objects.create(
            name="Test Root Category",
            status=True,
            url_key="test-root-category",
            meta_title="Test Root Category",
            meta_description="Test Root Category",
            meta_keywords="Test Root Category",
        )
        self.category = Category.objects.create(
            name="Test Category",
            status=True,
            url_key="test-category",
            meta_title="Test Category",
            meta_description="Test Category",
            meta_keywords="Test Category",
            root_category=self.root_category,
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="test-product",
            description="Test Product",
            short_description="Test Product",
            url_key="test-product",
            meta_title="Test Product",
            meta_description="Test Product",
            meta_keywords="Test Product",
            brand=self.brand,
            tax=self.tax,
        )
        self.product.categories.add(self.category)
        self.position = Position.objects.create(
            name="Gerente",
        )
        self.partner = Partner.objects.create(
            name=generate_random_string(),
            dni=generate_random_string(),
            email=generate_random_email(),
            city=self.city,
            address=generate_random_string(),
        )
        self.headquarter = Headquarter.objects.create(
            name=generate_random_string(),
            address=generate_random_email(),
            city=self.city,
            phone=generate_random_string(),
            partner=self.partner,
        )
        self.coworker = Coworker.objects.create(
            first_name=generate_random_string(),
            last_name=generate_random_string(),
            dni=generate_random_string(),
            email=generate_random_email(),
            position=self.position,
            headquarter=self.headquarter,
        )

        Stock.objects.create(
            partner=self.partner,
            product=self.product,
            stock=generate_random_decimal(),
            stock_min=generate_random_decimal(),
            stock_max=generate_random_decimal(),
        )

    def test_price_list(self):
        assert Stock.objects.count() == 1

    def test_price_list_log(self):
        assert StockLog.objects.count() == 1
