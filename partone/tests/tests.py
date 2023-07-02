from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..apps.video_streaming.models import Video


class VideoTests(APITestCase):
    """
    Video model test case
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_video(self):
        """
        Testing the create video
        """
        url = reverse('videolistcreate/')
        data = {'name': 'Test Video', 'path': 'video4.mp4'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.count(), 1)
        self.assertEqual(Video.objects.get().name, 'Test Video')

    def test_retrieve_video(self):
        """
        Testing the retrieves list of video
        """
        video = Video.objects.create(name='Test Video', path='video4.mp4')
        url = reverse('videolist/', args=[video.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Video')

    def test_update_video(self):
        """
        Testing the update video
        """
        video = Video.objects.create(name='Test Video', path='video5.mp4')
        url = reverse('videodetail', args=[video.pk])
        data = {'name': 'Updated Video', 'path': 'video5.mp4'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Video.objects.get(pk=video.pk).name, 'Updated Video')

    def test_delete_video(self):
        """
        Testing the delete video
        """
        video = Video.objects.create(name='Test Video', path='video5.mp4')
        url = reverse('video-detail', args=[video.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Video.objects.count(), 0)
