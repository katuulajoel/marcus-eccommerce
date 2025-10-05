from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSerializer
)
from apps.customers.models import Customer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user

    Required fields:
    - username
    - email
    - password
    - password2
    - name
    - phone (optional)
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Send verification email
        try:
            customer = user.customer_profile
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{customer.email_verification_token}"

            send_mail(
                'Verify your email - Marcus Custom Cycles',
                f'Please click the link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send verification email: {e}")

        return Response({
            'message': 'User registered successfully. Please check your email to verify your account.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user and return JWT tokens

    Required fields:
    - username
    - password
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting the refresh token

    Required fields:
    - refresh (refresh token)
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email_view(request, token):
    """
    Verify user's email with token
    """
    try:
        customer = Customer.objects.get(email_verification_token=token)
        customer.email_verified = True
        customer.email_verification_token = None
        customer.save()

        return Response({
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({
            'error': 'Invalid verification token'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Request password reset email

    Required fields:
    - email
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            customer = user.customer_profile

            # Generate reset token
            token = customer.generate_password_reset_token()

            # Send reset email
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"

            send_mail(
                'Password Reset - Marcus Custom Cycles',
                f'Please click the link to reset your password: {reset_url}\n\nThis link will expire in 1 hour.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({
                'message': 'Password reset email sent. Please check your inbox.'
            }, status=status.HTTP_200_OK)
        except (User.DoesNotExist, Customer.DoesNotExist):
            # Don't reveal if email exists or not
            return Response({
                'message': 'If an account with this email exists, you will receive a password reset link.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            return Response({
                'error': 'Failed to send password reset email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset password with token

    Required fields:
    - token
    - password
    - password2
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        try:
            customer = Customer.objects.get(
                password_reset_token=token,
                password_reset_token_expires__gt=timezone.now()
            )

            # Reset password
            user = customer.user
            user.set_password(password)
            user.save()

            # Clear reset token
            customer.password_reset_token = None
            customer.password_reset_token_expires = None
            customer.save()

            return Response({
                'message': 'Password reset successfully'
            }, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({
                'error': 'Invalid or expired reset token'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current authenticated user details
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
