import os
from csv import reader

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Ingredient

DATA = [
    (Ingredient, 'ingredients.csv'),
]


class Command(BaseCommand):
    """Импорт данных из csv-файлов"""

    help = ('Чтобы запустить импорт данных из csv-файлов, '
            'выполните команду "python manage.py load_csv".')

    def handle(self, *args, **kwargs):
        for model, filename in DATA:
            file = os.path.join(settings.BASE_DIR, 'data', filename)
            with open(file, 'r', encoding='utf-8') as csv_file:
                for row in reader(csv_file):
                    try:
                        if model == Ingredient:
                            model.objects.get_or_create(
                                name=row[0],
                                measurement_unit=row[1]
                            )
                    except ValueError as error:
                        self.stdout.write(self.style.ERROR(
                            'Ошибка при загрузке данных'
                            f'для модели "{model.__name__}": {error}'
                        ))
                self.stdout.write(self.style.SUCCESS(
                    f'Данные для модели "{model.__name__}" успешно загружены'
                ))
