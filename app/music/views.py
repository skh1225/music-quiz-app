"""
Views for the music APIs
"""
import os
import tempfile
import requests
import yt_dlp
import re
import ytmusicapi
from difflib import SequenceMatcher

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
    exceptions,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.core.files import File
from django.core.files.images import ImageFile

from core.models import (
    Music,
    Tag,
    Singer,
    Room
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
    ),
    search_music=extend_schema(
        parameters=[
            OpenApiParameter(
                'title_singer',
                OpenApiTypes.STR,
                description='title--singer',
            )
        ]
    ),
)
class MusicViewSet(viewsets.ModelViewSet):
    """Manage Musics in the database."""
    serializer_class = serializers.MusicSerializer
    queryset = Music.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def _params_to_list(self, qs):
        """Convert string to list of strings."""
        return qs.split(',')

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
        if self.action == 'partial_update':
            return serializers.MusicPatchSerializer
        elif self.action == 'upload_image':
            return serializers.MusicImageSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """Create music. (audio field is not required. It's automatically created)"""
        if not self.request.user.is_staff:
            return Response({'detail': 'only staff can register music.'}, status=status.HTTP_401_UNAUTHORIZED)
        url = 'https://www.youtube.com/watch?v=' + request.data['id']

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
                if error_code:
                    print('download fail')
                    return Response({'detail': 'download fail'}, status=status.HTTP_400_BAD_REQUEST)

                info_by_ytdlp = ydl.extract_info(url, download=False)

            temp_file = open(f'{tempdirname}/foo.mp3', "rb")
            request.data.__setitem__('audio', File(temp_file))
        if 'image' in request.data and request.data['image'].rfind('=') > -1:
            request.data['image'] = request.data['image'][:request.data['image'].rfind('=')]
        if 'release_year' not in request.data or not request.data['released_year']:
            if info_by_ytdlp['release_year']:
                request.data['released_year'] = info_by_ytdlp['release_year']
            else:
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', info_by_ytdlp['description'])
                if dates:
                    dates.sort()
                    request.data['released_year'] = dates[0][:4]
            request.data['tags'] = request.data.get('tags',[])
        if 'released_year' in request.data:
            request.data['tags'].append({ 'name': str(request.data['released_year'])[:3]+'0년대' })

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Create a new music."""
        serializer.save(user=self.request.user)

    @action(methods=['GET'], detail=False,  url_path='search_music')
    def search_music(self, request):
        """Search music"""
        if not self.request.user.is_staff:
            return Response({'detail': 'only staff can search music.'}, status=status.HTTP_401_UNAUTHORIZED)
        query = self.request.query_params.get('title_singer')
        if not query:
            return Response({'detail': 'title_singer param is required'}, status=status.HTTP_400_BAD_REQUEST)
        yt = ytmusicapi.YTMusic('/app/oauth.json', language='ko')
        similarity = -1
        music_infos = yt.search(query, filter='songs')[:2]
        for music_info in music_infos:
            title = music_info['title']
            l_find = title.find('(')
            r_find = title.rfind(')')
            if l_find != -1 and r_find != -1:
                title = title[:l_find]+title[r_find+1:]
            title = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z'\s]", " ", title).strip()
            if not title:
                title = music_info['title']
            search_similarity = SequenceMatcher(None, query.split('--')[0].lower(), title.lower()).ratio()

            if search_similarity > similarity:
                similarity = search_similarity
                image = music_info['thumbnails'][0]['url']
                if image.rfind('=') > -1:
                    image = image[:image.rfind('=')]
                search_result = {
                  'id': music_info['videoId'],
                  'title': title,
                  'singers': [
                    {
                      'name': music_info['artists'][0]['name']
                    }
                  ],
                  'released_year': music_info['year'],
                  'running_time': music_info['duration_seconds'],
                  'image': image,
                }
                if search_similarity > 0.7:
                    break
        try:
            serializer = self.get_serializer(self.queryset.get(id=search_result['id']))
        except Music.DoesNotExist:
            serializer = self.get_serializer(search_result)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        music = Music.objects.all().get(id=pk)
        print(music.id)
        image_file = requests.get(music.image)
        filename = music.id+music.title+'.jpg'
        with tempfile.TemporaryFile('w+b') as img_file:
            img_file.write(image_file.content)
            request.data.__setitem__('image_file', File(img_file, name=filename))
            print(request.data)
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

        return queryset.order_by('-id').distinct()


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
        if not self.request.user.is_staff:
            return Response({'detail': 'only staff can create room.'}, status=status.HTTP_401_UNAUTHORIZED)
        music_queryset = Music.objects.all()
        if 'music_length' not in request.data:
            request.data['music_length'] = 50
        if request.data['music_tags']:
            tag_ids = [int(str_id) for str_id in request.data['music_tags'].split(',')]
            music_queryset = music_queryset.filter(tags__id__in=tag_ids)

        request.data['music_list'] = list(music_queryset.order_by('?').values_list('id', flat=True))
        if len(request.data['music_list']) < request.data['music_length']:
            return Response({
                'detail': f"Filtered : {len(request.data['music_list'])}, Required : {request.data['music_length']}"},
                status=status.HTTP_400_BAD_REQUEST)
        request.data['music_list'] = request.data['music_list'][:request.data['music_length']]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        password = self.request.query_params.get('password', None)
        if not serializer.data['password'] and not password or serializer.data['password'] == password:
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        password = self.request.query_params.get('password', None)
        if not serializer.data['password'] and not password or serializer.data['password'] == password:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    def partial_update(self, request, *args, **kwargs):
        if 'music_length' in request.data:
            request.data['music_list'] = list(Music.objects.order_by('?').values_list('id', flat=True)[:request.data['music_length']])
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

