from django.contrib import admin

from .models import Category, Variation, Product, ProductImage, ProductVariation

class ProductImageInline (admin.TabularInline):#Параметр обозначает, что я хочу встроить одну модель в другую в админке (если вызывается одна модель, то также будет и другая)
    model = ProductImage
    extra = 1 #Количество пустых записей по умолчанию

class ProductVariationInline (admin.TabularInline):
    model = ProductVariation
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category','variation', 'height', 'width', 'length'] #параметры в таблице, которые будут отображаться в админке
    list_filter = ['category', 'variation']#категории по которым происходит сортировка
    search_fields = ['name', 'category', 'description'] # поля по которым происходит поиск
    prepopulated_fields = {'slug': ('name',)}#поля, которые будут заполняться по заданному принципу автоматически
    inlines = [ProductImageInline, ProductVariationInline] #будут отображаться на странице добавления продуктов

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ['name']

#После того, как все было прописано, классы нужно зарегистровать. Можно с помощью декоратора или так:
admin.site.register(Category, CategoryAdmin)
admin.site.register(Variation, VariationAdmin)#Берем модель (первую) и привязываем к ней настройки, которые сделаны в админ-модели
admin.site.register(Product, ProductAdmin)