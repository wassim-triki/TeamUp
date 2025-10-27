from django.http import JsonResponse


def api_index(request):
    return JsonResponse({'status': 'ok', 'service': 'TeamUp API placeholder'})
