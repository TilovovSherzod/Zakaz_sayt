# """
# Asosiy ilova ko'rinishlari
# """
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.db.models import Q, Sum, Count
# from django.contrib import messages
# from django.views.decorators.http import require_POST
# from django.utils import timezone
# from django.db import transaction
# import json
# import uuid
# import datetime
#
# from .models import Kategoriya, Maxsulot, Savat, SavatMaxsulot, Buyurtma, BuyurtmaMaxsulot, Savdo, SavdoMaxsulot, OmborHarakati
#
# def asosiy(request):
#     """Asosiy sahifa ko'rinishi"""
#     kategoriyalar = Kategoriya.objects.all()
#     maxsulotlar = Maxsulot.objects.filter(mavjud=True)
#
#     # Kategoriya bo'yicha filtrlash
#     kategoriya_id = request.GET.get('kategoriya')
#     if kategoriya_id:
#         maxsulotlar = maxsulotlar.filter(kategoriya_id=kategoriya_id)
#
#     # Qidiruv
#     qidiruv = request.GET.get('qidiruv')
#     if qidiruv:
#         maxsulotlar = maxsulotlar.filter(
#             Q(nomi__icontains=qidiruv) | Q(tavsif__icontains=qidiruv) | Q(barcode__icontains=qidiruv)
#         )
#
#     # Savatni olish
#     savat = savat_olish(request)
#     savat_maxsulotlar_soni = sum(item.miqdor for item in savat.savatlar.all())
#
#     return render(request, 'asosiy/asosiy.html', {
#         'kategoriyalar': kategoriyalar,
#         'maxsulotlar': maxsulotlar,
#         'savat_maxsulotlar_soni': savat_maxsulotlar_soni,
#     })
#
# def maxsulot_tafsilotlari(request, maxsulot_id):
#     """Maxsulot tafsilotlari sahifasi"""
#     maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id, mavjud=True)
#
#     # O'xshash maxsulotlar
#     oxshash_maxsulotlar = Maxsulot.objects.filter(
#         kategoriya=maxsulot.kategoriya,
#         mavjud=True
#     ).exclude(id=maxsulot_id)[:4]
#
#     # Savatni olish
#     savat = savat_olish(request)
#     savat_maxsulotlar_soni = sum(item.miqdor for item in savat.savatlar.all())
#
#     return render(request, 'asosiy/maxsulot_tafsilotlari.html', {
#         'maxsulot': maxsulot,
#         'oxshash_maxsulotlar': oxshash_maxsulotlar,
#         'savat_maxsulotlar_soni': savat_maxsulotlar_soni,
#     })
#
# def savat_olish(request):
#     """Foydalanuvchi savatini olish yoki yaratish"""
#     if request.user.is_authenticated:
#         # Ro'yxatdan o'tgan foydalanuvchi uchun
#         savat, yaratilgan = Savat.objects.get_or_create(foydalanuvchi=request.user, defaults={'sessiya_id': None})
#     else:
#         # Ro'yxatdan o'tmagan foydalanuvchi uchun
#         sessiya_id = request.session.get('savat_id')
#         if not sessiya_id:
#             # Yangi sessiya ID yaratish
#             sessiya_id = str(uuid.uuid4())
#             request.session['savat_id'] = sessiya_id
#
#         savat, yaratilgan = Savat.objects.get_or_create(sessiya_id=sessiya_id, defaults={'foydalanuvchi': None})
#
#     return savat
#
# @require_POST
# def savatga_qoshish(request):
#     """Maxsulotni savatga qo'shish"""
#     data = json.loads(request.body)
#     maxsulot_id = data.get('maxsulot_id')
#     miqdor = int(data.get('miqdor', 1))
#
#     # Maxsulotni tekshirish
#     maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id, mavjud=True)
#
#     # Savatni olish
#     savat = savat_olish(request)
#
#     # Maxsulotni savatga qo'shish yoki yangilash
#     savat_maxsulot, yaratilgan = SavatMaxsulot.objects.get_or_create(
#         savat=savat,
#         maxsulot=maxsulot,
#         defaults={'miqdor': miqdor}
#     )
#
#     if not yaratilgan:
#         # Agar maxsulot allaqachon savatda bo'lsa, miqdorini yangilash
#         savat_maxsulot.miqdor += miqdor
#         savat_maxsulot.save()
#
#     # Savatdagi maxsulotlar sonini qaytarish
#     savat_maxsulotlar_soni = sum(item.miqdor for item in savat.savatlar.all())
#
#     return JsonResponse({
#         'success': True,
#         'savat_maxsulotlar_soni': savat_maxsulotlar_soni,
#         'maxsulot_nomi': maxsulot.nomi
#     })
#
# def savat(request):
#     """Savat sahifasi"""
#     savat = savat_olish(request)
#     savat_maxsulotlar = savat.savatlar.all()
#
#     return render(request, 'asosiy/savat.html', {
#         'savat': savat,
#         'savat_maxsulotlar': savat_maxsulotlar,
#     })
#
# @require_POST
# def savat_yangilash(request):
#     """Savatdagi maxsulot miqdorini yangilash"""
#     data = json.loads(request.body)
#     maxsulot_id = data.get('maxsulot_id')
#     miqdor = int(data.get('miqdor', 1))
#
#     # Savatni olish
#     savat = savat_olish(request)
#
#     try:
#         savat_maxsulot = SavatMaxsulot.objects.get(savat=savat, maxsulot_id=maxsulot_id)
#
#         if miqdor > 0:
#             savat_maxsulot.miqdor = miqdor
#             savat_maxsulot.save()
#         else:
#             savat_maxsulot.delete()
#
#         # Yangilangan ma'lumotlarni qaytarish
#         return JsonResponse({
#             'success': True,
#             'jami_narx': float(savat.jami_narx),
#             'maxsulotlar_soni': savat.maxsulotlar_soni
#         })
#     except SavatMaxsulot.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Maxsulot topilmadi'})
#
# @require_POST
# def savat_tozalash(request):
#     """Savatni to'liq tozalash"""
#     savat = savat_olish(request)
#     savat.savatlar.all().delete()
#
#     return JsonResponse({'success': True})
#
# def buyurtma_yaratish(request):
#     """Buyurtma yaratish sahifasi"""
#     savat = savat_olish(request)
#
#     if savat.savatlar.count() == 0:
#         messages.error(request, "Savatda maxsulotlar yo'q")
#         return redirect('savat')
#
#     if request.method == 'POST':
#         # Buyurtma ma'lumotlarini olish
#         ism = request.POST.get('ism')
#         familiya = request.POST.get('familiya')
#         telefon = request.POST.get('telefon')
#         manzil = request.POST.get('manzil')
#         tolov_usuli = request.POST.get('tolov_usuli')
#
#         # Buyurtma yaratish
#         buyurtma = Buyurtma.objects.create(
#             foydalanuvchi=request.user if request.user.is_authenticated else None,
#             ism=ism,
#             familiya=familiya,
#             telefon=telefon,
#             manzil=manzil,
#             tolov_usuli=tolov_usuli,
#             jami_narx=savat.jami_narx
#         )
#
#         # Savatdagi maxsulotlarni buyurtmaga ko'chirish
#         for savat_maxsulot in savat.savatlar.all():
#             BuyurtmaMaxsulot.objects.create(
#                 buyurtma=buyurtma,
#                 maxsulot=savat_maxsulot.maxsulot,
#                 miqdor=savat_maxsulot.miqdor,
#                 narx=savat_maxsulot.maxsulot.chegirma_narx or savat_maxsulot.maxsulot.narx
#             )
#
#         # Savatni tozalash
#         savat.savatlar.all().delete()
#
#         # Buyurtma tasdiqlandi xabarini ko'rsatish
#         messages.success(request, "Buyurtmangiz muvaffaqiyatli qabul qilindi!")
#         return redirect('buyurtma_tasdiqlandi', buyurtma_id=buyurtma.id)
#
#     return render(request, 'asosiy/buyurtma_yaratish.html', {
#         'savat': savat,
#     })
#
# def buyurtma_tasdiqlandi(request, buyurtma_id):
#     """Buyurtma tasdiqlandi sahifasi"""
#     buyurtma = get_object_or_404(Buyurtma, id=buyurtma_id)
#
#     # Faqat o'z buyurtmasini ko'rish mumkin
#     if request.user.is_authenticated and buyurtma.foydalanuvchi and buyurtma.foydalanuvchi != request.user:
#         messages.error(request, "Siz bu buyurtmani ko'rish huquqiga ega emassiz")
#         return redirect('asosiy')
#
#     return render(request, 'asosiy/buyurtma_tasdiqlandi.html', {
#         'buyurtma': buyurtma,
#     })
#
# @login_required
# def buyurtmalarim(request):
#     """Foydalanuvchi buyurtmalari sahifasi"""
#     buyurtmalar = Buyurtma.objects.filter(foydalanuvchi=request.user).order_by('-yaratilgan_sana')
#
#     return render(request, 'asosiy/buyurtmalarim.html', {
#         'buyurtmalar': buyurtmalar,
#     })
#
# # Yangi ko'rinishlar
# @login_required
# def kassa(request):
#     """Kassa sahifasi - barcode skaner orqali maxsulotlarni sotish"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     # Joriy savdo uchun sessiya yaratish
#     if 'kassa_savdo' not in request.session:
#         request.session['kassa_savdo'] = []
#
#     # Sessiyadan savdo ma'lumotlarini olish
#     savdo_maxsulotlari = request.session['kassa_savdo']
#
#     # Jami narxni hisoblash
#     jami_narx = sum(item['jami_narx'] for item in savdo_maxsulotlari)
#
#     return render(request, 'asosiy/kassa.html', {
#         'savdo_maxsulotlari': savdo_maxsulotlari,
#         'jami_narx': jami_narx,
#     })
#
# @login_required
# @require_POST
# def barcode_qidirish(request):
#     """Barcode orqali maxsulotni qidirish"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         return JsonResponse({'success': False, 'error': 'Ruxsat yo\'q'})
#
#     data = json.loads(request.body)
#     barcode = data.get('barcode')
#
#     try:
#         maxsulot = Maxsulot.objects.get(barcode=barcode, mavjud=True)
#
#         # Omborda yetarli miqdor borligini tekshirish
#         if maxsulot.miqdor <= 0:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'Maxsulot "{maxsulot.nomi}" omborda mavjud emas'
#             })
#
#         # Sessiyadan savdo ma'lumotlarini olish
#         savdo_maxsulotlari = request.session.get('kassa_savdo', [])
#
#         # Maxsulot allaqachon savdoda borligini tekshirish
#         maxsulot_mavjud = False
#         for item in savdo_maxsulotlari:
#             if item['maxsulot_id'] == maxsulot.id:
#                 # Miqdorni oshirish
#                 item['miqdor'] += 1
#                 item['jami_narx'] = float(maxsulot.chegirma_narx or maxsulot.narx) * item['miqdor']
#                 maxsulot_mavjud = True
#                 break
#
#         # Agar maxsulot savdoda bo'lmasa, qo'shish
#         if not maxsulot_mavjud:
#             savdo_maxsulotlari.append({
#                 'maxsulot_id': maxsulot.id,
#                 'nomi': maxsulot.nomi,
#                 'narx': float(maxsulot.chegirma_narx or maxsulot.narx),
#                 'miqdor': 1,
#                 'jami_narx': float(maxsulot.chegirma_narx or maxsulot.narx),
#             })
#
#         # Sessiyani yangilash
#         request.session['kassa_savdo'] = savdo_maxsulotlari
#
#         # Jami narxni hisoblash
#         jami_narx = sum(item['jami_narx'] for item in savdo_maxsulotlari)
#
#         return JsonResponse({
#             'success': True,
#             'maxsulot': {
#                 'id': maxsulot.id,
#                 'nomi': maxsulot.nomi,
#                 'narx': float(maxsulot.chegirma_narx or maxsulot.narx),
#                 'miqdor': 1,
#             },
#             'savdo_maxsulotlari': savdo_maxsulotlari,
#             'jami_narx': jami_narx,
#         })
#     except Maxsulot.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Maxsulot topilmadi'})
#
# @login_required
# @require_POST
# def savdo_yaratish(request):
#     """Savdoni yakunlash va saqlash"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     # Sessiyadan savdo ma'lumotlarini olish
#     savdo_maxsulotlari = request.session.get('kassa_savdo', [])
#
#     if not savdo_maxsulotlari:
#         messages.error(request, "Savdoda maxsulotlar yo'q")
#         return redirect('kassa')
#
#     # Savdo ma'lumotlarini olish
#     mijoz_ismi = request.POST.get('mijoz_ismi', '')
#     tolov_usuli = request.POST.get('tolov_usuli', 'naqd')
#
#     # Jami narxni hisoblash
#     jami_narx = sum(item['jami_narx'] for item in savdo_maxsulotlari)
#
#     # Tranzaksiya boshlanishi
#     with transaction.atomic():
#         # Savdo yaratish
#         savdo = Savdo.objects.create(
#             kassir=request.user,
#             mijoz_ismi=mijoz_ismi,
#             jami_narx=jami_narx,
#             tolov_usuli=tolov_usuli,
#         )
#
#         # Savdo maxsulotlarini yaratish
#         for item in savdo_maxsulotlari:
#             maxsulot = Maxsulot.objects.get(id=item['maxsulot_id'])
#             SavdoMaxsulot.objects.create(
#                 savdo=savdo,
#                 maxsulot=maxsulot,
#                 miqdor=item['miqdor'],
#                 narx=item['narx'],
#             )
#
#     # Sessiyani tozalash
#     request.session['kassa_savdo'] = []
#
#     messages.success(request, "Savdo muvaffaqiyatli yakunlandi!")
#     return redirect('kassa')
#
# @login_required
# def hisobotlar(request):
#     """Hisobotlar sahifasi"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     return render(request, 'asosiy/hisobotlar.html')
#
# @login_required
# def savdo_hisoboti(request):
#     """Savdo hisoboti sahifasi"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     # Sana oralig'ini olish
#     boshlanish_sana = request.GET.get('boshlanish_sana')
#     tugash_sana = request.GET.get('tugash_sana')
#
#     # Bugungi sana
#     bugun = timezone.now().date()
#
#     # Agar sana berilmagan bo'lsa, joriy oyni olish
#     if not boshlanish_sana:
#         boshlanish_sana = bugun.replace(day=1).strftime('%Y-%m-%d')
#     if not tugash_sana:
#         tugash_sana = bugun.strftime('%Y-%m-%d')
#
#     # Sana oralig'i bo'yicha savdolarni olish
#     savdolar = Savdo.objects.filter(
#         yaratilgan_sana__date__gte=boshlanish_sana,
#         yaratilgan_sana__date__lte=tugash_sana
#     ).order_by('-yaratilgan_sana')
#
#     # Jami savdo summasi
#     jami_savdo = savdolar.aggregate(Sum('jami_narx'))['jami_narx__sum'] or 0
#
#     # Savdo usuli bo'yicha statistika
#     tolov_usuli_statistika = savdolar.values('tolov_usuli').annotate(
#         soni=Count('id'),
#         jami=Sum('jami_narx')
#     )
#
#     # Kassir bo'yicha statistika
#     kassir_statistika = savdolar.values('kassir__username').annotate(
#         soni=Count('id'),
#         jami=Sum('jami_narx')
#     )
#
#     # Eng ko'p sotilgan maxsulotlar
#     eng_kop_sotilgan = SavdoMaxsulot.objects.filter(
#         savdo__yaratilgan_sana__date__gte=boshlanish_sana,
#         savdo__yaratilgan_sana__date__lte=tugash_sana
#     ).values('maxsulot__nomi').annotate(
#         jami_miqdor=Sum('miqdor'),
#         jami_narx=Sum('narx')
#     ).order_by('-jami_miqdor')[:10]
#
#     return render(request, 'asosiy/savdo_hisoboti.html', {
#         'savdolar': savdolar,
#         'jami_savdo': jami_savdo,
#         'boshlanish_sana': boshlanish_sana,
#         'tugash_sana': tugash_sana,
#         'tolov_usuli_statistika': tolov_usuli_statistika,
#         'kassir_statistika': kassir_statistika,
#         'eng_kop_sotilgan': eng_kop_sotilgan,
#     })
#
# @login_required
# def ombor_hisoboti(request):
#     """Ombor hisoboti sahifasi"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     # Kategoriya bo'yicha filtrlash
#     kategoriya_id = request.GET.get('kategoriya')
#
#     # Maxsulotlarni olish
#     maxsulotlar = Maxsulot.objects.all()
#
#     if kategoriya_id:
#         maxsulotlar = maxsulotlar.filter(kategoriya_id=kategoriya_id)
#
#     # Qidiruv
#     qidiruv = request.GET.get('qidiruv')
#     if qidiruv:
#         maxsulotlar = maxsulotlar.filter(
#             Q(nomi__icontains=qidiruv) | Q(barcode__icontains=qidiruv)
#         )
#
#     # Kategoriyalarni olish
#     kategoriyalar = Kategoriya.objects.all()
#
#     # Ombordagi jami maxsulotlar soni
#     jami_maxsulotlar = maxsulotlar.count()
#
#     # Ombordagi jami maxsulotlar qiymati
#     jami_qiymat = sum(maxsulot.miqdor * (maxsulot.chegirma_narx or maxsulot.narx) for maxsulot in maxsulotlar)
#
#     # Tugayotgan maxsulotlar (miqdori 10 dan kam)
#     tugayotgan_maxsulotlar = maxsulotlar.filter(miqdor__lt=10, miqdor__gt=0)
#
#     # Tugagan maxsulotlar (miqdori 0)
#     tugagan_maxsulotlar = maxsulotlar.filter(miqdor=0)
#
#     return render(request, 'asosiy/ombor_hisoboti.html', {
#         'maxsulotlar': maxsulotlar,
#         'kategoriyalar': kategoriyalar,
#         'jami_maxsulotlar': jami_maxsulotlar,
#         'jami_qiymat': jami_qiymat,
#         'tugayotgan_maxsulotlar': tugayotgan_maxsulotlar,
#         'tugagan_maxsulotlar': tugagan_maxsulotlar,
#     })
#
# @login_required
# def ombor(request):
#     """Ombor sahifasi"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     # Kategoriya bo'yicha filtrlash
#     kategoriya_id = request.GET.get('kategoriya')
#
#     # Maxsulotlarni olish
#     maxsulotlar = Maxsulot.objects.all()
#
#     if kategoriya_id:
#         maxsulotlar = maxsulotlar.filter(kategoriya_id=kategoriya_id)
#
#     # Qidiruv
#     qidiruv = request.GET.get('qidiruv')
#     if qidiruv:
#         maxsulotlar = maxsulotlar.filter(
#             Q(nomi__icontains=qidiruv) | Q(barcode__icontains=qidiruv)
#         )
#
#     # Kategoriyalarni olish
#     kategoriyalar = Kategoriya.objects.all()
#
#     return render(request, 'asosiy/ombor.html', {
#         'maxsulotlar': maxsulotlar,
#         'kategoriyalar': kategoriyalar,
#     })
#
# @login_required
# def ombor_kirim(request):
#     """Ombor kirim sahifasi"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     if request.method == 'POST':
#         maxsulot_id = request.POST.get('maxsulot_id')
#         miqdor = int(request.POST.get('miqdor', 0))
#         izoh = request.POST.get('izoh', '')
#
#         if miqdor <= 0:
#             messages.error(request, "Miqdor 0 dan katta bo'lishi kerak")
#             return redirect('ombor_kirim')
#
#         maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id)
#
#         # Ombor harakatini yaratish
#         OmborHarakati.objects.create(
#             maxsulot=maxsulot,
#             harakat_turi='kirim',
#             miqdor=miqdor,
#             izoh=izoh,
#             foydalanuvchi=request.user
#         )
#
#         messages.success(request, f"{maxsulot.nomi} maxsuloti uchun {miqdor} ta kirim muvaffaqiyatli amalga oshirildi")
#         return redirect('ombor')
#
#     # Maxsulotlarni olish
#     maxsulotlar = Maxsulot.objects.all()
#
#     return render(request, 'asosiy/ombor_kirim.html', {
#         'maxsulotlar': maxsulotlar,
#     })
#
# @login_required
# def ombor_chiqim(request):
#     """Ombor chiqim sahifasi"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     if request.method == 'POST':
#         maxsulot_id = request.POST.get('maxsulot_id')
#         miqdor = int(request.POST.get('miqdor', 0))
#         izoh = request.POST.get('izoh', '')
#
#         if miqdor <= 0:
#             messages.error(request, "Miqdor 0 dan katta bo'lishi kerak")
#             return redirect('ombor_chiqim')
#
#         maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id)
#
#         # Omborda yetarli miqdor borligini tekshirish
#         if maxsulot.miqdor < miqdor:
#             messages.error(request, f"Omborda yetarli miqdor yo'q. Mavjud: {maxsulot.miqdor}")
#             return redirect('ombor_chiqim')
#
#         # Ombor harakatini yaratish
#         OmborHarakati.objects.create(
#             maxsulot=maxsulot,
#             harakat_turi='chiqim',
#             miqdor=miqdor,
#             izoh=izoh,
#             foydalanuvchi=request.user
#         )
#
#         messages.success(request, f"{maxsulot.nomi} maxsuloti uchun {miqdor} ta chiqim muvaffaqiyatli amalga oshirildi")
#         return redirect('ombor')
#
#     # Maxsulotlarni olish
#     maxsulotlar = Maxsulot.objects.all()
#
#     return render(request, 'asosiy/ombor_chiqim.html', {
#         'maxsulotlar': maxsulotlar,
#     })
#
# @login_required
# def ombor_inventarizatsiya(request):
#     """Ombor inventarizatsiya sahifasi"""
#     # Faqat staff foydalanuvchilar kirishi mumkin
#     if not request.user.is_staff:
#         messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
#         return redirect('asosiy')
#
#     if request.method == 'POST':
#         maxsulot_id = request.POST.get('maxsulot_id')
#         miqdor = int(request.POST.get('miqdor', 0))
#         izoh = request.POST.get('izoh', '')
#
#         if miqdor < 0:
#             messages.error(request, "Miqdor 0 dan katta yoki teng bo'lishi kerak")
#             return redirect('ombor_inventarizatsiya')
#
#         maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id)
#
#         # Ombor harakatini yaratish
#         OmborHarakati.objects.create(
#             maxsulot=maxsulot,
#             harakat_turi='inventarizatsiya',
#             miqdor=miqdor,
#             izoh=izoh,
#             foydalanuvchi=request.user
#         )
#
#         messages.success(request, f"{maxsulot.nomi} maxsuloti uchun inventarizatsiya muvaffaqiyatli amalga oshirildi")
#         return redirect('ombor')
#
#     # Maxsulotlarni olish
#     maxsulotlar = Maxsulot.objects.all()
#
#     return render(request, 'asosiy/ombor_inventarizatsiya.html', {
#         'maxsulotlar': maxsulotlar,
#     })
#


"""
Asosiy ilova ko'rinishlari
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
import json
import uuid
import datetime

from .models import Kategoriya, Maxsulot, Savat, SavatMaxsulot, Buyurtma, BuyurtmaMaxsulot, Savdo, SavdoMaxsulot, \
    OmborHarakati


def asosiy(request):
    """Asosiy sahifa ko'rinishi"""
    kategoriyalar = Kategoriya.objects.all()
    maxsulotlar = Maxsulot.objects.filter(mavjud=True)

    # Kategoriya bo'yicha filtrlash
    kategoriya_id = request.GET.get('kategoriya')
    if kategoriya_id:
        maxsulotlar = maxsulotlar.filter(kategoriya_id=kategoriya_id)

    # Qidiruv
    qidiruv = request.GET.get('qidiruv')
    if qidiruv:
        maxsulotlar = maxsulotlar.filter(
            Q(nomi__icontains=qidiruv) | Q(tavsif__icontains=qidiruv) | Q(barcode__icontains=qidiruv)
        )

    # Savatni olish
    savat = savat_olish(request)
    savat_maxsulotlar_soni = sum(item.miqdor for item in savat.savatlar.all())

    return render(request, 'asosiy/asosiy.html', {
        'kategoriyalar': kategoriyalar,
        'maxsulotlar': maxsulotlar,
        'savat_maxsulotlar_soni': savat_maxsulotlar_soni,
    })


def maxsulot_tafsilotlari(request, maxsulot_id):
    """Maxsulot tafsilotlari sahifasi"""
    maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id, mavjud=True)

    # O'xshash maxsulotlar
    oxshash_maxsulotlar = Maxsulot.objects.filter(
        kategoriya=maxsulot.kategoriya,
        mavjud=True
    ).exclude(id=maxsulot_id)[:4]

    # Savatni olish
    savat = savat_olish(request)
    savat_maxsulotlar_soni = sum(item.miqdor for item in savat.savatlar.all())

    return render(request, 'asosiy/maxsulot_tafsilotlari.html', {
        'maxsulot': maxsulot,
        'oxshash_maxsulotlar': oxshash_maxsulotlar,
        'savat_maxsulotlar_soni': savat_maxsulotlar_soni,
    })


def savat_olish(request):
    """Foydalanuvchi savatini olish yoki yaratish"""
    if request.user.is_authenticated:
        # Ro'yxatdan o'tgan foydalanuvchi uchun
        savat, yaratilgan = Savat.objects.get_or_create(foydalanuvchi=request.user, defaults={'sessiya_id': None})
    else:
        # Ro'yxatdan o'tmagan foydalanuvchi uchun
        sessiya_id = request.session.get('savat_id')
        if not sessiya_id:
            # Yangi sessiya ID yaratish
            sessiya_id = str(uuid.uuid4())
            request.session['savat_id'] = sessiya_id

        savat, yaratilgan = Savat.objects.get_or_create(sessiya_id=sessiya_id, defaults={'foydalanuvchi': None})

    return savat


@require_POST
def savatga_qoshish(request):
    """Maxsulotni savatga qo'shish"""
    data = json.loads(request.body)
    maxsulot_id = data.get('maxsulot_id')
    miqdor = int(data.get('miqdor', 1))

    # Maxsulotni tekshirish
    maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id, mavjud=True)

    # Savatni olish
    savat = savat_olish(request)

    # Maxsulotni savatga qo'shish yoki yangilash
    savat_maxsulot, yaratilgan = SavatMaxsulot.objects.get_or_create(
        savat=savat,
        maxsulot=maxsulot,
        defaults={'miqdor': miqdor}
    )

    if not yaratilgan:
        # Agar maxsulot allaqachon savatda bo'lsa, miqdorini yangilash
        savat_maxsulot.miqdor += miqdor
        savat_maxsulot.save()

    # Savatdagi maxsulotlar sonini qaytarish
    savat_maxsulotlar_soni = sum(item.miqdor for item in savat.savatlar.all())

    return JsonResponse({
        'success': True,
        'savat_maxsulotlar_soni': savat_maxsulotlar_soni,
        'maxsulot_nomi': maxsulot.nomi
    })


def savat(request):
    """Savat sahifasi"""
    savat = savat_olish(request)
    savat_maxsulotlar = savat.savatlar.all()

    return render(request, 'asosiy/savat.html', {
        'savat': savat,
        'savat_maxsulotlar': savat_maxsulotlar,
    })


@require_POST
def savat_yangilash(request):
    """Savatdagi maxsulot miqdorini yangilash"""
    data = json.loads(request.body)
    maxsulot_id = data.get('maxsulot_id')
    miqdor = int(data.get('miqdor', 1))

    # Savatni olish
    savat = savat_olish(request)

    try:
        savat_maxsulot = SavatMaxsulot.objects.get(savat=savat, maxsulot_id=maxsulot_id)

        if miqdor > 0:
            savat_maxsulot.miqdor = miqdor
            savat_maxsulot.save()
        else:
            savat_maxsulot.delete()

        # Yangilangan ma'lumotlarni qaytarish
        return JsonResponse({
            'success': True,
            'jami_narx': float(savat.jami_narx),
            'maxsulotlar_soni': savat.maxsulotlar_soni
        })
    except SavatMaxsulot.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Maxsulot topilmadi'})


@require_POST
def savat_tozalash(request):
    """Savatni to'liq tozalash"""
    savat = savat_olish(request)
    savat.savatlar.all().delete()

    return JsonResponse({'success': True})


def buyurtma_yaratish(request):
    """Buyurtma yaratish sahifasi"""
    savat = savat_olish(request)

    if savat.savatlar.count() == 0:
        messages.error(request, "Savatda maxsulotlar yo'q")
        return redirect('savat')

    if request.method == 'POST':
        # Buyurtma ma'lumotlarini olish
        ism = request.POST.get('ism')
        familiya = request.POST.get('familiya')
        telefon = request.POST.get('telefon')
        manzil = request.POST.get('manzil')
        tolov_usuli = request.POST.get('tolov_usuli')

        # Ombordagi miqdorni tekshirish
        yetarli_miqdor = True
        for savat_maxsulot in savat.savatlar.all():
            if savat_maxsulot.maxsulot.miqdor < savat_maxsulot.miqdor:
                messages.error(request,
                               f"{savat_maxsulot.maxsulot.nomi} maxsuloti omborda yetarli emas. Mavjud: {savat_maxsulot.maxsulot.miqdor}")
                yetarli_miqdor = False
                break

        if not yetarli_miqdor:
            return redirect('savat')

        # Buyurtma yaratish
        buyurtma = Buyurtma.objects.create(
            foydalanuvchi=request.user if request.user.is_authenticated else None,
            ism=ism,
            familiya=familiya,
            telefon=telefon,
            manzil=manzil,
            tolov_usuli=tolov_usuli,
            jami_narx=savat.jami_narx
        )

        # Savatdagi maxsulotlarni buyurtmaga ko'chirish
        for savat_maxsulot in savat.savatlar.all():
            BuyurtmaMaxsulot.objects.create(
                buyurtma=buyurtma,
                maxsulot=savat_maxsulot.maxsulot,
                miqdor=savat_maxsulot.miqdor,
                narx=savat_maxsulot.maxsulot.chegirma_narx or savat_maxsulot.maxsulot.narx
            )

        # Savatni tozalash
        savat.savatlar.all().delete()

        # Buyurtma tasdiqlandi xabarini ko'rsatish
        messages.success(request, "Buyurtmangiz muvaffaqiyatli qabul qilindi!")
        return redirect('buyurtma_tasdiqlandi', buyurtma_id=buyurtma.id)

    return render(request, 'asosiy/buyurtma_yaratish.html', {
        'savat': savat,
    })


def buyurtma_tasdiqlandi(request, buyurtma_id):
    """Buyurtma tasdiqlandi sahifasi"""
    buyurtma = get_object_or_404(Buyurtma, id=buyurtma_id)

    # Faqat o'z buyurtmasini ko'rish mumkin
    if request.user.is_authenticated and buyurtma.foydalanuvchi and buyurtma.foydalanuvchi != request.user:
        messages.error(request, "Siz bu buyurtmani ko'rish huquqiga ega emassiz")
        return redirect('asosiy')

    return render(request, 'asosiy/buyurtma_tasdiqlandi.html', {
        'buyurtma': buyurtma,
    })


@login_required
def buyurtmalarim(request):
    """Foydalanuvchi buyurtmalari sahifasi"""
    buyurtmalar = Buyurtma.objects.filter(foydalanuvchi=request.user).order_by('-yaratilgan_sana')

    return render(request, 'asosiy/buyurtmalarim.html', {
        'buyurtmalar': buyurtmalar,
    })


# Yangi ko'rinishlar
@login_required
def kassa(request):
    """Kassa sahifasi - barcode skaner orqali maxsulotlarni sotish"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    # Joriy savdo uchun sessiya yaratish
    if 'kassa_savdo' not in request.session:
        request.session['kassa_savdo'] = []

    # Sessiyadan savdo ma'lumotlarini olish
    savdo_maxsulotlari = request.session['kassa_savdo']

    # Jami narxni hisoblash
    jami_narx = sum(item['jami_narx'] for item in savdo_maxsulotlari)

    return render(request, 'asosiy/kassa.html', {
        'savdo_maxsulotlari': savdo_maxsulotlari,
        'jami_narx': jami_narx,
    })


@login_required
@require_POST
def barcode_qidirish(request):
    """Barcode orqali maxsulotni qidirish"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yo\'q'})

    data = json.loads(request.body)
    barcode = data.get('barcode')

    try:
        maxsulot = Maxsulot.objects.get(barcode=barcode, mavjud=True)

        # Omborda yetarli miqdor borligini tekshirish
        if maxsulot.miqdor <= 0:
            return JsonResponse({
                'success': False,
                'error': f'Maxsulot "{maxsulot.nomi}" omborda mavjud emas'
            })

        # Sessiyadan savdo ma'lumotlarini olish
        savdo_maxsulotlari = request.session.get('kassa_savdo', [])

        # Maxsulot allaqachon savdoda borligini tekshirish
        maxsulot_mavjud = False
        for item in savdo_maxsulotlari:
            if item['maxsulot_id'] == maxsulot.id:
                # Miqdorni oshirish
                item['miqdor'] += 1
                item['jami_narx'] = float(maxsulot.chegirma_narx or maxsulot.narx) * item['miqdor']
                maxsulot_mavjud = True
                break

        # Agar maxsulot savdoda bo'lmasa, qo'shish
        if not maxsulot_mavjud:
            savdo_maxsulotlari.append({
                'maxsulot_id': maxsulot.id,
                'nomi': maxsulot.nomi,
                'narx': float(maxsulot.chegirma_narx or maxsulot.narx),
                'miqdor': 1,
                'jami_narx': float(maxsulot.chegirma_narx or maxsulot.narx),
            })

        # Sessiyani yangilash
        request.session['kassa_savdo'] = savdo_maxsulotlari

        # Jami narxni hisoblash
        jami_narx = sum(item['jami_narx'] for item in savdo_maxsulotlari)

        return JsonResponse({
            'success': True,
            'maxsulot': {
                'id': maxsulot.id,
                'nomi': maxsulot.nomi,
                'narx': float(maxsulot.chegirma_narx or maxsulot.narx),
                'miqdor': 1,
            },
            'savdo_maxsulotlari': savdo_maxsulotlari,
            'jami_narx': jami_narx,
        })
    except Maxsulot.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Maxsulot topilmadi'})


@login_required
@require_POST
def savdo_yaratish(request):
    """Savdoni yakunlash va saqlash"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    # Sessiyadan savdo ma'lumotlarini olish
    savdo_maxsulotlari = request.session.get('kassa_savdo', [])

    if not savdo_maxsulotlari:
        messages.error(request, "Savdoda maxsulotlar yo'q")
        return redirect('kassa')

    # Savdo ma'lumotlarini olish
    mijoz_ismi = request.POST.get('mijoz_ismi', '')
    tolov_usuli = request.POST.get('tolov_usuli', 'naqd')

    # Jami narxni hisoblash
    jami_narx = sum(item['jami_narx'] for item in savdo_maxsulotlari)

    # Ombordagi miqdorni tekshirish
    yetarli_miqdor = True
    for item in savdo_maxsulotlari:
        try:
            maxsulot = Maxsulot.objects.get(id=item['maxsulot_id'])
            if maxsulot.miqdor < item['miqdor']:
                messages.error(request, f"{maxsulot.nomi} maxsuloti omborda yetarli emas. Mavjud: {maxsulot.miqdor}")
                yetarli_miqdor = False
                break
        except Maxsulot.DoesNotExist:
            messages.error(request, f"Maxsulot topilmadi")
            yetarli_miqdor = False
            break

    if not yetarli_miqdor:
        return redirect('kassa')

    # Tranzaksiya boshlanishi
    with transaction.atomic():
        # Savdo yaratish
        savdo = Savdo.objects.create(
            kassir=request.user,
            mijoz_ismi=mijoz_ismi,
            jami_narx=jami_narx,
            tolov_usuli=tolov_usuli,
        )

        # Savdo maxsulotlarini yaratish
        for item in savdo_maxsulotlari:
            maxsulot = Maxsulot.objects.get(id=item['maxsulot_id'])
            SavdoMaxsulot.objects.create(
                savdo=savdo,
                maxsulot=maxsulot,
                miqdor=item['miqdor'],
                narx=item['narx'],
            )

    # Sessiyani tozalash
    request.session['kassa_savdo'] = []

    messages.success(request, "Savdo muvaffaqiyatli yakunlandi!")
    return redirect('kassa')


@login_required
def hisobotlar(request):
    """Hisobotlar sahifasi"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    return render(request, 'asosiy/hisobotlar.html')


@login_required
def savdo_hisoboti(request):
    """Savdo hisoboti sahifasi"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    # Sana oralig'ini olish
    boshlanish_sana = request.GET.get('boshlanish_sana')
    tugash_sana = request.GET.get('tugash_sana')

    # Bugungi sana
    bugun = timezone.now().date()

    # Agar sana berilmagan bo'lsa, joriy oyni olish
    if not boshlanish_sana:
        boshlanish_sana = bugun.replace(day=1).strftime('%Y-%m-%d')
    if not tugash_sana:
        tugash_sana = bugun.strftime('%Y-%m-%d')

    # Sana oralig'i bo'yicha savdolarni olish
    savdolar = Savdo.objects.filter(
        yaratilgan_sana__date__gte=boshlanish_sana,
        yaratilgan_sana__date__lte=tugash_sana
    ).order_by('-yaratilgan_sana')

    # Jami savdo summasi
    jami_savdo = savdolar.aggregate(Sum('jami_narx'))['jami_narx__sum'] or 0

    # Savdo usuli bo'yicha statistika
    tolov_usuli_statistika = savdolar.values('tolov_usuli').annotate(
        soni=Count('id'),
        jami=Sum('jami_narx')
    )

    # Kassir bo'yicha statistika
    kassir_statistika = savdolar.values('kassir__username').annotate(
        soni=Count('id'),
        jami=Sum('jami_narx')
    )

    # Eng ko'p sotilgan maxsulotlar
    eng_kop_sotilgan = SavdoMaxsulot.objects.filter(
        savdo__yaratilgan_sana__date__gte=boshlanish_sana,
        savdo__yaratilgan_sana__date__lte=tugash_sana
    ).values('maxsulot__nomi').annotate(
        jami_miqdor=Sum('miqdor'),
        jami_narx=Sum('narx')
    ).order_by('-jami_miqdor')[:10]

    return render(request, 'asosiy/savdo_hisoboti.html', {
        'savdolar': savdolar,
        'jami_savdo': jami_savdo,
        'boshlanish_sana': boshlanish_sana,
        'tugash_sana': tugash_sana,
        'tolov_usuli_statistika': tolov_usuli_statistika,
        'kassir_statistika': kassir_statistika,
        'eng_kop_sotilgan': eng_kop_sotilgan,
    })


@login_required
def ombor_hisoboti(request):
    """Ombor hisoboti sahifasi"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    # Kategoriya bo'yicha filtrlash
    kategoriya_id = request.GET.get('kategoriya')

    # Maxsulotlarni olish
    maxsulotlar = Maxsulot.objects.all()

    if kategoriya_id:
        maxsulotlar = maxsulotlar.filter(kategoriya_id=kategoriya_id)

    # Qidiruv
    qidiruv = request.GET.get('qidiruv')
    if qidiruv:
        maxsulotlar = maxsulotlar.filter(
            Q(nomi__icontains=qidiruv) | Q(barcode__icontains=qidiruv)
        )

    # Kategoriyalarni olish
    kategoriyalar = Kategoriya.objects.all()

    # Ombordagi jami maxsulotlar soni
    jami_maxsulotlar = maxsulotlar.count()

    # Ombordagi jami maxsulotlar qiymati
    jami_qiymat = sum(maxsulot.miqdor * (maxsulot.chegirma_narx or maxsulot.narx) for maxsulot in maxsulotlar)

    # Tugayotgan maxsulotlar (miqdori 10 dan kam)
    tugayotgan_maxsulotlar = maxsulotlar.filter(miqdor__lt=10, miqdor__gt=0)

    # Tugagan maxsulotlar (miqdori 0)
    tugagan_maxsulotlar = maxsulotlar.filter(miqdor=0)

    return render(request, 'asosiy/ombor_hisoboti.html', {
        'maxsulotlar': maxsulotlar,
        'kategoriyalar': kategoriyalar,
        'jami_maxsulotlar': jami_maxsulotlar,
        'jami_qiymat': jami_qiymat,
        'tugayotgan_maxsulotlar': tugayotgan_maxsulotlar,
        'tugagan_maxsulotlar': tugagan_maxsulotlar,
    })


@login_required
def ombor(request):
    """Ombor sahifasi"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    # Kategoriya bo'yicha filtrlash
    kategoriya_id = request.GET.get('kategoriya')

    # Maxsulotlarni olish
    maxsulotlar = Maxsulot.objects.all()

    if kategoriya_id:
        maxsulotlar = maxsulotlar.filter(kategoriya_id=kategoriya_id)

    # Qidiruv
    qidiruv = request.GET.get('qidiruv')
    if qidiruv:
        maxsulotlar = maxsulotlar.filter(
            Q(nomi__icontains=qidiruv) | Q(barcode__icontains=qidiruv)
        )

    # Kategoriyalarni olish
    kategoriyalar = Kategoriya.objects.all()

    return render(request, 'asosiy/ombor.html', {
        'maxsulotlar': maxsulotlar,
        'kategoriyalar': kategoriyalar,
    })


@login_required
def ombor_kirim(request):
    """Ombor kirim sahifasi"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    if request.method == 'POST':
        maxsulot_id = request.POST.get('maxsulot_id')
        miqdor = int(request.POST.get('miqdor', 0))
        izoh = request.POST.get('izoh', '')

        if miqdor <= 0:
            messages.error(request, "Miqdor 0 dan katta bo'lishi kerak")
            return redirect('ombor_kirim')

        maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id)

        # Ombor harakatini yaratish
        OmborHarakati.objects.create(
            maxsulot=maxsulot,
            harakat_turi='kirim',
            miqdor=miqdor,
            izoh=izoh,
            foydalanuvchi=request.user
        )

        messages.success(request, f"{maxsulot.nomi} maxsuloti uchun {miqdor} ta kirim muvaffaqiyatli amalga oshirildi")
        return redirect('ombor')

    # Maxsulotlarni olish
    maxsulotlar = Maxsulot.objects.all()

    return render(request, 'asosiy/ombor_kirim.html', {
        'maxsulotlar': maxsulotlar,
    })


@login_required
def ombor_chiqim(request):
    """Ombor chiqim sahifasi"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    if request.method == 'POST':
        maxsulot_id = request.POST.get('maxsulot_id')
        miqdor = int(request.POST.get('miqdor', 0))
        izoh = request.POST.get('izoh', '')

        if miqdor <= 0:
            messages.error(request, "Miqdor 0 dan katta bo'lishi kerak")
            return redirect('ombor_chiqim')

        maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id)

        # Omborda yetarli miqdor borligini tekshirish
        if maxsulot.miqdor < miqdor:
            messages.error(request, f"Omborda yetarli miqdor yo'q. Mavjud: {maxsulot.miqdor}")
            return redirect('ombor_chiqim')

        # Ombor harakatini yaratish
        OmborHarakati.objects.create(
            maxsulot=maxsulot,
            harakat_turi='chiqim',
            miqdor=miqdor,
            izoh=izoh,
            foydalanuvchi=request.user
        )

        messages.success(request, f"{maxsulot.nomi} maxsuloti uchun {miqdor} ta chiqim muvaffaqiyatli amalga oshirildi")
        return redirect('ombor')

    # Maxsulotlarni olish
    maxsulotlar = Maxsulot.objects.all()

    return render(request, 'asosiy/ombor_chiqim.html', {
        'maxsulotlar': maxsulotlar,
    })


@login_required
def ombor_inventarizatsiya(request):
    """Ombor inventarizatsiya sahifasi"""
    # Faqat staff foydalanuvchilar kirishi mumkin
    if not request.user.is_staff:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q")
        return redirect('asosiy')

    if request.method == 'POST':
        maxsulot_id = request.POST.get('maxsulot_id')
        miqdor = int(request.POST.get('miqdor', 0))
        izoh = request.POST.get('izoh', '')

        if miqdor < 0:
            messages.error(request, "Miqdor 0 dan katta yoki teng bo'lishi kerak")
            return redirect('ombor_inventarizatsiya')

        maxsulot = get_object_or_404(Maxsulot, id=maxsulot_id)

        # Ombor harakatini yaratish
        OmborHarakati.objects.create(
            maxsulot=maxsulot,
            harakat_turi='inventarizatsiya',
            miqdor=miqdor,
            izoh=izoh,
            foydalanuvchi=request.user
        )

        messages.success(request, f"{maxsulot.nomi} maxsuloti uchun inventarizatsiya muvaffaqiyatli amalga oshirildi")
        return redirect('ombor')

    # Maxsulotlarni olish
    maxsulotlar = Maxsulot.objects.all()

    return render(request, 'asosiy/ombor_inventarizatsiya.html', {
        'maxsulotlar': maxsulotlar,
    })

