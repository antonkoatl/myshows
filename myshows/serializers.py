from rest_framework import serializers

from myshows.models import Show


class ShowSerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField(many=True)
    genres = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    network = serializers.StringRelatedField(many=False)

    class Meta:
        model = Show
        fields = '__all__'
