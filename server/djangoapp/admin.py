from django.contrib import admin
from .models import CarMake, CarModel


# Register CarMake model
@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_of_origin', 'founded_year')
    search_fields = ('name', 'description')
    list_filter = ('country_of_origin',)


# Register CarModel model
@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('car_make', 'name', 'year', 'type', 'dealer_id', 'is_available')
    list_filter = ('type', 'year', 'fuel_type', 'is_available')
    search_fields = ('name', 'car_make__name')
    autocomplete_fields = ('car_make',)  # Makes selecting CarMake easier

    # Optional: Organize fields in the detail view
    fieldsets = (
        (None, {
            'fields': ('car_make', 'name', 'dealer_id')
        }),
        ('Vehicle Details', {
            'fields': ('type', 'year', 'engine', 'fuel_type')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_available')
        }),
    )