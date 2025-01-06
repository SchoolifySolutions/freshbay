from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from django.contrib.auth import get_user_model, authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import update_session_auth_hash
from .serializers import ChangePasswordSerializer, UserSerializer, FoodBankSerializer
from .models import CustomUser, FoodBank
from django.shortcuts import get_object_or_404

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        username = request.data.get('email')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Serialize department data
            
           

            return Response({
                'Email': username,
                'Id': user.id,
                'Username': user.username,
                'First Name': user.first_name,
                'Last Name': user.last_name,
                'access_token': str(refresh.access_token),
                'refresh': str(refresh),
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if user.check_password(serializer.data.get('old_password')):
            user.set_password(serializer.data.get('new_password'))
            user.save()
            update_session_auth_hash(request, user)
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})

import requests
def create_foodbanks(request):
    api_url = "https://controllerdata.lacity.org/id/v2mg-qsxf.json"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()  # Parse the JSON data from the API
        for item in data:
            # Create FoodBank objects in the database
            FoodBank.objects.create(
                name=item.get("name", None),
                street_address=item.get("street_address", None),
                city=item.get("city", None),
                state=item.get("state", None),
                zip_code=item.get("zip_code", None),
                county=item.get("county", None),
                phone=item.get("phone", None),
                description=item.get("description", None),
                resource_type=item.get("resource_type", None),
                web_link=item.get("web_link", {}).get("url", None),
                latitude=item.get("latitude", None),
                longitude=item.get("longitude", None)
            )
        # Return a success message as JSON response
        return JsonResponse({"message": "Data successfully saved to the database."}, status=200)
    else:
        # Return an error message as JSON response
        return JsonResponse({"error": f"Failed to fetch data: {response.status_code}"}, status=response.status_code)

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import FoodSource
from .serializers import FoodSourceSerializer

class FoodSourceCreateAPIView(generics.CreateAPIView):
    queryset = FoodSource.objects.all()
    serializer_class = FoodSourceSerializer
    permission_classes = [IsAuthenticated]  # Ensures that only authenticated users can create food sources

    def perform_create(self, serializer):
        # Automatically set the owner to the current user
        serializer.save(owner=self.request.user)


from rest_framework.pagination import PageNumberPagination
class MarkerPagination(PageNumberPagination):
    page_size = 100  # Return 10 markers per page


class AllFoodBanksView(APIView):
    def get(self, request):
        # Query the database to get all foodbanks
        foodbanks = FoodBank.objects.all()

        # Create a paginator instance
        paginator = MarkerPagination()

        # Paginate the queryset
        result_page = paginator.paginate_queryset(foodbanks, request)

        # Serialize the paginated data
        serializer = FoodBankSerializer(result_page, many=True)

        # Return the paginated response with the serialized data
        return paginator.get_paginated_response(serializer.data)


class FoodSourceCreateView(APIView):
    def post(self, request):
        # Define the Geoapify API URL with your API key and parameters
        url = "https://api.geoapify.com/v2/places?categories=catering.restaurant,commercial.food_and_drink,catering.fast_food,catering.food_court&filter=rect:-131.79757822774695,43.46362686555679,-116.41427752962585,32.73770429604316&limit=200&apiKey=4fa11476db874a3e9dbc3b0fe029f8a9"
        
        # Make the request to the Geoapify API
        response = requests.get(url)
        
        # Check if the Geoapify API request was successful
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            
            # Loop through the data returned by Geoapify API and create FoodSource objects
            for result in data.get('features', []):
                name = result.get('properties', {}).get('name', '')
                address = result.get('properties', {}).get('address', '')
                latitude = result.get('geometry', {}).get('coordinates', [])[1]
                longitude = result.get('geometry', {}).get('coordinates', [])[0]
                source_type = 'RESTAURANT'  # You can customize this depending on the type of source
                
                # Assuming contact_email and contact_phone are optional, set them to empty strings for now
                contact_email = ''
                contact_phone = ''
                
                # Create and save the FoodSource object
                food_source = FoodSource(
                    name=name,
                    address=address,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    latitude=latitude,
                    longitude=longitude,
                    source_type=source_type
                )
                food_source.save()  # Save to the database

            return Response({"message": "Successfully fetched and created FoodSource objects."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to fetch data from Geoapify API."}, status=status.HTTP_400_BAD_REQUEST)
        
class AllFoodSources(APIView):
    permission_classes=[AllowAny]
    
    def get(self, request):
        foodsources = FoodSource.objects.all()
        
        # Ensure invalid latitude and longitude values are set to None or 0.0
        for foodsource in foodsources:
            if foodsource.latitude == '':
                foodsource.latitude = None  # Or set to 0.0 if that's more appropriate
            if foodsource.longitude == '':
                foodsource.longitude = None  # Or set to 0.0 if that's more appropriate
        
        serializer = FoodSourceSerializer(foodsources, many=True)
        return Response(serializer.data)