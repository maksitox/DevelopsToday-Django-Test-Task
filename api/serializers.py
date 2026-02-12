from rest_framework import serializers
from .models import TravelProject, Place
from .services import ArtInstituteService

class PlaceSerializer(serializers.ModelSerializer):
    external_id = serializers.IntegerField()

    class Meta:
        model = Place
        fields = ['id', 'external_id', 'name', 'notes', 'visited', 'project']
        read_only_fields = ['id', 'name', 'project']
        extra_kwargs = {
            'project': {'required': False} # Injected in view or parent serializer
        }

    def validate_external_id(self, value):
        # Basic validation that place exists
        place_data = ArtInstituteService.get_place(value)
        if not place_data:
            raise serializers.ValidationError(f"Place with ID {value} not found in Art Institute API.")
        self.context['place_data'] = place_data
        return value

    def create(self, validated_data):
        place_data = self.context.get('place_data')
        if not place_data:
            # Re-fetch if not in context (e.g. bulk create passing validated data directly?)
            # Or reliance on validate running first.
             place_data = ArtInstituteService.get_place(validated_data['external_id'])
        
        validated_data['name'] = place_data['name']
        return super().create(validated_data)


class TravelProjectSerializer(serializers.ModelSerializer):
    places = PlaceSerializer(many=True, read_only=True)
    initial_places = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = TravelProject
        fields = ['id', 'name', 'description', 'start_date', 'created_at', 'completed', 'places', 'initial_places']
        read_only_fields = ['id', 'created_at', 'completed']

    def validate_initial_places(self, value):
        if len(value) > 10:
             raise serializers.ValidationError("Maximum 10 places allowed per project.")
        
        seen_ids = set()
        validated_places_data = []

        for item in value:
            ext_id = item.get('external_id')
            if not ext_id:
                raise serializers.ValidationError("Each place must have an 'external_id'.")
            
            if ext_id in seen_ids:
                raise serializers.ValidationError(f"Duplicate external_id {ext_id} in request.")
            seen_ids.add(ext_id)

            place_data = ArtInstituteService.get_place(ext_id)
            if not place_data:
                raise serializers.ValidationError(f"Place ID {ext_id} not found.")
            
            # Merge API name with input notes
            item['name'] = place_data['name']
            validated_places_data.append(item)
        
        # Store for create method
        self.context['validated_places_data'] = validated_places_data
        return value

    def create(self, validated_data):
        initial_places = validated_data.pop('initial_places', [])
        project = super().create(validated_data)
        
        validated_places_data = self.context.get('validated_places_data', [])
        
        # We rely on previous validation or re-validate?
        # Since validate_initial_places is called by isValid, validated_data contains the returned value of validate logic.
        # But wait, validate_initial_places updates self.context but returns 'value'.
        # If 'initial_places' is popped from validated_data, it is the RAW input or clean input?
        # It's what returned by validate_initial_places.
        
        # Better to rely on the data we enriched in context or re-fetch (caching in service helps).
        # We already enriched in logic above? No, we appended to locally.
        
        # Actually, let's just use the data we have.
        if validated_places_data:
            for item in validated_places_data:
                Place.objects.create(
                    project=project,
                    external_id=item['external_id'],
                    name=item['name'],
                    notes=item.get('notes', '')
                )
        elif initial_places:
             # Fallback if validate didn't populate context (e.g. direct save?)
             pass
             
        return project
