from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import QuizAnswer, QuizResult
from Stone.models import StoneCategory, Stone

@login_required
def quiz_start(request):
    return render(request, 'quiz/quiz.html')

@login_required
def quiz_results(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Собираем ответы и считаем баллы
                scores = {
                    'granite': 0,
                    'marble': 0,
                    'quartzite': 0,
                    'travertine': 0,
                    'slate': 0,
                    'onyx': 0
                }
                
                answers_data = {}
                
                # Обрабатываем 8 вопросов
                for i in range(1, 9):
                    answer_key = f'question_{i}'
                    answer_id = request.POST.get(answer_key)
                    
                    if answer_id:
                        answers_data[str(i)] = int(answer_id)
                        
                        # Находим ответ в базе данных по ID
                        try:
                            answer = QuizAnswer.objects.get(id=answer_id)
                            scores['granite'] += answer.granite_weight
                            scores['marble'] += answer.marble_weight
                            scores['quartzite'] += answer.quartzite_weight
                            scores['travertine'] += answer.travertine_weight
                            scores['slate'] += answer.slate_weight
                            scores['onyx'] += answer.onyx_weight
                        except QuizAnswer.DoesNotExist:
                            # Если ответ не найден, пропускаем
                            continue
                
                # Проверяем, что хоть какие-то ответы были получены
                if not answers_data:
                    messages.error(request, 'Не получены ответы на вопросы')
                    return redirect('quiz_start')
                
                # Определяем максимальную категорию
                max_category = max(scores, key=scores.get)
                category_map = {
                    'granite': 'Гранит',
                    'marble': 'Мрамор',
                    'quartzite': 'Кварцит',
                    'travertine': 'Травертин',
                    'slate': 'Сланец',
                    'onyx': 'Оникс'
                }
                recommended_name = category_map.get(max_category, 'Гранит')
                
                # Находим категорию в БД
                try:
                    category = StoneCategory.objects.filter(name__icontains=recommended_name).first()
                except:
                    category = None
                
                # Сохраняем результат
                result = QuizResult.objects.create(
                    user=request.user,
                    first_name=request.user.first_name,
                    last_name=request.user.last_name,
                    email=request.user.email,
                    phone=request.user.phone,
                    answers=answers_data,
                    granite_score=scores['granite'],
                    marble_score=scores['marble'],
                    quartzite_score=scores['quartzite'],
                    travertine_score=scores['travertine'],
                    slate_score=scores['slate'],
                    onyx_score=scores['onyx'],
                    recommended_category=category
                )
                
                # Получаем рекомендуемые камни
                if category:
                    recommended_stones = Stone.objects.filter(category=category, in_stock=True)[:4]
                else:
                    recommended_stones = Stone.objects.filter(in_stock=True)[:4]
                
                context = {
                    'result': result,
                    'scores': scores,
                    'max_category': max_category,
                    'recommended_name': recommended_name,
                    'recommended_stones': recommended_stones
                }
                return render(request, 'quiz/results.html', context)
                
        except Exception as e:
            # Выводим ошибку для отладки
            print(f"Ошибка: {e}")
            messages.error(request, f'Произошла ошибка при обработке результатов: {str(e)}')
            return redirect('quiz_start')
    
    return redirect('quiz_start')