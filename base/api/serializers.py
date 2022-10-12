# used to convert or serialise object into json file
# the reponse cannot be python, so to convert python object to json we use this.
# will work like model form

from rest_framework.serializers import ModelSerializer
from base.models import Room


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


