from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from .models import TravelProject, Place

class TravelProjectTests(APITestCase):
    def setUp(self):
        self.project_data = {'name': 'Test Project'}
        self.project = TravelProject.objects.create(**self.project_data)

    def test_create_project(self):
        url = reverse('project-list')
        data = {'name': 'New Project'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TravelProject.objects.count(), 2)

    @patch('api.services.ArtInstituteService.get_place')
    def test_create_project_with_places(self, mock_get_place):
        mock_get_place.return_value = {'external_id': 123, 'name': 'Artwork'}
        url = reverse('project-list')
        data = {
            'name': 'Project with Places',
            'initial_places': [{'external_id': 123}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.count(), 1)
        self.assertEqual(Place.objects.first().name, 'Artwork')

    @patch('api.services.ArtInstituteService.get_place')
    def test_add_place_to_project(self, mock_get_place):
        mock_get_place.return_value = {'external_id': 456, 'name': 'Another Artwork'}
        url = reverse('project-add-place', args=[self.project.id])
        data = {'external_id': 456}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.project.places.count(), 1)

    def test_delete_project_with_visited_places(self):
        Place.objects.create(project=self.project, external_id=1, name='Vis', visited=True)
        url = reverse('project-detail', args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_project_without_visited_places(self):
        Place.objects.create(project=self.project, external_id=1, name='Vis', visited=False)
        url = reverse('project-detail', args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_project_completion_logic(self):
        place = Place.objects.create(project=self.project, external_id=1, name='Vis', visited=False)
        self.assertFalse(self.project.completed)
        
        # Mark visited via Place update
        url = reverse('place-detail', args=[place.id])
        response = self.client.patch(url, {'visited': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.project.refresh_from_db()
        self.assertTrue(self.project.completed)

        # Mark unvisited
        response = self.client.patch(url, {'visited': False})
        self.project.refresh_from_db()
        self.assertFalse(self.project.completed)
