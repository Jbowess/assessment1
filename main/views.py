from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay
from .models import Sensor, SensorEvent
import datetime

def day_of_week_average_count(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return JsonResponse({"error": "Both start_date and end_date are required"}, status=400)

    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    # Filter between start and end dates
    events = SensorEvent.objects.filter(
        event_datetime__range=[start_date, end_date]
    ).annotate(day_of_week=ExtractWeekDay('event_datetime'))

    data = []
    for sensor in Sensor.objects.all():
        sensor_data = {
            "sensor_id": sensor.id,
            "sensor_name": sensor.name
        }
        # counts per day of week
        day_counts = events.filter(sensor=sensor).values('day_of_week').annotate(avg_count=Count('id'))
        days = ['mon_avg_count', 'tue_avg_count', 'wed_avg_count', 'thu_avg_count', 'fri_avg_count', 'sat_avg_count', 'sun_avg_count']
        day_data = {day: 0 for day in days}

        for count in day_counts:
            day_index = (count['day_of_week'] + 5) % 7
            day_name = days[day_index]
            day_data[day_name] = count['avg_count']

        sensor_data.update(day_data)
        data.append(sensor_data) 

    return JsonResponse({"results": data})
