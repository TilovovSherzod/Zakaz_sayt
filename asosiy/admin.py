"""
Admin panel konfiguratsiyasi
"""
from django.contrib import admin
from .models import Kategoriya, Maxsulot, Savat, SavatMaxsulot, Buyurtma, BuyurtmaMaxsulot, Savdo, SavdoMaxsulot, OmborHarakati

@admin.register(Kategoriya)
class KategoriyaAdmin(admin.ModelAdmin):
    """Kategoriya admin konfiguratsiyasi"""
    list_display = ('nomi', 'yaratilgan_sana')
    search_fields = ('nomi',)

class SavatMaxsulotInline(admin.TabularInline):
    """Savat maxsulotlarini ko'rsatish uchun inline"""
    model = SavatMaxsulot
    extra = 0

@admin.register(Savat)
class SavatAdmin(admin.ModelAdmin):
    """Savat admin konfiguratsiyasi"""
    list_display = ('id', 'foydalanuvchi', 'yaratilgan_sana', 'jami_narx', 'maxsulotlar_soni')
    inlines = [SavatMaxsulotInline]

@admin.register(Maxsulot)
class MaxsulotAdmin(admin.ModelAdmin):
    """Maxsulot admin konfiguratsiyasi"""
    list_display = ('nomi', 'kategoriya', 'narx', 'chegirma_narx', 'barcode', 'miqdor', 'mavjud', 'yaratilgan_sana')
    list_filter = ('kategoriya', 'mavjud')
    search_fields = ('nomi', 'tavsif', 'barcode')

class BuyurtmaMaxsulotInline(admin.TabularInline):
    """Buyurtma maxsulotlarini ko'rsatish uchun inline"""
    model = BuyurtmaMaxsulot
    extra = 0
    readonly_fields = ('maxsulot', 'miqdor', 'narx')

@admin.register(Buyurtma)
class BuyurtmaAdmin(admin.ModelAdmin):
    """Buyurtma admin konfiguratsiyasi"""
    list_display = ('id', 'ism', 'familiya', 'telefon', 'holat', 'tolov_usuli', 'jami_narx', 'yaratilgan_sana')
    list_filter = ('holat', 'tolov_usuli', 'yaratilgan_sana')
    search_fields = ('ism', 'familiya', 'telefon')
    readonly_fields = ('jami_narx',)
    inlines = [BuyurtmaMaxsulotInline]

    def get_readonly_fields(self, request, obj=None):
        """Tahrirlash mumkin bo'lmagan maydonlarni belgilash"""
        if obj:  # Agar buyurtma mavjud bo'lsa
            return self.readonly_fields + ('foydalanuvchi', 'ism', 'familiya', 'telefon', 'manzil', 'tolov_usuli')
        return self.readonly_fields

class SavdoMaxsulotInline(admin.TabularInline):
    """Savdo maxsulotlarini ko'rsatish uchun inline"""
    model = SavdoMaxsulot
    extra = 0
    readonly_fields = ('maxsulot', 'miqdor', 'narx')

@admin.register(Savdo)
class SavdoAdmin(admin.ModelAdmin):
    """Savdo admin konfiguratsiyasi"""
    list_display = ('id', 'kassir', 'mijoz_ismi', 'jami_narx', 'tolov_usuli', 'yaratilgan_sana')
    list_filter = ('tolov_usuli', 'yaratilgan_sana', 'kassir')
    search_fields = ('mijoz_ismi',)
    readonly_fields = ('jami_narx',)
    inlines = [SavdoMaxsulotInline]
    date_hierarchy = 'yaratilgan_sana'

@admin.register(OmborHarakati)
class OmborHarakatiAdmin(admin.ModelAdmin):
    """Ombor harakati admin konfiguratsiyasi"""
    list_display = ('maxsulot', 'harakat_turi', 'miqdor', 'foydalanuvchi', 'yaratilgan_sana')
    list_filter = ('harakat_turi', 'yaratilgan_sana', 'foydalanuvchi')
    search_fields = ('maxsulot__nomi', 'izoh')
    date_hierarchy = 'yaratilgan_sana'

