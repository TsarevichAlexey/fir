from django.db import models

# по сути модели это таблица в бд, чтобы не писать запросы на sql, а делать все на python

from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100) #Charfield модель для вывода символов
    slug = models.CharField(max_length=100) #генерация url для конкретного продукта

    def save(self, *args, **kwargs):
        '''*args - это кортеж с неопределенным количеством аргументов, которые передаются в функцию \test_function(1, 2, 3, 4) \\
        **kwargs - словарь с неопределенным количеством пар \(имя="Иван", возраст=30, город="Берлин")\ '''
        if not self.slug: #если не задали url в админке
            self.slug = slugify(self.name)
        #super это следующий класс в цепочке наследования, то есть родительский класс по отношению к текущему
        # В данном случае это класс моделей (django.db.models.Model)
        super().save(*args, **kwargs)  #метод .save() это у родительского класса, который создает sql запрос и все сопровождающее

    def __str__(self):
        return self.name #возвращает имя категории в админке 
    
class Variation(models.Model):#встроенная функция, которая создает поля/параметры, которые затем через миграцию отправляются в бд
    name = models.CharField()

    def __str__(self):
        return self.name
    
class ProductVariation(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_variant')#удалится товар - удалится связь; product_variant - имя в админке
    variation =  models.ForeignKey(Variation, on_delete=models.CASCADE) #удалится цвет, удалится связь
    stock = models.PositiveIntegerField(default=0)#Количество товара

    def __str__(self):
        return f'{self.variation.name} ({self.stock} in stock) for {self.product.name}' #такой-то цвет в таком-то количестве для такого-то товара


class Product (models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    #ForeignKey берет все параметры, функции класса
    #variation = models.CharField(max_length=100)#параметр default, чтобы не ругался при миграции - создавалось из-за ошибки
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')#Cascade обозначает, что при удалении категории удаляются все объекты этой категории
    height = models.IntegerField(); width = models.IntegerField(); length = models.IntegerField()
    weight = models.DecimalField(max_digits=6,decimal_places=1)
    description = models.TextField(blank=True)#параметр, что поле может быть пустым при заполнении
    #Только главное фото
    main_image = models.ImageField(upload_to='product/main') #Сначала загружается в Media(смотри settings), потом далее по адресу
    created_at = models.DateTimeField(auto_now_add=True)#автоматическое обновление при добавлении товара
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name

#Соединение продукта с его изображением
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/extra') #Добавление любого количества дополнительных фото