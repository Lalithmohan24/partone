'''
Video streaming entire api endpoint functions are occured in this screen use to this function.
Easy user to register, login, logout authentication functionality.
Easy to Create, update, delete and retrieves the videos.
'''
import logging
import threading
from datetime import datetime
import cv2
import pytz
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.permissions import AllowAny
from utils import json
from .forms import RegisterForm, VideoForm
from .serializers import VideoSerializer
from .models import Video

logger = logging.getLogger( __name__ )

now = datetime.now(pytz.timezone('UTC'))
current_date = now.date()
current_time = now.time()

#User login view
def login_view(request):
    '''
    Login page get the forms and post the forms data functions
    '''
    errors = None
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                # Perform any additional actions after successful login
                token_key = user.auth_token.key
                request.session['token'] = token_key
                logger.info(f"{current_date} {current_time} : Login page Successed")
                return redirect('video_stream')

            if not form.is_valid():
                errors = form.errors.as_json()
        else:
            form = AuthenticationForm()
        return render(request, 'login.html', {'form': form, 'error_msg': errors})

    except Exception as err_msg:
        logger.info(f"{current_date} {current_time} : {err_msg}: Failed Login page")

#register page view
def register_view(request):
    '''
    Register page functions
    '''
    error_msg = None
    try:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password1 = form.cleaned_data['password']
                password2 = form.cleaned_data['confirm_password']
                if len(password1) < 8:
                    error_msg = "minimum 8 characters are allows the password"
                    return render(
                        request, 'register.html',
                        {'form': form, 'error_msg': error_msg})
                if password1 == password2:
                    user = User.objects.create_user(
                        username=username, password=password1)
                    token = Token.objects.create(user=user)
                    logger.info(
                        f"{current_date} {current_time} : Registration Successed")
                    return redirect('login')
                if password1 != password2:
                    error_msg = "confirm password not match"
            if not form.is_valid():
                error_msg = form.errors.as_json()
        if request.method == 'GET':
            form = RegisterForm()

        return render(
            request, 'register.html', {'form': form, 'error_msg': error_msg})
    except Exception as err_msg:
        logger.info(
            f"{current_date} {current_time} : {err_msg}: Failed Registration page")

#user logout function
@login_required
def logout_view(request):
    # Clear the session
    logout(request)
    return redirect('login')

#video stream multi-thread functionality and opencv to convert the video frame by frame
class VideoStreamer(threading.Thread):
    '''
    video streamming multiple thread functions
    '''
    def __init__(self, video_path):
        '''
        initialize the video stream objects
        '''
        super(VideoStreamer, self).__init__()
        self.video_path = video_path
        self.stop_event = threading.Event()

    def generate_frames(self):
        '''
        using opencv to convert the video frame by frame
        '''
        try:
            cap = cv2.VideoCapture(self.video_path)
            while cap.isOpened() and not self.stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break
                # Convert the frame to JPEG format
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                # Yield the frame as a response
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            cap.release()
            logger.info(f"{current_date} {current_time} : videostream multithread init Successed")
        except Exception as err_msg:
            logger.info(
                f"{current_date} {current_time} : {err_msg}: Failed Video stream multithread init")
    def stop(self):
        '''
        stop the event
        '''
        self.stop_event.set()

#shows the list of videos created
@login_required
def video_stream(request):
    '''
    get the list of streaming videos 
    '''
    try:
        search_query = request.GET.get('search')
        user_id = request.user.id
        if search_query:
            videos = Video.objects.filter(name__icontains=search_query, user_id=user_id)
        else:
            videos = Video.objects.filter(user_id=user_id)
        videos_list = []
        for video in videos:
            value = {
                'id': video.id,
                'name': video.name,
                'path': video.path
            }
            videos_list.append(value)
        logger.info(f"{current_date} {current_time} : videos list shows Successed")
        return render(request, 'video_stream.html', {'videos': videos_list})
    except Exception as err_msg:
        logger.info(
            f"{current_date} {current_time} : {err_msg}: Failed videostream list page")

#stream the video if users clicks the videos name
@login_required
def start_stream(request, video_path):
    '''
    start the video stream
    '''
    try:
        video_streamer = VideoStreamer(video_path)
        video_streamer.start()

        def stream():
            '''
            stream will get the generated frames each videos then stream.
            each video each thread
            '''
            for frame in video_streamer.generate_frames():
                yield frame
                if video_streamer.stop_event.is_set():
                    break

        response = StreamingHttpResponse(
            stream(), content_type='multipart/x-mixed-replace; boundary=frame')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        logger.info(f"{current_date} {current_time} : Start stream Successed")
        return response
    except Exception as err_msg:
        logger.info(
            f"{current_date} {current_time} : {err_msg}: Failed to Stream the video")

#users create the videos name and videos path
@login_required  # Ensure the user is authenticated
def create_video(request):
    '''
    Users can Create the streaming videos
    '''
    error_msg = None
    try:
        if request.method == 'POST':
            form = VideoForm(request.POST)
            if form.is_valid():
                video = form.save(commit=False)
                video.user = request.user # Set the current user as the video owner
                video.save()
                logger.info(
                    f"{current_date} {current_time} : create video Successed")
                return redirect('video_stream')# Redirect to the video list
            if not form.is_valid():
                error_msg = form.errors.get_json_data()
        elif request.method == 'GET':
            form = VideoForm()
        return render(
            request, 'video_stream.html', {'form': form, 'error_msg': error_msg})
    except Exception as err_msg:
        logger.info(
            f"{current_date} {current_time} : {err_msg}: Failed to create video")

#users update the videos name and videos path
@login_required
def update_video(request, video_id):
    '''
    Users can update the video
    '''
    error_msg = None
    try:
        video = get_object_or_404(Video, pk=video_id)
        if request.method == 'POST':
            form = VideoForm(request.POST, instance=video)
            if form.is_valid():
                form.save()
                logger.info(
                    f"{current_date} {current_time} : update video Successed")
                return redirect('video_stream')# Redirect to the video list view
            if not form.is_valid():
                error_msg = form.errors.get_json_data()

        elif request.method == 'GET':
            form = VideoForm(instance=video)
        return render(
            request, 'video_stream.html',
              {'form': form, 'video_id': video_id, 'error_msg': error_msg})
    except Exception as err_msg:
        logger.info(
            f"{current_date} {current_time} : {err_msg}: Failed to update video")

#users delete the videos
@login_required
def delete_video(request, video_id):
    '''
    users can delete the videos
    '''
    try:
        video = get_object_or_404(Video, pk=video_id)
        if request.method == 'POST':
            video.delete()
            logger.info(
                f"{current_date} {current_time} : update video Successed")
            return redirect('video_stream')  # Redirect to the video list view
        return render(request, 'delete_video.html', {'video': video})
    except Exception as err_msg:
        logger.info(
            f"{current_date} {current_time} : {err_msg}: Failed to delete the video")

class VideoListCreateAPIView(generics.ListCreateAPIView):
    '''
        video list and create rest api
    '''
    permission_classes = (AllowAny,)
#    permission_classes = (IsAuthenticated,)

    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def list(self, request, *args, **kwargs):
        '''
        users can get the videos using api
        '''
        try:
            #  user_id = request.user.id
            # Get the user_id from query parameter
            user_id = request.query_params.get('user_id')
            # Get the is_check from query parameters
            video_name = request.query_params.get('video_name')
            queryset = self.get_queryset()
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            if video_name:
                queryset = queryset.filter(name=video_name)
            # Note the use of `get_queryset()` instead of `self.queryset`
            serializer = VideoSerializer(queryset, many=True)
            logger.info(
                f"{current_date} {current_time} : Video List Retrieve successfully")         
            return json.Response(
                {'data':[serializer.data]},
                'Video list get successfully',200,True)
        except Exception as err_msg:
            logger.info(
                f"{current_date} {current_time} : {err_msg} : Failed to retrieve video List")
            return json.Response(
                {'data':err_msg},'Internal Server Error',400,False)

    def create(self, request, *args, **kwargs):
        '''
        users can create the videos using api
        '''
        try:
            datas = request.data
            user_id = datas['user_id']
            video_name = datas['video_name']
            video_path = datas['video_path']
            video = Video.objects.create(
                user_id=user_id, name=video_name, path=video_path)
            logger.info(
                f"{current_date} {current_time} : Selected Graph List created")
            return json.Response(
                {'data':video.name},'Successfully created the graph list',201,True)
        except Exception as err_msg:
            logger.info(
                f"{current_date} {current_time} : {err_msg} : Failed Selected Graph create list")
            return json.Response({'data':err_msg},'',400, False)

class VideoUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    video update and delete rest api
    '''
    queryset = Video.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = VideoSerializer
    lookup_field = ["id"]
    patchable_fields = ["name", "path"]

    def partial_update(self, request, *args, **kwargs):
        '''
        users can update the videos using api
        '''
        try:
            selected_graph = self.get_queryset().get(id=kwargs["pk"])

            data = request.data
            filtered_data = {}
            for e in self.patchable_fields:
                if e in data:
                    filtered_data[e] = data[e]

            serializer = self.get_serializer(
                selected_graph,
                partial=True,
                data=filtered_data
            )
            if serializer.is_valid():
                serializer.save()
                response_data = VideoSerializer(selected_graph).data
            logger.info(
                f"{current_date} {current_time} : Video detail updated")
            return json.Response(
                {'data':[response_data]},'Successfully updated',200,True)
        except Exception as err_msg:
            logger.info(
                f"{current_date} {current_time} : {err_msg} : Failed to update video detail")
            return json.Response(
                {'data':err_msg},'Internal Server Error',400,False)

    def destroy(self, request, *args, **kwargs):
        '''
        users can delete the videos using api
        '''
        try:
            instance = self.get_queryset().get(id=kwargs.get('pk'))
            if instance is not None:
                instance.delete()
                logger.info(f"{current_date} {current_time} : Video Destroy")
                return json.Response({'data':[]},'Successfully deleted',204,True)
            if instance is None:
                response_data = {
                    "validation_errors": None,
                }
                return json.Response(
                    {'data':[response_data]},'In-valid data',400,False)
        except Exception as err_msg: # pylint: disable=broad-except
            logger.info(
                f"{current_date} {current_time} : {err_msg} : Failed to Video Destroy")
            return json.Response(
                {'data':err_msg},'Internal Server Error',400,True)
