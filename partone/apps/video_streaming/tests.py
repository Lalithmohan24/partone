from rest_framework import status
from rest_framework.test import APITestCase
from urllib.parse import urlencode
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Video
class VideoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_video(self):
        user_id = self.user.id
        url = reverse('videolistcreate')
        data = {'video_name': 'Test Video', 'video_path': 'video4.mp4', 'user_id': user_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.count(), 1)
        self.assertEqual(Video.objects.get().name, 'Test Video')

    def test_retrieve_video(self):
        user_id = self.user.id
        video = Video.objects.create(name='Test Video', path='video4.mp4', user_id=user_id)
        url = reverse('videolistcreate')
        params = {'video_name': video.name}  # Customize the parameter name as needed
        url_with_params = f"{url}?{urlencode(params)}"

        response = self.client.get(url_with_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_video(self):
        user_id = self.user.id
        video = Video.objects.create(name='Test Video', path='video5.mp4', user_id=user_id)
        url = reverse('videodetail', args=[video.pk])
        data = {'name': 'Updated Video', 'path': 'video5.mp4'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Video.objects.get(pk=video.pk).name, 'Updated Video')

    def test_delete_video(self):
        user_id = self.user.id
        video = Video.objects.create(name='Test Video', path='video5.mp4', user_id=user_id)
        url = reverse('videodetail', args=[video.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Video.objects.count(), 0)
