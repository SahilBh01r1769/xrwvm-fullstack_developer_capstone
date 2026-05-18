from .models import CarMake, CarModel

def initiate():
    print("Starting data population...")

    # Create Car Makes using get_or_create to avoid duplicates
    car_makes = [
        {"name": "Toyota", "description": "Japanese multinational automotive manufacturer", "country_of_origin": "Japan"},
        {"name": "Honda", "description": "Japanese public multinational conglomerate", "country_of_origin": "Japan"},
        {"name": "Ford", "description": "American multinational auto manufacturer", "country_of_origin": "USA"},
        {"name": "BMW", "description": "German multinational manufacturer of luxury vehicles", "country_of_origin": "Germany"},
    ]

    makes_dict = {}
    for make_data in car_makes:
        make, created = CarMake.objects.get_or_create(
            name=make_data["name"],
            defaults=make_data
        )
        makes_dict[make.name] = make
        if created:
            print(f"Created CarMake: {make.name}")
        else:
            print(f"CarMake already exists: {make.name}")

    # Create Car Models
    if CarModel.objects.count() == 0:
        print("Creating Car Models...")

        CarModel.objects.create(
            car_make=makes_dict["Toyota"], dealer_id=1, name="Camry", 
            type="Sedan", year=2020, price=25000, fuel_type="Petrol"
        )
        CarModel.objects.create(
            car_make=makes_dict["Toyota"], dealer_id=1, name="RAV4", 
            type="SUV", year=2021, price=32000, fuel_type="Hybrid"
        )
        CarModel.objects.create(
            car_make=makes_dict["Honda"], dealer_id=2, name="Civic", 
            type="Sedan", year=2019, price=22000, fuel_type="Petrol"
        )
        CarModel.objects.create(
            car_make=makes_dict["Ford"], dealer_id=3, name="Mustang", 
            type="Coupe", year=2022, price=45000, fuel_type="Petrol"
        )
        CarModel.objects.create(
            car_make=makes_dict["BMW"], dealer_id=4, name="X5", 
            type="SUV", year=2021, price=65000, fuel_type="Petrol"
        )
        print("Car Models created successfully!")
    else:
        print("Car Models already exist.")

    print("Data population completed!")