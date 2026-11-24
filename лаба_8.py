import functools
import time
attempts_state = {'n':0}
def create_genre_filter(genre:str):
    """ Фильтр жанров  """
    def genre_filter(track: dict) -> bool:
        return track.get('genre')==genre
    return genre_filter

def create_duration_filter(max_seconds:int):
    """ фильтр по длительности"""
    def duration_filter(track: dict) -> bool:
        return track.get('duration', 0) <= max_seconds
    return duration_filter

def create_bpm_filter(min_bpm:int, max_bpm:int):
    """ фильтр по бпм"""
    def bpm_filter(track: dict):
        bpm = track.get('bpm',0)
        return min_bpm <= bpm <=max_bpm
    return bpm_filter

def create_pipeline(filters:list):
    """ фильтр трека по всем вышеперечисленным характеристикам """
    def pipeline(tracks:list) -> list:
        result = tracks
        for f in filters:
            result = [track for track in result if f(track)]
        return result
    return pipeline

def log_calls(func):
    """ информация о каждом вызове функции """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f'{k} =  {v!r}' for k,v in kwargs.items()]
        signature = ', '.join(args_repr + kwargs_repr)
        print(f'[LOG] Вызов {func.__name__}({signature})')
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f'[LOG] {func.__name__} выбросил {type(e).__name__}: {e}')
            raise
        print(f'[LOG] {func.__name__} -> {result!r}')
        return result
    return wrapper

def count_calls(func):
    """ Счётчик вызовов """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)
    wrapper.call_count = 0
    return wrapper

def retry(times=3):
    """ повторная попытка вызова функции """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    print(f'[RETRY] {func.__name__}: попытка {attempt}/{times}'
                          f' провалилась ({type(e).__name__}: {e})')
                    if attempt < times:
                        time.sleep(0.05)
            raise last_exc
        return wrapper
    return decorator

class Playlist():
    def __init__(self, tracks: list):
        self._tracks = list(tracks)
        self._history = []

    def __call__(self, filter_func):
        self._tracks = [t for t in self._tracks if filter_func(t)]
        name = getattr(filter_func, "__name__", repr(filter_func))
        self._history.append(name)
        return self

    def __len__(self):
        return len(self._tracks)

    def __str__(self):
        if not self._tracks:
            return 'Плейлист пуст'
        lines = [f'Плейлист ({len(self._tracks)} треков):']
        for t in self._tracks[:3]:
            lines.append(f' - {t.get("title", "?")}'
                         f'[{t.get("genre", "?")},'
                         f'{t.get("duration", "?")} с,'
                         f'{t.get("bpm", "?")} bpm]')
        if len(self._tracks)>3:
            lines.append(f' ... и ещё {len(self._tracks) - 3} треков')
        return '\n'.join(lines)
    def history(self):
        return list(self._history)

    @property
    def tracks(self):
        return list(self._tracks)

class MusicPipeline():
    def __init__(self, filters:list):
        self._filters = list(filters)

    def process(self, tracks:list) -> list:
        print(f'\n [PIPELINE] Начало плейлиста из {len(tracks)} треков'
              f' всего фильтров:{len(self._filters)}')
        current = list(tracks)
        for i, f in enumerate (self._filters, 1):
            name = getattr(f, '__name__', f'filter_{i}')
            before = len(current)
            current = [t for t in current if f(t)] #записываем только отфильтрованные значения в список
            after = len(current)
            titles = [t.get('title', '?') for t in current] #выводим названия отфильтрованных значений 
            print(f'Шаг {i}: {name} ({before} -> {after})'
                  f'осталось: {titles}')
        print (f'[PIPELINE] Готово: {len(current)} треков')
        return current 

    def __len__(self):
        return len(self._filters)

    def __iter__(self):
        return iter(self._filters)
tracks = [
    {'title': "We're not gonna take it ", 'genre': 'metal', 'duration': 220, 'bpm':90},
    {'title': 'Somebody that i used to know ', 'genre': 'pop', 'duration': 245, 'bpm':128},
    {'title': 'Ток', 'genre': 'pop', 'duration':173 , 'bpm':120},
    {'title': 'Авиасейлс', 'genre': 'pop', 'duration': 33, 'bpm':94},
    {'title': 'In the end', 'genre': 'rock', 'duration':217 , 'bpm':105},
    {'title': 'Beliver', 'genre': 'rock', 'duration':203 , 'bpm':98},
    {'title': 'Papermoon', 'genre': 'pop', 'duration':263 , 'bpm':163},
    {'title': 'Купидоны', 'genre': 'rap', 'duration':167 , 'bpm':172},
    {'title': 'Two time', 'genre': 'pop', 'duration':142 , 'bpm':99}
    ]

def show(title,items):
    print(f'\n==={title}===')
    if not items:
        print(' (пусто) ')
        return
    for t in items:
        print(f" {t['title']} | {t['genre']} "
              f"{t['duration']} s | {t['bpm']} bpm")
show('Все треки', tracks)
rock_only = create_genre_filter('rock')
show('create_genre_filter("rock"),', [t for t in tracks if rock_only(t)])
max_have = create_duration_filter(215)
show('create_duration_filter(215)', [t for t in tracks if max_have(t)])
ograch = create_bpm_filter(90,120)
show('create_bpm_filter(90,120)', [t for t in tracks if ograch(t)])
filterch = create_pipeline([create_genre_filter('rock'), create_duration_filter(215),  create_bpm_filter(90,120)])
show('create_pipeline ([rock, <=215 s, 90-120 bpm ])', filterch(tracks))

print('='*60)
print('2 задание')
print('='*60)

@log_calls
def total_duration(tracks_list):
    return sum(t['duration'] for t in tracks_list)
total_duration(tracks)
print(f'Метаданные сохранены: {total_duration.__name__}'
      f'(functools.wraps)')
print(f'\n--- @count_calls ---')

@count_calls
def count_rock(track_list):
    return sum(1 for t in track_list if t['genre'] == 'rock')

for _ in range(3):
    count_rock(tracks)
print(f' count_calls.call_count = {count_rock.call_count}')
print(f' __name__ сохранён: {count_rock.__name__}')

print(f'\n ---@retry---')
attemps_state = {'n':0}

@retry(times=3)
def flaky_loader():
    attempts_state['n'] += 1
    if attempts_state['n'] < 2:
        raise ConnectionError(f"сеть недоступна (попытка {attempts_state['n']})")
    return f"успех с {attempts_state['n']}-й попытки"
try:
    result = flaky_loader()
    print(f'Результат: {result}')
except Exception as e:
    print(f'Ошибка! {e}')

print("=" * 60)
print("3. Playlist")
print("=" * 60)

pl = Playlist(tracks)
print(f'Изначально: {len(pl)} треков')

rock_filter = create_genre_filter("rock")
short_filter = create_duration_filter(215)
bpm_filter = create_bpm_filter(90, 200)

pl(rock_filter)(short_filter)(bpm_filter)   # цепочка через __call__
print(f'После 3 фильтров: {len(pl)} треков')
print(pl)                                     # __str__
print(f'История: {pl.history()}')           # history()

print("=" * 60)
print("4. MusicPipeline")
print("=" * 60)

pipeline = MusicPipeline([rock_filter, short_filter, bpm_filter])
print(f'Фильтров в конвейере (__len__): {len(pipeline)}')
print(f'Итерация (__iter__): '
      f'{[getattr(f, '__name__', '?') for f in pipeline]}')

final = pipeline.process(tracks)
print(f"Финальный результат: {[t['title'] for t in final]}")
print("=" * 60)
 