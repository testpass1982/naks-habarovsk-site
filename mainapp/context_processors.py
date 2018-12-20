from .models import Menu


def menu_urls(request):
    print('...menu_urls context_processors works...')
    menu_urls = Menu.objects.filter(url__startswith='http').order_by('order')
    print('urls in database:', len(menu_urls))
    return {'menu_urls': menu_urls, }
