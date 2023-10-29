import os
from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Ingredient, Tag

DATA = [
    (Ingredient, 'ingredients.csv'),
    (Tag, 'tags.csv'),
]


class Command(BaseCommand):
    """Импорт данных из csv-файлов"""

    help = ('Чтобы запустить импорт данных из csv-файлов, '
            'выполните команду "python manage.py load_csv".')

    def handle(self, *args, **kwargs):
        for model, filename in DATA:
            try:
                file = os.path.join(settings.BASE_DIR, 'data', filename)
                with open(file, 'r', encoding='utf-8') as csv_file:
                    for data in DictReader(csv_file):
                        try:
                            model.objects.get_or_create(**data)
                        except ValueError as error:
                            self.stdout.write(self.style.ERROR(
                                'Ошибка при загрузке данных'
                                f'для модели "{model.__name__}": {error}'
                            ))
                    self.stdout.write(self.style.SUCCESS(
                        f'Данные для модели "{model.__name__}" '
                        f'успешно загружены'
                    ))
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(
                    f'Файл "{filename}" не найден'
                ))
