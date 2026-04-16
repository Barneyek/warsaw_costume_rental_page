from django.contrib import admin
from .models import Category, Tag, Size, Costume, CostumeImage


class CostumeImageInline(admin.TabularInline):
    model = CostumeImage
    extra = 1


@admin.register(Costume)
class CostumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'is_available')
    list_filter = ('is_active', 'is_available', 'categories')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('tags', 'sizes', 'categories')
    inlines = [CostumeImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'parent_category')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    pass
