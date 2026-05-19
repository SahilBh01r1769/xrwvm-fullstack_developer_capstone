from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import datetime
from .models import CarMake, CarModel
from .populate import initiate

# Get an instance of a logger
logger = logging.getLogger(__name__)


# ====================== AUTHENTICATION VIEWS ======================

@csrf_exempt
def login_user(request):
    """
    Handle user login via AJAX request and return JSON response.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('userName')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({
                    "status": "Error",
                    "message": "Username and password are required"
                }, status=400)

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({
                    "userName": username,
                    "status": "Authenticated"
                })
            else:
                return JsonResponse({
                    "status": "Error",
                    "message": "Invalid credentials"
                }, status=401)

        except json.JSONDecodeError:
            return JsonResponse({
                "status": "Error",
                "message": "Invalid JSON data"
            }, status=400)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return JsonResponse({
                "status": "Error",
                "message": "An error occurred during login"
            }, status=500)

    return JsonResponse({
        "status": "Error",
        "message": "Invalid request method"
    }, status=405)


@csrf_exempt
def logout_request(request):
    """Handle user logout - EXACT FORMAT REQUIRED BY LAB"""
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Must return empty username
    return JsonResponse(data)


# ====================== OTHER VIEWS ======================

@csrf_exempt
def registration(request):
    """Handle user registration via AJAX"""
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        username = data.get('userName')
        password = data.get('password')
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')
        email = data.get('email')

        # Basic validation
        if not all([username, password, email]):
            return JsonResponse({
                "error": "Username, password, and email are required"
            }, status=400)

        username_exist = False
        email_exist = False

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            username_exist = True

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            email_exist = True

        if username_exist:
            return JsonResponse({
                "userName": username,
                "error": "Already Registered"  # Keep as per lab requirement
            })

        if email_exist:
            return JsonResponse({
                "error": "Email already exists"
            }, status=409)

        # Create new user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        # Log the user in immediately after registration
        login(request, user)

        logger.info(f"New user registered: {username}")

        return JsonResponse({
            "userName": username,
            "status": "Authenticated"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({
            "error": "Registration failed. Please try again."
        }, status=500)


#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})


def get_dealer_reviews(request, dealer_id):
    if not dealer_id:
        return JsonResponse({"status": 400, "message": "Dealer ID is required"}, status=400)

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
        return JsonResponse({
            "status": 500,
            "message": "Failed to retrieve reviews"
        }, status=500)

def get_dealer_details(request, dealer_id):
    """
    Fetch dealer details by dealer_id from the backend service.
    """
    if not dealer_id:
        return JsonResponse({
            "status": 400,
            "message": "Bad Request: Dealer ID is required"
        }, status=400)

    try:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)

        if dealership:
            return JsonResponse({
                "status": 200,
                "dealer": dealership
            })
        else:
            return JsonResponse({
                "status": 404,
                "message": f"Dealer with ID {dealer_id} not found"
            }, status=404)

    except Exception as e:
        logger.error(f"Error fetching dealer details (ID: {dealer_id}): {str(e)}")
        return JsonResponse({
            "status": 500,
            "message": "Internal server error while fetching dealer details"
        }, status=500)

@csrf_exempt
def add_review(request):
    """
    Handle posting a new review for a dealer.
    Only authenticated users can post reviews.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": 403,
            "message": "Unauthorized: Please login to post a review"
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            "status": 405,
            "message": "Method not allowed"
        }, status=405)

    try:
        data = json.loads(request.body)

        # Optional: Add user information to the review data
        data['user_id'] = request.user.id
        data['user_name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username

        # Call the post request function
        response = post_request(data)        # Use post_request as per lab standard

        print("Review posting response:", response)  # For debugging

        return JsonResponse({
            "status": 200,
            "message": "Review posted successfully",
            "review": response
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "status": 400,
            "message": "Invalid JSON data"
        }, status=400)

    except Exception as e:
        logger.error(f"Error posting review: {str(e)}")
        return JsonResponse({
            "status": 500,
            "message": "Failed to post review. Please try again later."
        }, status=500)
def get_cars(request):
    print("=== get_cars called ===")

    make_count = CarMake.objects.count()
    model_count = CarModel.objects.count()
    print(f"Before initiate → CarMake: {make_count}, CarModel: {model_count}")

    # Force initiate if no data
    if make_count == 0 or model_count == 0:
        print("⚠️  No data found → Running initiate() now...")
        try:
            from .populate import initiate
            initiate()
            print("✅ initiate() executed successfully!")
        except Exception as e:
            print(f"❌ Error in initiate(): {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        print("✅ Data already exists.")

    # Refresh counts
    make_count = CarMake.objects.count()
    model_count = CarModel.objects.count()
    print(f"After initiate → CarMake: {make_count}, CarModel: {model_count}")

    # Fetch data
    car_models = CarModel.objects.select_related('car_make').all()

    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
            "Year": car_model.year,
            "Type": car_model.type,
        })

    print(f"Returning {len(cars)} cars")
    return JsonResponse({"CarModels": cars})
