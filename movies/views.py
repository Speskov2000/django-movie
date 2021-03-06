from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse

from .models import Movie, Actor, Genre
from .forms import ReviewForm


class GenreYear():
    '''Жанры и года выхода фильмов'''

    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values('year')


class MovieView(GenreYear, ListView):
    '''Список фильмов'''

    model = Movie
    queryset = Movie.objects.filter(draft=False)


class MovieDetailView(GenreYear, DetailView):
    '''Полное описание фильмов'''

    model = Movie
    slug_field = 'url'


class AddReview(View):
    '''Отзывы'''

    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get('parent', None):
                form.parent_id = int(request.POST.get('parent'))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())


class ActorView(GenreYear, DetailView):
    '''Вывод инфомрации о актере'''

    model = Actor
    template_name = 'movies/actor.html'
    slug_field = 'name'


class FilterMoviesView(GenreYear, ListView):
    '''Фильтр фильмов'''

    def get_queryset(self):
        queryset = Movie.objects.filter(
                Q(year__in=self.request.GET.getlist('year')) |
                Q(genres__in=self.request.GET.getlist('genre'))
        )
        return queryset


class JsonFilterMoviesView(ListView):
    '''Фильтр фильмов в json'''

    def get_queryset(self):
        queryset = Movie.objects.filter(
                Q(year__in=self.request.GET.getlist('year')) |
                Q(genres__in=self.request.GET.getlist('genre'))
        ).distinct().values('title', 'tagline', 'url', 'poster')
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        return JsonResponse({'movies': queryset}, safe=False)
