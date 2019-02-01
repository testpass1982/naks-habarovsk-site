from .models import Menu


def menu_urls(request):
    print('...menu_urls context_processors works...')
    menu_urls = Menu.objects.all().order_by('order')
    print('urls in database:', len(menu_urls))
    for url in menu_urls:
        print('url', url.title, url.url)
    return {'menu_urls': menu_urls, }
