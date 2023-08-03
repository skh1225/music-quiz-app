"""
Views for the music APIs
"""
import tempfile
import yt_dlp
from urllib.request import urlopen

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.core.files import File
from django.core.files.base import ContentFile

from core.models import (
    Music,
    Tag,
    Singer,
    Room,
    User
)

from music import serializers
from django.db.models import Case, When



@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'singers',
                OpenApiTypes.STR,
                description='Comma separated list of singer IDs to filter',
            ),
            OpenApiParameter(
                'musics',
                OpenApiTypes.STR,
                description='Comma separated list of music IDs to filter',
            ),
        ]
    )
)
class MusicViewSet(viewsets.ModelViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.MusicSerializer
    queryset = Music.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def _params_to_list(self, qs):
        """Convert a list of strings to integers."""
        return [str_id for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve music for authenticated user."""
        tags = self.request.query_params.get('tags')
        singers = self.request.query_params.get('singers')
        musics = self.request.query_params.get('musics')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if singers:
            singer_ids = self._params_to_ints(singers)
            queryset = queryset.filter(singers__id__in=singer_ids)
        if musics:
            music_ids = self._params_to_list(musics)
            case_list = [When(id=id_val, then=pos) for pos, id_val in enumerate(music_ids)]
            queryset = queryset.filter(id__in=music_ids).order_by(Case(*case_list))
        return queryset.distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'upload_audio':
            return serializers.MusicAudioSerializer
        elif self.action == 'add_description':
            return serializers.MusicDescriptionSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new music."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-audio')
    def upload_audio(self, request, pk=None):
        """Upload an audio to music."""
        music = self.get_object()
        url = request.data.__getitem__('audio')

        with tempfile.TemporaryDirectory(dir='/vol') as tempdirname:
            URLS = [url]
            ydl_opts = {
                'format': 'bestaudio/best',  # 가장 좋은 화질로 선택(화질을 선택하여 다운로드 가능)
                'outtmpl': f'{tempdirname}/foo',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error_code = ydl.download(URLS)
            temp_file = open(f'{tempdirname}/foo.mp3', "rb")
            request.data.__setitem__('audio', File(temp_file))
        serializer = self.get_serializer(music, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='add-description')
    def add_description(self, request, pk=None):
        """Upload an audio to music."""
        music = self.get_object()
        description = request.data.__getitem__('description')
        request.data.__setitem__('description', music.description+','+description)

        serializer = self.get_serializer(music, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to music.',
            ),
        ]
    )
)
class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(music__isnull=False)

        return queryset.order_by('-name').distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to music.',
            ),
        ]
    )
)
class SingerViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.SingerSerializer
    queryset = Singer.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(music__isnull=False)

        return queryset.order_by('-name').distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'available_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
            OpenApiParameter(
                'mode',
                OpenApiTypes.STR, enum=['solo', 'team', 'all'],
                description='Filter by game mode ( solo | team )',
            ),
        ]
    ),
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                'password',
                OpenApiTypes.STR,
                description='Enter password',
            ),
        ]
    ),
    destroy=extend_schema(
        parameters=[
            OpenApiParameter(
                'password',
                OpenApiTypes.STR,
                description='Enter password',
            ),
        ]
    ),
)
class RoomViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RoomDetailSerializer
    queryset = Room.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        available_only = bool(
            int(self.request.query_params.get('available_only', 0))
        )
        mode = self.request.query_params.get('mode', 'all')
        queryset = self.queryset
        if available_only:
            queryset = queryset.filter(is_full=False)

        if mode == 'team':
            queryset = queryset.filter(is_team_battle=True)
        elif mode == 'solo':
            queryset = queryset.filter(is_team_battle=False)

        return queryset.distinct()


    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RoomSerializer
        elif self.action == 'partial_update':
            return serializers.RoomPatchSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        if 'music_length' not in request.data:
            request.data['music_length'] = 50
        request.data['music_list'] = list(Music.objects.order_by('?').values_list('id', flat=True)[:request.data['music_length']])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        password = self.request.query_params.get('password', None)
        if serializer.data['password'] is None and password is None or serializer.data['password'] == password:
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        password = self.request.query_params.get('password', None)
        if serializer.data['password'] is None and password is None or serializer.data['password'] == password:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    def partial_update(self, request, *args, **kwargs):
        if 'music_length' in request.data:
            request.data['music_list'] = list(Music.objects.order_by('?').values_list('id', flat=True)[:request.data['music_length']])
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

