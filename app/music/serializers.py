"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Music,
    Tag,
    Singer,
    Room
)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class SingerSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Singer
        fields = ['id', 'name']
        read_only_fields = ['id']


class MusicAudioSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Music
        fields = ['id', 'audio']
        read_only_fields = ['id']


class MusicDescriptionSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Music
        fields = ['description']
        extra_kwargs = {'description': {'required': 'True'}}


class MusicSerializer(serializers.ModelSerializer):
    """Serializer for music."""
    tags = TagSerializer(many=True, required=False)
    singers = SingerSerializer(many=True, required=False)

    class Meta:
        model = Music
        fields = ['id', 'title', 'singers', 'tags', 'running_time', 'released_year', 'description', 'image', 'audio']

    def _get_or_create_tags(self, tags, music):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            music.tags.add(tag_obj)

    def _get_or_create_singers(self, singers, music):
        """Handle getting or creating singers as needed."""
        auth_user = self.context['request'].user
        for singer in singers:
            singer_obj, created = Singer.objects.get_or_create(
                user=auth_user,
                **singer,
            )
            music.singers.add(singer_obj)

    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        singers = validated_data.pop('singers', [])
        music = Music.objects.create(**validated_data)
        self._get_or_create_tags(tags,music)
        self._get_or_create_singers(singers,music)

        return music

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        singers = validated_data.pop('singers', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if singers is not None:
            instance.singers.clear()
            self._get_or_create_singers(singers, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room."""

    class Meta:
        model = Room
        fields = ['name', 'is_team_battle', 'is_full', 'max_user', 'music_length']


class RoomDetailSerializer(RoomSerializer):
    """Serializer for recipe detail view."""

    class Meta(RoomSerializer.Meta):
        fields = RoomSerializer.Meta.fields + ['music_list', 'password']


class RoomPatchSerializer(RoomSerializer):
    """Serializer for Room."""

    class Meta(RoomSerializer.Meta):
        fields = RoomSerializer.Meta.fields + ['music_list', 'music_length']
        read_only_fields = ['name']


