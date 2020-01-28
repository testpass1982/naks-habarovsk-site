import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
# from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, PostPhoto, Tag, Category, Document, Article, Message, Contact
from .models import Registry
from .models import Staff
from .forms import PostForm, ArticleForm, DocumentForm, ProfileImportForm, Profile
from .forms import SendMessageForm, SubscribeForm, AskQuestionForm, DocumentSearchForm, SearchRegistryForm
from django.core.mail import send_mail
from .adapters import MessageModelAdapter
from .message_tracker import MessageTracker
from .utilites import UrlMaker, update_from_dict
from .registry_import import Importer, data_url
from .forms import OrderForm
from django.conf import settings

# Create your views here.


def index(request):
    """this is mainpage view with forms handler and adapter to messages"""
    title = "Главная страница"
    tracker = MessageTracker()
    if request.method == 'POST':
        request_to_dict = dict(zip(request.POST.keys(), request.POST.values()))
        form_select = {
            'send_message_button': SendMessageForm,
            'subscribe_button': SubscribeForm,
            'ask_question': AskQuestionForm,
        }
        for key in form_select.keys():
            if key in request_to_dict:
                print('got you!', key)
                form_class = form_select[key]
        form = form_class(request_to_dict)
        if form.is_valid():
            # saving form data to messages (need to be cleaned in future)
            adapted_data = MessageModelAdapter(request_to_dict)
            adapted_data.save_to_message()
            print('adapted data saved to database')
            tracker.check_messages()
            tracker.notify_observers()
        else:
            raise ValidationError('form not valid')

    main_page_news = Post.objects.filter(
        publish_on_main_page=True)[:3]

    not_pictured_posts = Post.objects.filter(
        publish_in_basement=True)[:3]

    main_page_documents = Document.objects.filter(
        publish_on_main_page=True).order_by('-created_date')[:3]

    main_page_secondery_news = Post.objects.filter(
        publish_in_basement=True).order_by('-published_date')[:4]
    pictured_posts = {}
    for post in main_page_news:
        pictured_posts[post] = PostPhoto.objects.filter(post__pk=post.pk).first()
    print(pictured_posts)

    main_page_articles = Article.objects.filter(
        publish_on_main_page=True).order_by('-published_date')[:3]

    # print(request.resolver_match)
    # print(request.resolver_match.url_name)

    content = {
        'title': title,
        'pictured_posts': pictured_posts,
        'not_pictured_posts': not_pictured_posts,
        'articles': main_page_articles,
        'docs': main_page_documents,
        'send_message_form': SendMessageForm(),
        'subscribe_form': SubscribeForm(),
        'ask_question_form': AskQuestionForm()
    }
    # import pdb; pdb.set_trace()
    return render(request, 'mainapp/index.html', content)


def news(request):
    """this is the news view"""
    title = "Новости АЦ"
    all_news = Post.objects.all().filter(
        publish_on_news_page=True).order_by('-created_date')
    all_documents = Document.objects.all().order_by('-created_date')[:5]
    side_articles = Article.objects.all().order_by('-created_date')[:3]
    post_list = [dict({'post': post, 'picture': PostPhoto.objects.filter(
        post__pk=post.pk).first()}) for post in all_news]
    # показываем несколько новостей на странице
    paginator = Paginator(post_list, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    articles = Article.objects.all().order_by('-created_date')[:3]

    print(request.resolver_match)
    print(request.resolver_match.url_name)

    content = {
        'title': title,
        'news': posts,
        'documents': all_documents,
        'side_related': side_articles,
        'bottom_related': articles

    }

    return render(request, 'mainapp/news.html', content)


def details(request, pk=None, content=None):

    print(request.resolver_match)
    print(request.resolver_match.url_name)
    return_link = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    if request.GET:
        content = request.GET.get('content_type')
        pk = request.GET.get('pk')

    content_select = {
        'post': Post,
        'article': Article
    }
    obj = get_object_or_404(content_select[content], pk=pk)
    print(obj)
    common_content = {'title': obj.title}
    if content == 'post':
        attached_images = PostPhoto.objects.filter(post__pk=pk)
        attached_documents = Document.objects.filter(post__pk=pk)
        side_related = Post.objects.all().exclude(
            id=pk).order_by('-created_date')[:2]
        side_related_posts = [dict({'post': post, 'picture': PostPhoto.objects.filter(
            post__pk=post.pk).first()}) for post in side_related]
        post_content = {
            'post': obj,
            'images': attached_images,
            'documents': attached_documents,
            'side_related_posts': side_related_posts,
            'side_panel': obj.side_panel,
            'bottom_related': Article.objects.all().order_by(
                '-created_date')[:3]
        }
        print('SIDE_RELATED', post_content['side_related_posts'])
    if content == 'article':
        tags_pk_list = [tag.pk for tag in obj.tags.all()]
        related_articles = Article.objects.filter(
            tags__in=tags_pk_list).exclude(pk=pk).distinct()
        post_content = {
            'post': obj,
            'related': related_articles,
            'bottom_related': related_articles.order_by('-created_date')[:3]
        }

    context = common_content.copy()
    from .models import SidePanel
    context.update(post_content)
    context['return_link'] = return_link

    print(request.resolver_match)
    print(request.resolver_match.url_name)

    return render(request, 'mainapp/page_details.html', context)


def create_factory(request, content_type):

    form_name_select = {
        'post': 'новость',
        'article': 'статью',
        'document': 'документ'
    }
    title = 'Создать {}'.format(form_name_select[content_type])

    forms = {
        'post': PostForm,
        'article': ArticleForm,
        'document': DocumentForm
    }

    if request.method == "POST":

        form_Class = forms[content_type]

        form = form_Class(request.POST)
        if content_type == 'document':
            form = form_Class(request.POST, request.FILES)

        if form.is_valid():
            content = form.save(commit=False)
            content.save()
            return redirect('news')
        else:
            messages.error(request, "Error")
            context = {
                'title': 'Исправьте ошибки формы',
                'form': form
            }

            return render(request, 'mainapp/content_edit_form.html', context)
    else:
        form_Class = forms[content_type]
        if content_type in forms:
            context = {
                'title': title,
                'form': form_Class()
            }
        else:
            raise Http404

        return render(request, 'mainapp/content_edit_form.html', context)


def validate_form(request):
    '''view to expand in future with ajax'''
    email = request.GET.get('email', None)
    data = {
        'Email': 'Email success'
    }
    return JsonResponse(data)


def contact(request):
    '''view to contact page - forms will redirect here in future'''
    if request.method == 'POST':
        print(request.POST)
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        context = {
            'name': name,
            'phone': phone
        }
    else:
        context = {
            'title': 'Контакты'
        }

    contacts = Contact.objects.all().order_by('number')

    context['contacts'] = contacts

    return render(request, 'mainapp/contact.html', context)


def messages(request):
    '''view to all messages in one page - will be @login_required'''
    # html = '<h1>I\'m working</h1>'
    # return HttpResponse(html)
    messages_list = Message.objects.all()

    context = {
        'messages': messages_list
    }
    return render(request, 'mainapp/messages.html', context)


def documents(request):
    """view for documents page"""

    # doctypes = ['Аккредитация САСв', 'Допуск ЦОК', 'Оценочное средство']

    # tags = Tag.objects.all().filter(name__in=doctypes)
    search_form = DocumentSearchForm()
    if request.method == 'GET':
        search_result_content = {}
        if 'search_document' in request.GET:
            print('REQUEST_GET', request.GET)
            search_form = DocumentSearchForm(request.GET)
            if search_form.is_valid():
                search_result = Document.objects.filter(
                    title__contains=request.GET.get('document_name')).order_by('-created_date')
                print('SEARCH_RESULT', search_result)
                search_result_content['search_result'] = search_result
    all_documents = Document.objects.all().order_by('created_date')
    # accreditation_list = Document.objects.filter(
    #     tags__in=Tag.objects.filter(name='Аккредитация САСв'))
    # cok_accreditation_list = Document.objects.filter(
    #     tags__in=Tag.objects.filter(name='Допуск ЦОК'))
    # os_doc_list = Document.objects.filter(
    #     tags__in=Tag.objects.filter(name='Оценочное средство'))
    # norm_doc_list = Document.objects.filter(
    #     tags__in=Tag.objects.filter(name='Нормативный документ'))
    # sogl_doc_list = Document.objects.filter(
    #     tags__in=Tag.objects.filter(name='Соглашение'))
    # print(accreditation_list)
    # print(cok_accreditation_list)
    # print(os_doc_list)

    content = {
        'title': 'Документы',
        # 'accreditation_list': accreditation_list,
        # 'cok_accreditation_list': cok_accreditation_list,
        # 'os_doc_list': os_doc_list,
        # 'norm_doc_list': norm_doc_list,
        # 'sogl_doc_list': sogl_doc_list,
        'documents': all_documents,
        'search_form': search_form
    }
    if search_result_content:
        content.update(search_result_content)
        print('CONTENT WITH SEARCH', content)
    return render(request, 'mainapp/documents.html', content)


def services(request, pk):
    from .models import Service
    service = Service.objects.get(pk=pk)
    side_panel = service.side_panel
    return render(request, 'mainapp/services.html', {'service': service, 'side_panel': side_panel})

def articles(request):
    all_articles = Article.objects.all().order_by('published_date')
    content = {
        'articles': all_articles
    }
    return render(request, 'mainapp/articles.html', content)

def article_details(request, pk):
    article = get_object_or_404(Article, pk=pk)
    content = {
        'article': article
    }
    return render(request, 'mainapp/article_details.html', content)

def about(request):
    """this is docstring"""
    pages = Post.objects.filter(category__name='О центре')
    content = {
        'pages': pages
    }
    return render(request, 'mainapp/about.html', content)


def staff(request):
    """this is docstring"""
    staff = Staff.objects.all().order_by('-priority')
    print(staff)

    content = {
        'staff': staff
    }

    return render(request, 'mainapp/staff.html', content)


def reestrsp(request, type=None):
    """registry view for imported database entries"""
    search_form = SearchRegistryForm()
    if 'search' in request.GET:
        form = SearchRegistryForm(request.GET)
        if form.is_valid:
            print('valid')
            search_form = form
            records = Registry.objects.filter(
                Q(title__contains=request.GET.get('fio')), Q(org__contains=request.GET.get('work_place')))
    else:
        records = Registry.objects.all().order_by('-created_date')

    result_to_page = []
    for result in records:
        result_to_page.append(json.loads(result.params))

    list_of_records = result_to_page

    """import data from data-url using token"""
    if request.GET.get('import'):
        accept = request.GET.get('import')
        if accept == 'Y':
            imported = Importer(data_url)
            for i in range(200):
                imported.save_data_to_db(imported.data[i])
                print('DONE IMPORT')

    page = request.GET.get('page')
    paginator = Paginator(list_of_records, 10)
    paginated_records = paginator.get_page(page)
    page_url = request.build_absolute_uri()

    """making next and previous page urls"""
    urlmaker = UrlMaker(page_url, paginated_records)
    urlmaker.make_next_url()
    urlmaker.make_prev_url()
    print('CURRENT', urlmaker.current)

    if len(paginated_records) != 0:
        content = {
            'records': paginated_records,
            'search_form': search_form,
            'urls': urlmaker.urls_dict,
        }
    else:
        print('empty')
        content = None

    return render(request, 'mainapp/reestr.html', content)

def import_profile(request):
    content = {}
    if request.method == "POST":
        if len(request.FILES) > 0:
            form = ProfileImportForm(request.POST, request.FILES)
            if form.is_valid():
                data = request.FILES.get('file')
                file = data.readlines()
                import_data = {}
                for line in file:
                    string = line.decode('utf-8')
                    if string.startswith('#') or string.startswith('\n'):
                        # print('Пропускаем: ', string)
                        continue
                    splitted = string.split("::")
                    import_data.update({splitted[0].strip(): splitted[1].strip()})
                    # print('Импортируем:', string)
                profile = Profile.objects.first()
                if profile is None:
                    profile = Profile.objects.create(org_short_name="DEMO")
                try:
                    #updating existing record with imported fields
                    update_from_dict(profile, import_data)
                    content.update({'profile_dict': '{}'.format(profile.__dict__)})
                    content.update({'profile': profile})
                    print('***imported***')
                except Exception as e:
                    print("***ERRORS***", e)
                    content.update({'errors': e})
        else:
            content.update({'errors': 'Файл для загрузки не выбран'})
        return render(request, 'mainapp/includes/profile_load.html', content)


def accept_order(request):
    if request.method == 'POST':
        # print('REQUEST POST', request.POST)

        order_variants = {
            "att_sv": "Аттестация сварщиков",
            "att_sp_sv": "Аттестация специалистов сварочного производства",
            "att_sm": "Аттестация сварочных материалов",
            "att_so": "Аттестация сварочного оборудования",
            "att_st": "Аттестация сварочных технологий",
            "ocenka_qual": "Оценка квалификации в области сварки и контроля",
        }
        data = {
            "name": request.POST.get('name'),
            "phone": request.POST.get('phone'),
            "captcha_1": request.POST.get('captcha_1'),
            "captcha_0": request.POST.get('captcha_0'),
            "order_type": order_variants[request.POST.get('order_type')]
            }
        form = OrderForm(data)
        if form.is_valid():
            instance = form.save()
            current_absolute_url = request.build_absolute_uri()
            email_address_arr = ['popov.anatoly@gmail.com']

            if '8000' not in current_absolute_url:
                if Profile.objects.first() is not None:
                    admin_email_address = Profile.objects.first().org_order_email.split(" ")
                else:
                    admin_email_address = 'popov@naks.ru'
                email_address_arr += admin_email_address
            # 4seconds economy to send_email every time i make tests
            if not instance.name == 'tolik_make_tests':
                send_mail(
                    'Заполнена заявка на сайте',
    """
    Заполнена заявка на сайте {url}
    Имя: {name}, Телефон: {phone},
    Заявлено: {order_string}
    """.format(url=current_absolute_url,
               name=instance.name,
               phone=instance.phone,
               order_string=data['order_type']),
                    settings.EMAIL_HOST_USER,
                    email_address_arr
                )
            return JsonResponse({'message': 'ok', 'order_id': instance.pk})
        else:
            return JsonResponse({'errors': form.errors})