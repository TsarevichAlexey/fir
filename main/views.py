from django.shortcuts import get_object_or_404 #render - по умолчанию, нужен для функционального представления, здесь же будет классовое. Сама по себе функция нужна, если пользователь сразу хочет перейти на страницу товара

#Сайт будет многостраничным, но вместо того, чтобы каждый раз загружать новую страницу, сайт 1 раз загрузит base.html и в нем просто будет менять block content каждой нужной страницы
#По сути сайт будет динамичным (не такое частое явление)

#Будет возвращаться не шаблон страницы, а блок

from django.views.generic import TemplateView, DetailView #Классовое представление для больших массивов данных / шаблоны, первый для одностраничных сайтов без задействования бд; второй сам находит нужный товар из бд и вставляет его в страницу
from django.http import HttpResponse #возвращает браузеру простейшие команды/текст на python в виде http-запроса
from django.template.response import TemplateResponse #Позволяет менять содержание страницы, не меняя шаблон
from .models import Category, Product, Variation

from django.db.models import Q #позволяет делать запрос в бд через OR (обычно ищет так, чтобы все требования совпали)

class IndexView (TemplateView): #Первая страница при заходе, генерируется автоматически и выдается пользователю
    template_name = 'main/base.html'

    def get_context_data (self, **kwargs): #контекст сам по себе словарь, который передает информацию из Python в HTML
        context = super.get_context_data(**kwargs) #Стандартные сгенерированные Django данные, которые передаются сюда
        context['categories'] = Category.objects.all()#выводит все существующие категории
        context['current_category'] = None #по умолчанию ничего не выбрано
        return context
    
    def get(self, request, *args, **kwargs): #с помощью этого метода получаются шаблоны
        context = self.get_context_data (**kwargs) #вызов предыдущего метода, чтобы получить все категории
        #Проверка на динамическую подгрузку
        if request.headers.get ('HX.Request'):
            return TemplateResponse(request, 'main/home_content.html', context)#Если да, то отдаем кусочек страницы
        #Если обычный заход, то отдаем страницу целиком
        return TemplateResponse(request, self.template_name, context)
    
#Работа с маппингом
class CatalogView(TemplateView):
    template_name = 'main/base.html'

    #Словарь параметров-флагов, отвечающих за сортировку
    FILTER_MAPPING = {
        #queryset - массив с продуктами
        'manufacturer': lambda queryset, value : queryset.filter(manufacturer__iexact=value), #__iexact=value - что человек выбрал в сортировке
        'min_price': lambda queryset, value : queryset.filter(price_gte=value),
        'max_price': lambda queryset, value : queryset.filter(manufacturer_lte=value),
        'variation': lambda queryset, value : queryset.filter(product_variation__variation__name=value),
    }

    #По сути в методе достаем элементы из бд, с которыми будем взаимодействовать
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug') #для фильтрации по категории
        categories = Category.objects.all()
        products = Product.objects.all().order_by("-created_at")
        current_category = None

        #Если человек выбрал категорию в запросе url, то пытаемся прочитать ее и отсортировать по ней
        if category_slug:
            current_category = get_object_or_404(Category, slug = category_slug)
            products = products.filter(category=current_category)

        query =self.request.Get.get('q')#Поиск по url
        if query: 
            #Если есть параметр с q-запроса, то стараемся найти в названии или описании его и отсортировать по нему
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        #Перехватывает параметр по которому должна идти сортировка и ищет среди уже созданных нами сортировок
        filter_params = {}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.Get.get(param)
            if value:
                #Передаем в функцию продукт и параметр по которому будем сортироват, например, цвет
                products = filter_func(products, value) 
                filter_params[param] =value
            #Если фильтрации нет, то ее нет
            else:
                filter_params[param] = ''
        filter_params['q'] = query or ''
        #Обновление контекста (массива данных, которые мы будем выводить)
        context.update({
            'categories': categories,
            'products': products,
            #фильтрация по slug идет
            'current_category' : category_slug,
            'filter_params' : filter_params,
            #Чтобы фильтровать по вариантам нужно вывести и добавить в контекст процессора?
            'variations' : Variation.objects.all(),
            #Запоминание поиска
            'search_queary' : query or ''
        })

        #Отделение поиска от обычного каталога
        if self.request.GET.get('show_search') == 'true':
            context['show_search'] = True
        elif self.request.Get.get('reset_search') == 'true':
            context['reset_search'] = True
        return context
    
    #Получение от сервера бэк части страницы
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            if context.get('show_search'):
                #Где хотим вводить поиск на сайте
                return TemplateResponse(request, 'main/search_input')
            elif context.get('reset_search'):
                #При любом выводе возвращается шаблон ответа через запрос
                return TemplateResponse(request, 'main/search_buttom.html',{})
            #Все параметры фильтрации для каталога, когда пользователь пытается воспользоваться фильтром он создает Get запрос, который перехватывается
            template = 'main/filter_modal.html' if  request.Get.get('show_filters') == 'true' else 'main/catalog'
            return TemplateResponse(request, template, context)
        return TemplateResponse(request, self.template_name, context)
    
#В класс передаем встроенный метод для просмотра страниц
class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/base.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Запрос в бд для товара, self - это тело запроса(request)
        product = self.get_object()
        context['categories'] = Category.objects.all()
        context['related_products'] = Product.objects.filter(
            #Для рекомендации товаров
            Category = product.category
        ).exclude(id=product.id)[:4]
        context['current_category'] = product.category.slug
        return context
    
    def get(self, request, *args, **kwargs):
        #Получение товара, который будем показывать
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        #Если запрос из HTMX
        if request.headers.get('HX-Request'):
            #Возвращаем шаблон модуля, который встаиваем в base.html
            return TemplateResponse(request, 'main/product_detail.html', context)
        raise TemplateResponse(request, self.template_name, context)