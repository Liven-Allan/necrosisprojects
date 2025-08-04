from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Image
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .utilities import process_image_v2
import os
from ultralytics import YOLO
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserSerializer, AnalysisSessionSerializer
from .models import User, AnalysisSession, CassavaImage
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.files.storage import default_storage
import zipfile
import io
from django.http import StreamingHttpResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


FIL_DIR = os.path.dirname((os.path.abspath(__file__)))
model_path = os.path.join(FIL_DIR, "../media/models/exp_new-Sep-24_yolov8n-seg_24-09-27_13_26/best.pt")
model = YOLO(model_path)


# Create your views here.
def index(request):
    # print(request.META['HTTP_HOST'])
    # print(request.get_host())
    print(request.build_absolute_uri())
    return HttpResponse("Hello World")


class ImageUploadAPIView(APIView):

    @csrf_exempt
    def post(self, request):
        image = request.FILES.get('image')

        if image:
            instance = Image(image=image)
            instance.save()
            print(instance.image.path)

            res = process_image_v2(instance.image.path, model)
            # print(len(res))
            print(res)
            out = {"percentage_necrosis": res[0], "lesion_count": res[2],
                   "image": f'{ request.scheme }://{ request.META["HTTP_HOST"]}/results/{res[1]}',
                   "necrosis_lesions": res[3]}

            return Response(
                {
                    "result": out,
                    "message": "Image submitted successfully",
                }, status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "message": "No image found in request",
                "status": "failed"
            }, status=status.HTTP_400_BAD_REQUEST
        )
    #
    # def get(self, request):
    #     images = Image.objects.all()
    #     serializer = ImageUploadSerializer(images, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

# View for browser-based image upload and result display
def upload_image_view(request):
    result = None
    message = ""
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        instance = Image(image=image)
        instance.save()
        res = process_image_v2(instance.image.path, model)
        result = {
            "percentage_necrosis": res[0],
            "lesion_count": res[2],
            "image": f"/media/results/{res[1]}"
        }
        message = "Image submitted successfully"
    return render(request, "upload.html", {"result": result, "message": message})

class AnalyzeImagesAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist('images')
        results = []
        import uuid
        from django.core.files.base import File
        session_id = request.data.get('session_id')
        session = None
        # Try to use existing session if provided and valid
        if session_id:
            try:
                session = AnalysisSession.objects.get(session_id=session_id, user=user)
            except AnalysisSession.DoesNotExist:
                session = None
        if session is None:
            # Create new session
            session_id = str(uuid.uuid4())
            session = AnalysisSession.objects.create(
                user=user,
                session_id=session_id,
                num_images=0,
            )
        # Add images to session
        for file in files:
            unique_name = f'{uuid.uuid4()}_{file.name}'
            upload_path = os.path.join('uploads/images/', unique_name)
            full_upload_path = os.path.join(default_storage.location, upload_path)
            with default_storage.open(upload_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            res = process_image_v2(full_upload_path, model)
            cassava_img = CassavaImage.objects.create(
                session=session,
                original_image=upload_path,
                processed_image=f'results/{res[1]}',
                image_name=file.name,
                total_lesions=res[2],
                necrosis_percentage=res[0],
                metadata={'necrosis_lesions': res[3]},
            )
            out = {
                "filename": file.name,
                "percentage_necrosis": res[0],
                "lesion_count": res[2],
                "result_image": f'{request.scheme}://{request.get_host()}/media/results/{res[1]}',
                "necrosis_lesions": res[3],
            }
            results.append(out)
        # Update session image count
        session.num_images = session.cassava_images.count()
        session.save()
        return Response({
            "results": results,
            "session_id": session.session_id,
            "created_at": session.created_at,
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """
    API endpoint for registering a new user (regular).
    Accepts: username, email, password, confirm_password
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):
    """
    API endpoint to fetch or update user details (email, contact, organisation) by email. Requires authentication.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
            return Response({
                'username': user.username,
                'email': user.email,
                'contact': user.contact,
                'organisation': user.organisation,
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, email):
        # Only allow the user to update their own profile
        if request.user.email != email:
            return Response({'error': 'You can only update your own profile.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteSessionImagesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # Get the latest session for the user
        session = AnalysisSession.objects.filter(user=user).order_by('-created_at').first()
        if not session:
            return Response({'message': 'No session found.'}, status=status.HTTP_404_NOT_FOUND)
        # Delete images for all CassavaImage in this session
        for img in session.cassava_images.all():
            if img.original_image:
                try:
                    default_storage.delete(img.original_image.path)
                except Exception:
                    pass
                img.original_image.delete(save=False)
            if img.processed_image:
                try:
                    default_storage.delete(img.processed_image.path)
                except Exception:
                    pass
                img.processed_image.delete(save=False)
            img.original_image = None
            img.processed_image = None
            img.save()
        return Response({'message': 'Images deleted, text results retained.'}, status=status.HTTP_200_OK)

class LatestSessionResultsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        session = AnalysisSession.objects.filter(user=user).order_by('-created_at').first()
        if not session:
            return Response({'results': []}, status=status.HTTP_200_OK)
        results = []
        for img in session.cassava_images.all():
            results.append({
                'filename': img.image_name,
                'percentage_necrosis': img.necrosis_percentage,
                'lesion_count': img.total_lesions,
                'result_image': None,  # No image returned
                'necrosis_lesions': img.metadata.get('necrosis_lesions') if img.metadata else None,
            })
        return Response({'results': results, 'session_id': session.session_id}, status=status.HTTP_200_OK)

class UserSessionsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sessions = AnalysisSession.objects.filter(user=user).order_by('-created_at')
        data = [
            {
                'session_id': s.session_id,
                'created_at': s.created_at,
                'num_images': s.num_images,
                'session_name': s.session_name,  # Added to persist custom session names
            }
            for s in sessions
        ]
        return Response({'sessions': data}, status=status.HTTP_200_OK)

class DeleteAnalysisSessionAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, session_id):
        user = request.user
        try:
            session = AnalysisSession.objects.get(session_id=session_id)
        except AnalysisSession.DoesNotExist:
            return Response({'detail': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
        if session.user != user:
            return Response({'detail': 'Not authorized to delete this session.'}, status=status.HTTP_403_FORBIDDEN)
        # Delete all related CassavaImage and AnalysisReport (should cascade, but ensure files are deleted)
        for img in session.cassava_images.all():
            if img.original_image:
                try:
                    default_storage.delete(img.original_image.path)
                except Exception:
                    pass
            if img.processed_image:
                try:
                    default_storage.delete(img.processed_image.path)
                except Exception:
                    pass
        # Delete the session (cascades to CassavaImage and AnalysisReport)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SessionResultsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        user = request.user
        try:
            session = AnalysisSession.objects.get(session_id=session_id, user=user)
        except AnalysisSession.DoesNotExist:
            return Response({'detail': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
        results = []
        for img in session.cassava_images.all():
            results.append({
                'filename': img.image_name,
                'percentage_necrosis': img.necrosis_percentage,
                'lesion_count': img.total_lesions,
                'result_image': None,  # No image returned
                'necrosis_lesions': img.metadata.get('necrosis_lesions') if img.metadata else None,
            })
        return Response({'results': results, 'session_id': session.session_id, 'created_at': session.created_at}, status=status.HTTP_200_OK)

class UpdateSessionNameAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, session_id):
        user = request.user
        try:
            session = AnalysisSession.objects.get(session_id=session_id, user=user)
        except AnalysisSession.DoesNotExist:
            return Response({'detail': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnalysisSessionSerializer(session, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DownloadSessionImagesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        user = request.user
        try:
            session = AnalysisSession.objects.get(session_id=session_id, user=user)
        except AnalysisSession.DoesNotExist:
            return Response({'detail': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
        images = session.cassava_images.all()
        if not images:
            return Response({'detail': 'No images found for this session.'}, status=status.HTTP_404_NOT_FOUND)
        # Create a zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img in images:
                if img.processed_image and img.processed_image.name:
                    img_path = img.processed_image.path
                    # Use the original uploaded image name for the zip entry
                    original_name = img.image_name or img.processed_image.name.split('/')[-1]
                    try:
                        with open(img_path, 'rb') as f:
                            zip_file.writestr(original_name, f.read())
                    except Exception:
                        continue
        zip_buffer.seek(0)
        response = StreamingHttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="session_{session_id}_images.zip"'
        return response

class EmailAuthTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'non_field_errors': ['Email and password are required.']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'non_field_errors': ['Invalid email or password.']}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=user.username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'non_field_errors': ['Invalid email or password.']}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        errors = {}
        if not email:
            errors['email'] = 'Email is required.'
        elif not User.objects.filter(email=email).exists():
            errors['email'] = 'No user with this email.'
        if not new_password:
            errors['new_password'] = 'New password is required.'
        elif len(new_password) < 8:
            errors['new_password'] = 'Password must be at least 8 characters.'
        elif not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
            errors['new_password'] = 'Password must contain letters and numbers.'
        if not confirm_password:
            errors['confirm_password'] = 'Please confirm your password.'
        elif new_password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
