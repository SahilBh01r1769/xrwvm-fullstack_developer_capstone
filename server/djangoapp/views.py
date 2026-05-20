from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
import json
import logging

# ✅ Correct Imports from restapis
from .restapis import get_request, analyze_review_sentiments, post_review

from .models import CarMake, CarModel
from .populate import initiate

# Get an instance of a logger
logger = logging.getLogger(__name__)


# ====================== AUTHENTICATION VIEWS ======================

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('userName')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"status": "Error", "message": "Username and password are required"}, status=400)

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username, "status": "Authenticated"})
            else:
                return JsonResponse({"status": "Error", "message": "Invalid credentials"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"status": "Error", "message": "Invalid JSON data"}, status=400)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return JsonResponse({"status": "Error", "message": "An error occurred during login"}, status=500)

    return JsonResponse({"status": "Error", "message": "Invalid request method"}, status=405)


@csrf_exempt
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})


# ====================== REGISTRATION ======================

@csrf_exempt
def registration(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')
        email = data.get('email')

        if not all([username, password, email]):
            return JsonResponse({"error": "Username, password, and email are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"userName": username, "error": "Already Registered"})

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=409)

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        login(request, user)

        return JsonResponse({"userName": username, "status": "Authenticated"})

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({"error": "Registration failed"}, status=500)


# ====================== DEALERSHIP VIEWS ======================

def get_dealerships(request, state="All"):
    try:
        if state == "All" or state.lower() == "all":
            endpoint = "/fetchDealers"
        else:
            endpoint = f"/fetchDealers/{state}"

        dealerships = get_request(endpoint)

        return JsonResponse({
            "status": 200,
            "dealers": dealerships if dealerships else []
        })
    except Exception as e:
        logger.error(f"Error in get_dealerships: {str(e)}")
        return JsonResponse({
            "status": 500,
            "dealers": [],
            "message": str(e)
        }, status=500)    

def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f"/fetchReviews/dealer/{dealer_id}")

        if reviews:
            for review in reviews:
                try:
                    sentiment = analyze_review_sentiments(review.get('review', ''))
                    review['sentiment'] = sentiment.get('sentiment', 'neutral')
                except:
                    review['sentiment'] = 'neutral'

        return JsonResponse({
            "status": 200,
            "reviews": reviews or []
        })

    except Exception as e:
        logger.exception(f"Failed to fetch reviews for dealer {dealer_id}")
        return JsonResponse({"status": 500, "message": "Failed to retrieve reviews"}, status=500)


def get_dealer_details(request, dealer_id):
    try:
        dealership = get_request(f"/fetchDealer/{dealer_id}")

        if dealership:
            return JsonResponse({"status": 200, "dealer": dealership})
        else:
            return JsonResponse({
                "status": 404,
                "message": f"Dealer with ID {dealer_id} not found"
            }, status=404)

    except Exception as e:
        logger.error(f"Error fetching dealer details: {str(e)}")
        return JsonResponse({"status": 500, "message": "Internal server error"}, status=500)


@csrf_exempt
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 403, "message": "Please login to post a review"}, status=403)

    if request.method != 'POST':
        return JsonResponse({"status": 405, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        # Add reviewer name
        data['name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username

        response = post_review(data)

        return JsonResponse({
            "status": 200,
            "message": "Review posted successfully",
            "review": response
        })

    except Exception as e:
        logger.error(f"Error posting review: {str(e)}")
        return JsonResponse({"status": 500, "message": "Failed to post review"}, status=500)


# ====================== CAR MODELS ======================

def get_cars(request):
    try:
        if CarModel.objects.count() == 0:
            initiate()

        car_models = CarModel.objects.select_related('car_make').all()

        cars = [{
            "CarModel": model.name,
            "CarMake": model.car_make.name,
            "Year": model.year,
            "Type": model.type,
        } for model in car_models]

        return JsonResponse({"CarModels": cars})

    except Exception as e:
        logger.error(f"Error in get_cars: {str(e)}")
        return JsonResponse({"error": "Failed to fetch cars"}, status=500)