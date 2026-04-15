from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import * 
from knox.models import AuthToken
import random
from django.core.mail import send_mail
from django.core.cache import cache 


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        }, status=status.HTTP_201_CREATED)


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        # user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LogoutAPI(APIView):
    # Only authenticated users can access this endpoint
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete the token associated with the current user
            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out."}, 
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Something went wrong or token already deleted."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = str(random.randint(100000, 999999))
            
            # Store OTP in Redis for 10 minutes (600 seconds)
            cache.set(f"otp_{email}", otp, timeout=600)
            
            # Send Email
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP for password reset is: {otp}. It expires in 10 minutes.",
                from_email="noreply@yourschool.com",
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Delete OTP from Redis after successful reset
            cache.delete(f"otp_{email}")
            
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)