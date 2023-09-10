from django.test import TestCase
from artd_partner.models import Partner, Headquarter, Position, Coworker
from artd_location.models import Country, Region, City
from artd_partner.utils.generators import generate_random_string, generate_random_email

# Create your tests here.


class TestPartner(TestCase):
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

        self.position = Position.objects.create(name="Gerente")
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

    def test_position(self):
        assert Position.objects.count() == 1

    def test_partner(self):
        assert Partner.objects.count() == 1

    def test_headquarter(self):
        assert Headquarter.objects.count() == 1

    def test_coworker(self):
        assert Coworker.objects.count() == 1
