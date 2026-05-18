from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import datetime

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

# def get_dealerships(request):
#     ...

# def get_dealer_reviews(request, dealer_id):
#     ...

# def get_dealer_details(request, dealer_id):
#     ...

# def add_review(request):
#     ...