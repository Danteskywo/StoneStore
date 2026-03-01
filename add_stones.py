import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StoneStore.settings')
django.setup()

from Stone.models import StoneCategory, Stone

def create_categories_and_stones():
    print("Создаем категории камней...")
    
    # Создаем категории
    categories = [
        {
            'name': 'Гранит',
            'slug': 'granit',
            'description': 'Гранит - самый прочный и долговечный натуральный камень. Идеален для кухонных столешниц, полов с высокой проходимостью, уличных ступеней. Устойчив к царапинам, кислотам и перепадам температур.',
            'order': 1
        },
        {
            'name': 'Мрамор',
            'slug': 'mramor',
            'description': 'Мрамор - благородный камень с уникальным рисунком. Идеален для ванных комнат, каминов, подоконников. Требует бережного ухода, но создает неповторимую атмосферу роскоши.',
            'order': 2
        },
        {
            'name': 'Кварцит',
            'slug': 'kvarcit',
            'description': 'Кварцит - очень твердый камень, по прочности превосходит гранит. Обладает красивым рисунком и устойчив к высоким температурам. Отлично подходит для кухонь и зон барбекю.',
            'order': 3
        },
        {
            'name': 'Травертин',
            'slug': 'travertin',
            'description': 'Травертин - пористый камень теплых оттенков. Создает уютную атмосферу, идеален для полов, стен, фасадов. Часто используется в средиземноморском стиле.',
            'order': 4
        },
        {
            'name': 'Сланец',
            'slug': 'slanec',
            'description': 'Сланец - слоистый камень с уникальной текстурой. Идеален для полов, стен, каминов. Создает эффект натурального камня в интерьере.',
            'order': 5
        },
        {
            'name': 'Оникс',
            'slug': 'oniks',
            'description': 'Оникс - полудрагоценный камень с потрясающей подсветкой. Пропускает свет, создавая эффект свечения. Идеален для барных стоек, декоративных панно, подсветки.',
            'order': 6
        }
    ]
    
    category_objects = {}
    for cat_data in categories:
        category, created = StoneCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'order': cat_data['order']
            }
        )
        if created:
            print(f"  ✓ Создана категория: {cat_data['name']}")
        else:
            print(f"  ✓ Категория уже существует: {cat_data['name']}")
        category_objects[cat_data['name']] = category
    
    print("\nСоздаем камни...")
    
    # Список камней
    stones = [
        # Граниты
        {
            'name': 'Абсолют Блэк',
            'slug': 'absolut-black',
            'category': 'Гранит',
            'description': 'Изысканный черный гранит с мелкозернистой структурой. Идеально ровный черный цвет без вкраплений. Придает интерьеру строгость и элегантность.',
            'characteristics': 'Очень прочный, устойчив к царапинам, кислотам, перепадам температур. Не впитывает влагу. Сохраняет цвет десятилетиями.',
            'price_per_sqm': 8500,
            'hardness': 7,
            'frost_resistance': True,
            'water_absorption': 0.2,
            'available_finishes': 'Полированная, Матовая',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 150,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Кашмир Голд',
            'slug': 'kashmir-gold',
            'category': 'Гранит',
            'description': 'Роскошный гранит с золотисто-коричневыми вкраплениями на светлом фоне. Напоминает кашемировую ткань. Придает интерьеру тепло и уют.',
            'characteristics': 'Высокая прочность, устойчивость к истиранию, морозостойкость. Не выцветает на солнце. Легко моется.',
            'price_per_sqm': 7200,
            'hardness': 6,
            'frost_resistance': True,
            'water_absorption': 0.3,
            'available_finishes': 'Полированная, Матовая, Термообработанная',
            'available_thickness': '20,30,40',
            'in_stock': True,
            'stock_quantity': 120,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Сибирский Серый',
            'slug': 'sibirskiy-seryy',
            'category': 'Гранит',
            'description': 'Классический серый гранит с равномерной зернистой структурой. Универсальное решение для любого интерьера. Сочетается с любыми цветами.',
            'characteristics': 'Очень плотный, низкое водопоглощение, высокая морозостойкость. Выдерживает большие нагрузки. Подходит для уличного использования.',
            'price_per_sqm': 5500,
            'hardness': 7,
            'frost_resistance': True,
            'water_absorption': 0.15,
            'available_finishes': 'Полированная, Матовая, Пиленая',
            'available_thickness': '20,30,40,50',
            'in_stock': True,
            'stock_quantity': 200,
            'is_popular': False,
            'is_new': False,
        },
        {
            'name': 'Красный Мариинский',
            'slug': 'krasnyy-mariinskiy',
            'category': 'Гранит',
            'description': 'Яркий красный гранит с черными и серыми вкраплениями. Создает акцент в интерьере. Отлично смотрится в больших помещениях.',
            'characteristics': 'Высокая прочность, устойчивость к ударам, морозостойкость. Не боится соли и реагентов. Идеален для фасадов и мощения.',
            'price_per_sqm': 6800,
            'hardness': 7,
            'frost_resistance': True,
            'water_absorption': 0.2,
            'available_finishes': 'Полированная, Лощеная',
            'available_thickness': '20,30,50',
            'in_stock': True,
            'stock_quantity': 80,
            'is_popular': False,
            'is_new': True,
        },
        {
            'name': 'Куру Блэк',
            'slug': 'kuru-black',
            'category': 'Гранит',
            'description': 'Эксклюзивный черный гранит с мелкими серебристыми вкраплениями. Выглядит как ночное небо со звездами. Премиальный выбор для элитных интерьеров.',
            'characteristics': 'Максимальная твердость, нулевое водопоглощение, абсолютная морозостойкость. Не царапается даже металлом. Вечный камень.',
            'price_per_sqm': 12500,
            'hardness': 8,
            'frost_resistance': True,
            'water_absorption': 0.05,
            'available_finishes': 'Полированная, Суперполированная',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 40,
            'is_popular': True,
            'is_new': True,
        },
        
        # Мраморы
        {
            'name': 'Каррара Бьянко',
            'slug': 'carrara-bianco',
            'category': 'Мрамор',
            'description': 'Знаменитый итальянский мрамор из Каррары. Белый фон с изящными серыми прожилками. Эталон классической роскоши.',
            'characteristics': 'Мелкозернистая структура, высокая светопроницаемость. Требует защиты от кислот. Идеален для ванных и каминов.',
            'price_per_sqm': 9500,
            'hardness': 3,
            'frost_resistance': False,
            'water_absorption': 1.2,
            'available_finishes': 'Полированная, Матовая',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 60,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Каллаката',
            'slug': 'kallakata',
            'category': 'Мрамор',
            'description': 'Элитный итальянский мрамор с крупными выразительными прожилками золотистого и серого цвета. Самый престижный мрамор в мире.',
            'characteristics': 'Плотная структура, полупрозрачность, уникальный рисунок. Требует бережного ухода. Используется в люксовых проектах.',
            'price_per_sqm': 18500,
            'hardness': 3,
            'frost_resistance': False,
            'water_absorption': 1.0,
            'available_finishes': 'Полированная',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 25,
            'is_popular': True,
            'is_new': True,
        },
        {
            'name': 'Крема Валенсия',
            'slug': 'krema-valensia',
            'category': 'Мрамор',
            'description': 'Теплый бежевый мрамор с кремовым оттенком. Равномерный фон без ярких прожилок. Создает уютную атмосферу.',
            'characteristics': 'Однородная структура, приятная текстура. Подходит для полов, стен, столешниц. Требует регулярного ухода.',
            'price_per_sqm': 7800,
            'hardness': 3,
            'frost_resistance': False,
            'water_absorption': 1.5,
            'available_finishes': 'Полированная, Матовая',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 90,
            'is_popular': False,
            'is_new': False,
        },
        {
            'name': 'Верде Гватемала',
            'slug': 'verde-gvatemala',
            'category': 'Мрамор',
            'description': 'Редкий зеленый мрамор с белыми и темно-зелеными прожилками. Экзотический вариант для смелых интерьеров.',
            'characteristics': 'Плотный, хорошо полируется. Устойчив к выцветанию. Создает уникальный визуальный эффект.',
            'price_per_sqm': 11200,
            'hardness': 4,
            'frost_resistance': False,
            'water_absorption': 0.9,
            'available_finishes': 'Полированная',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 35,
            'is_popular': False,
            'is_new': True,
        },
        
        # Кварциты
        {
            'name': 'Фантастико Браун',
            'slug': 'fantastiko-brown',
            'category': 'Кварцит',
            'description': 'Невероятно красивый кварцит с коричневыми, бежевыми и серыми переливами. Рисунок напоминает горный пейзаж.',
            'characteristics': 'Очень твердый, практически вечный камень. Устойчив к кислотам, царапинам, высоким температурам. Можно ставить горячее.',
            'price_per_sqm': 14500,
            'hardness': 7,
            'frost_resistance': True,
            'water_absorption': 0.1,
            'available_finishes': 'Полированная',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 30,
            'is_popular': True,
            'is_new': True,
        },
        {
            'name': 'Бьянко Макиято',
            'slug': 'bianco-macchiato',
            'category': 'Кварцит',
            'description': 'Белый кварцит с деликатными серыми разводами. Напоминает мрамор, но прочнее в разы. Идеален для кухонь.',
            'characteristics': 'Высочайшая твердость, низкое водопоглощение. Не боится вина, кофе, лимона. Легко моется.',
            'price_per_sqm': 15800,
            'hardness': 7,
            'frost_resistance': True,
            'water_absorption': 0.1,
            'available_finishes': 'Полированная, Матовая',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 25,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Тайгер Ай',
            'slug': 'tiger-eye',
            'category': 'Кварцит',
            'description': 'Золотисто-коричневый кварцит с шелковистым блеском. Напоминает камень тигровый глаз. Очень эффектный внешний вид.',
            'characteristics': 'Чрезвычайно твердый, устойчив к ударам. Полируется до зеркального блеска. Не тускнеет со временем.',
            'price_per_sqm': 16800,
            'hardness': 8,
            'frost_resistance': True,
            'water_absorption': 0.08,
            'available_finishes': 'Полированная',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 20,
            'is_popular': True,
            'is_new': True,
        },
        
        # Травертины
        {
            'name': 'Навахо',
            'slug': 'navaho',
            'category': 'Травертин',
            'description': 'Травертин песочного цвета с мелкими порами и природным рисунком. Создает атмосферу средиземноморья.',
            'characteristics': 'Пористая структура, легкий вес. Теплый на ощупь. Требует заполнения пор. Идеален для полов, стен, фасадов.',
            'price_per_sqm': 4800,
            'hardness': 3,
            'frost_resistance': True,
            'water_absorption': 2.5,
            'available_finishes': 'Пиленая, Лощеная, Брушированная',
            'available_thickness': '20,30,40',
            'in_stock': True,
            'stock_quantity': 150,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Рома Классико',
            'slug': 'roma-classico',
            'category': 'Травертин',
            'description': 'Классический итальянский травертин кремового цвета. Использовался при строительстве Колизея. Проверен веками.',
            'characteristics': 'Плотный травертин с равномерной структурой. Хорошо держит тепло. Подходит для теплых полов.',
            'price_per_sqm': 6200,
            'hardness': 3,
            'frost_resistance': True,
            'water_absorption': 2.0,
            'available_finishes': 'Пиленая, Лощеная',
            'available_thickness': '20,30,40',
            'in_stock': True,
            'stock_quantity': 100,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Ночной Жемчуг',
            'slug': 'nochnoy-zhemchug',
            'category': 'Травертин',
            'description': 'Травертин темно-серого цвета с перламутровым отливом. Редкий и благородный вариант.',
            'characteristics': 'Плотный, хорошо полируется. Создает эффект мокрого камня. Идеален для ванных комнат.',
            'price_per_sqm': 7200,
            'hardness': 3,
            'frost_resistance': True,
            'water_absorption': 1.8,
            'available_finishes': 'Полированная, Лощеная',
            'available_thickness': '20,30',
            'in_stock': True,
            'stock_quantity': 45,
            'is_popular': False,
            'is_new': True,
        },
        
        # Сланцы
        {
            'name': 'Индийский Черный',
            'slug': 'indian-black',
            'category': 'Сланец',
            'description': 'Черный сланец с графитовым отливом. Имеет естественную слоистую текстуру. Создает драматичный эффект в интерьере.',
            'characteristics': 'Натуральная текстура, не скользит. Устойчив к перепадам температур. Подходит для полов и стен.',
            'price_per_sqm': 4200,
            'hardness': 4,
            'frost_resistance': True,
            'water_absorption': 1.5,
            'available_finishes': 'Натуральный скол, Лощеная',
            'available_thickness': '15,20,30',
            'in_stock': True,
            'stock_quantity': 200,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Зеленый Риф',
            'slug': 'zelenyy-rif',
            'category': 'Сланец',
            'description': 'Зеленовато-серый сланец с волнистым рисунком. Напоминает морскую гладь. Уникальный материал для отделки.',
            'characteristics': 'Природная текстура, нескользящий. Легко колется на пластины. Идеален для фасадов и дорожек.',
            'price_per_sqm': 4800,
            'hardness': 4,
            'frost_resistance': True,
            'water_absorption': 1.3,
            'available_finishes': 'Натуральный скол',
            'available_thickness': '15,20,30',
            'in_stock': True,
            'stock_quantity': 120,
            'is_popular': False,
            'is_new': True,
        },
        
        # Оникс
        {
            'name': 'Медовый',
            'slug': 'medovyy',
            'category': 'Оникс',
            'description': 'Оникс медового цвета с полупрозрачной структурой. При подсветке светится изнутри теплым янтарным светом.',
            'characteristics': 'Полупрозрачный, требует подсветки. Хрупкий, используется в декоративных целях. Создает эффект свечения.',
            'price_per_sqm': 22000,
            'hardness': 3,
            'frost_resistance': False,
            'water_absorption': 2.0,
            'available_finishes': 'Полированная',
            'available_thickness': '15,20',
            'in_stock': True,
            'stock_quantity': 30,
            'is_popular': True,
            'is_new': False,
        },
        {
            'name': 'Белый Мраморный',
            'slug': 'belyy-mramornyy',
            'category': 'Оникс',
            'description': 'Белый полупрозрачный оникс с нежными прожилками. При подсветке создает эффект морозного узора на стекле.',
            'characteristics': 'Высокая светопроницаемость, хрупкий. Требует бережного обращения. Используется для декоративных панно и барных стоек с подсветкой.',
            'price_per_sqm': 25000,
            'hardness': 3,
            'frost_resistance': False,
            'water_absorption': 1.8,
            'available_finishes': 'Полированная',
            'available_thickness': '15,20',
            'in_stock': True,
            'stock_quantity': 20,
            'is_popular': True,
            'is_new': True,
        },
    ]
    
    # Добавляем камни
    created_count = 0
    exists_count = 0
    
    for stone_data in stones:
        category_name = stone_data.pop('category')
        category = category_objects[category_name]
        
        stone, created = Stone.objects.get_or_create(
            slug=stone_data['slug'],
            category=category,
            defaults=stone_data
        )
        
        if created:
            created_count += 1
            print(f"  ✓ Создан камень: {stone_data['name']} ({category_name})")
        else:
            exists_count += 1
            print(f"  • Камень уже существует: {stone_data['name']} ({category_name})")
    
    print(f"\n✅ Готово!")
    print(f"   Создано камней: {created_count}")
    print(f"   Уже существовало: {exists_count}")
    print(f"   Всего камней в базе: {Stone.objects.count()}")

if __name__ == '__main__':
    create_categories_and_stones()