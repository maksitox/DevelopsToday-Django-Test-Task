from rest_framework import viewsets, mixins, status
from rest_framework import viewsets, mixins, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import TravelProject, Place
from .serializers import TravelProjectSerializer, PlaceSerializer, UserRegistrationSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class TravelProjectViewSet(viewsets.ModelViewSet):
    queryset = TravelProject.objects.all().order_by('-created_at')
    serializer_class = TravelProjectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.places.filter(visited=True).exists():
            return Response(
                {"error": "Cannot delete project with visited places."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='places')
    def add_place(self, request, pk=None):
        project = self.get_object()
        if project.places.count() >= 10:
             return Response({"error": "Maximum 10 places allowed per project."}, status=status.HTTP_400_BAD_REQUEST)
        
        # We need to validate unique external_id within project
        # Serializer validator might need project context, or we check here.
        external_id = request.data.get('external_id')
        if external_id and project.places.filter(external_id=external_id).exists():
             return Response({"error": "Place with this external ID already exists in the project."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PlaceSerializer(data=request.data, context={'project': project})
        if serializer.is_valid():
             serializer.save(project=project)
             # Adding a place means project is incomplete (unless place is visited immediately?)
             # Usually new place is visited=False.
             if project.completed:
                 project.completed = False
                 project.save()
             return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='places')
    def list_places(self, request, pk=None):
        project = self.get_object()
        places = project.places.all()
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data)

class PlaceViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    def perform_update(self, serializer):
        place = serializer.save()
        # Update project completion status
        project = place.project
        # Check if all places are visited
        all_visited = not project.places.filter(visited=False).exists()
        # Also ensure at least one place exists to be "completed"?
        # Requirement: "When all places... are marked as visited, the project is marked as completed."
        # If 0 places, is it completed? Maybe.
        if project.places.count() > 0 and all_visited:
            if not project.completed:
                project.completed = True
                project.save()
        else:
            if project.completed:
                project.completed = False
                project.save()
