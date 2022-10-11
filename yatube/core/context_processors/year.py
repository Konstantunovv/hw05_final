import datetime


def year(request):
    # Добавляем переменную с текущим годом.
    year = datetime.date.today().year
    return {
        "year": year,
    }
