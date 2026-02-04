"""
Management command to update search vectors for all inventory products.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from inventario.models import ChemicalProduct, Pipe, PumpAndMotor, Accessory


class Command(BaseCommand):
    help = 'Update search vectors for all inventory products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['chemical', 'pipe', 'pump', 'accessory', 'all'],
            default='all',
            help='Specify which model to update (default: all)'
        )

    def handle(self, *args, **options):
        model_choice = options['model']
        
        models_to_update = []
        if model_choice == 'all':
            models_to_update = [ChemicalProduct, Pipe, PumpAndMotor, Accessory]
        elif model_choice == 'chemical':
            models_to_update = [ChemicalProduct]
        elif model_choice == 'pipe':
            models_to_update = [Pipe]
        elif model_choice == 'pump':
            models_to_update = [PumpAndMotor]
        elif model_choice == 'accessory':
            models_to_update = [Accessory]

        total_updated = 0
        
        for model_class in models_to_update:
            self.stdout.write(f'Updating search vectors for {model_class.__name__}...')
            
            with transaction.atomic():
                products = model_class.objects.all()
                count = 0
                
                for product in products:
                    try:
                        product.update_search_vector()
                        count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error updating {product.sku}: {str(e)}'
                            )
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated {count} {model_class.__name__} records'
                    )
                )
                total_updated += count
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Total records updated: {total_updated}'
            )
        )