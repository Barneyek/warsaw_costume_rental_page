from rest_framework import serializers
from .models import Category, Tag, Size, Costume, CostumeImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class CostumeImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # "to pole istnieje, liczę je sam"

    class Meta:
        model = CostumeImage
        fields = ['id', 'image_url', 'is_main']

    def get_image_url(self, obj): # "a oto jak je liczę"
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class CostumeListSerializer(serializers.ModelSerializer):
    """Lekki serializer — do listy kostiumów (dużo rekordów)."""
    categories = CategorySerializer(many=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Costume
        fields = ['id', 'name', 'slug', 'price', 'deposit',
                  'is_available', 'categories', 'main_image']

    def get_main_image(self, obj):
        main = obj.images.filter(is_main=True).first()
        if main:
            return CostumeImageSerializer(main, context=self.context).data
        return None


class CostumeDetailSerializer(serializers.ModelSerializer):
    """Pełny serializer — do strony szczegółów jednego kostiumu."""
    categories = CategorySerializer(many=True)
    tags = TagSerializer(many=True)
    sizes = SizeSerializer(many=True)
    images = CostumeImageSerializer(many=True)

    class Meta:
        model = Costume
        fields = ['id', 'name', 'slug', 'description', 'price', 'deposit',
                  'is_available', 'categories', 'tags', 'sizes', 'images']
