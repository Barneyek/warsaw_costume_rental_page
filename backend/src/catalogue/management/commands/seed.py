from django.core.management.base import BaseCommand
from src.catalogue.models import Category, Tag, Size, Costume


class Command(BaseCommand):
    help = 'Wypełnia bazę danych testowymi danymi'

    def handle(self, *args, **kwargs):
        self.stdout.write('Czyszczę stare dane...')
        Costume.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Size.objects.all().delete()

        self.stdout.write('Tworzę kategorie...')

        # --- Kostiumy dla dorosłych ---
        adults = Category.objects.create(name='Kostiumy dla dorosłych', slug='kostiumy-dla-doroslych')

        antyk_a = Category.objects.create(name='Antyk', slug='antyk-doroslych', parent_category=adults)
        jaselka_a = Category.objects.create(name='Jasełka', slug='jaselka-doroslych', parent_category=adults)
        bajki_a = Category.objects.create(name='Bajki', slug='bajki-doroslych', parent_category=adults)
        halloween_a = Category.objects.create(name='Halloween', slug='halloween-doroslych', parent_category=adults)
        super_a = Category.objects.create(name='Superbohaterowie', slug='superbohaterowie-doroslych', parent_category=adults)
        zwierzaki_a = Category.objects.create(name='Zwierzaki', slug='zwierzaki-doroslych', parent_category=adults)
        swiat_a = Category.objects.create(name='Z różnych stron świata', slug='swiat-doroslych', parent_category=adults)
        ludowo_a = Category.objects.create(name='Na ludowo', slug='ludowo-doroslych', parent_category=adults)
        zawody_a = Category.objects.create(name='Zawody', slug='zawody-doroslych', parent_category=adults)
        piraci_a = Category.objects.create(name='Piraci', slug='piraci-doroslych', parent_category=adults)
        lata20_a = Category.objects.create(name='Lata XX-te', slug='lata-20-doroslych', parent_category=adults)
        lata60_a = Category.objects.create(name='Lata 60-te, 70-te i 80-te', slug='lata-60-doroslych', parent_category=adults)
        mikolaj_a = Category.objects.create(name='Mikołaj', slug='mikolaj-doroslych', parent_category=adults)
        owoce_a = Category.objects.create(name='Owoce i warzywa', slug='owoce-doroslych', parent_category=adults)

        historyczne_a = Category.objects.create(name='Kostiumy Historyczne', slug='historyczne-doroslych', parent_category=adults)
        Category.objects.create(name='Średniowiecze i renesans', slug='sredniowiecze-doroslych', parent_category=historyczne_a)
        Category.objects.create(name='XIX wiek', slug='xix-wiek-doroslych', parent_category=historyczne_a)
        Category.objects.create(name='Empire', slug='empire-doroslych', parent_category=historyczne_a)
        Category.objects.create(name='Kontusze Szlacheckie', slug='kontusze-doroslych', parent_category=historyczne_a)
        Category.objects.create(name='XVII i XVIII wiek', slug='xvii-xviii-doroslych', parent_category=historyczne_a)

        # --- Kostiumy dla dzieci ---
        kids = Category.objects.create(name='Kostiumy dla dzieci', slug='kostiumy-dla-dzieci')

        Category.objects.create(name='Zwierzaki', slug='zwierzaki-dzieci', parent_category=kids)
        Category.objects.create(name='Superbohaterowie', slug='superbohaterowie-dzieci', parent_category=kids)
        Category.objects.create(name='Bajki', slug='bajki-dzieci', parent_category=kids)
        Category.objects.create(name='Halloween', slug='halloween-dzieci', parent_category=kids)
        Category.objects.create(name='Jasełka', slug='jaselka-dzieci', parent_category=kids)
        Category.objects.create(name='Z różnych stron świata', slug='swiat-dzieci', parent_category=kids)
        Category.objects.create(name='Piraci', slug='piraci-dzieci', parent_category=kids)
        Category.objects.create(name='Na ludowo', slug='ludowo-dzieci', parent_category=kids)
        Category.objects.create(name='Inne', slug='inne-dzieci', parent_category=kids)
        Category.objects.create(name='Antyk', slug='antyk-dzieci', parent_category=kids)

        historyczne_k = Category.objects.create(name='Kostiumy Historyczne', slug='historyczne-dzieci', parent_category=kids)
        Category.objects.create(name='XIX wiek', slug='xix-wiek-dzieci', parent_category=historyczne_k)
        Category.objects.create(name='XVII i XVIII wiek', slug='xvii-xviii-dzieci', parent_category=historyczne_k)
        Category.objects.create(name='Średniowiecze i renesans', slug='sredniowiecze-dzieci', parent_category=historyczne_k)
        Category.objects.create(name='XX wiek', slug='xx-wiek-dzieci', parent_category=historyczne_k)

        # --- Tagi ---
        self.stdout.write('Tworzę tagi...')
        halloween_tag = Tag.objects.create(name='Halloween')
        bajki_tag = Tag.objects.create(name='Bajki')
        historyczny_tag = Tag.objects.create(name='Historyczny')

        # --- Rozmiary ---
        self.stdout.write('Tworzę rozmiary...')
        rozmiary = []
        for nazwa in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
            rozmiary.append(Size.objects.create(name=nazwa))

        # --- Kostiumy (kilka przykładowych) ---
        self.stdout.write('Tworzę kostiumy...')

        batman = Costume.objects.create(
            name='Strój Batman',
            slug='stroj-batman',
            description='Klasyczny strój Batmana dla dorosłych.',
            price='49.99',
            deposit='100.00',
        )
        batman.categories.set([super_a])
        batman.tags.set([bajki_tag])
        batman.sizes.set(rozmiary)

        czarownica = Costume.objects.create(
            name='Strój Czarownicy',
            slug='stroj-czarownicy',
            description='Czarna suknia z kapeluszem. Idealna na Halloween.',
            price='39.99',
            deposit='80.00',
        )
        czarownica.categories.set([halloween_a])
        czarownica.tags.set([halloween_tag])
        czarownica.sizes.set([rozmiary[1], rozmiary[2], rozmiary[3]])

        rycerz = Costume.objects.create(
            name='Strój Rycerza',
            slug='stroj-rycerza',
            description='Zbroja rycerska z epoki średniowiecza.',
            price='69.99',
            deposit='150.00',
        )
        rycerz.categories.set([historyczne_a])
        rycerz.tags.set([historyczny_tag])
        rycerz.sizes.set([rozmiary[2], rozmiary[3], rozmiary[4]])

        self.stdout.write(self.style.SUCCESS('Gotowe! Baza wypełniona danymi testowymi.'))