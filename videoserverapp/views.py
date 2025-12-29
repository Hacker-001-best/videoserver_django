import os
import jwt
import time
from django.conf import settings
from django.http import JsonResponse, HttpResponse, FileResponse, Http404,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *


@csrf_exempt
def add_video(request):
    if request.method != "POST":
        return JsonResponse({'succes': False})
    file_path = request.POST.get('file_path')
    teacher_name = request.POST.get("teacher_name")
    video_name = request.POST.get("video_name")
    lesson_name = request.POST.get("lesson_name")
    lesson_category_name = request.POST.get("lesson_category_name")
    user = teacher.objects.get(username=teacher_name)
    if not all([file_path, teacher_name, video_name, lesson_name, lesson_category_name]):
        return JsonResponse({"success": False})
    if (not file_path):
        return JsonResponse({"succes": False})
    try:
        lesson = lessons.objects.get(lesson_name=lesson_name)
        lesson_categorys= lesson_category.objects.get(
            category_name=lesson_category_name)
    except (lessons.DoesNotExist,
            lesson_category.DoesNotExist):
        return JsonResponse({"success": False})

    video_creat = video.objects.create(
        video_name=video_name,
        teacher=user,
        lesson=lesson,
        lesson_category=lesson_categorys,
        video_path=file_path,
    )
    video_creat.save()
    return JsonResponse({"success": True})

@csrf_exempt
def get_video(request):
    teacher_name = request.POST.get("teacher_name")

    user = teacher.objects.get(username=teacher_name)
    videos = video.objects.filter(teacher=user)

    lessons_dict = {}

    for v in videos:
        lesson_name = v.lesson.lesson_name
        lesson_type = v.lesson_category.category_name  # ← ТИП УРОКА
        if lesson_name not in lessons_dict:
            lessons_dict[lesson_name] = {}
        if lesson_type not in lessons_dict[lesson_name]:
            lessons_dict[lesson_name][lesson_type] = []

        lessons_dict[lesson_name][lesson_type].append({
            "id": v.id,
            "video_name": v.video_name,
        })
    return JsonResponse(
        {"lessons_dict": lessons_dict},
        json_dumps_params={"ensure_ascii": False}
    )

@csrf_exempt
def delete_video(request):
    if request.method != "POST":
        return JsonResponse({"success": False})

    data = json.loads(request.body)
    ids = data.get("video_ids", [])
    video.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True})


def get_lessons_and_categories(request):
    lessons_list = list(lessons.objects.values_list("lesson_name", flat=True))
    categories_list = list(lesson_category.objects.values_list("category_name", flat=True))
    return JsonResponse({
        "lessons": lessons_list,
        "categories": categories_list
    })

import os


VIDEO_ROOT = "/home/grandmc/Видео/uploads/"

def stream_video(request, video_id):
    token = request.GET.get("token")
    if not token:
        return HttpResponseForbidden("Token required")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGO]
        )
    except jwt.ExpiredSignatureError:
        return HttpResponseForbidden("Token expired")
    except jwt.InvalidTokenError:
        return HttpResponseForbidden("Invalid token")

    if payload.get("video_id") != video_id:
        return HttpResponseForbidden("Wrong video")
    try:
        v = video.objects.get(id=video_id)
    except video.DoesNotExist:
        raise Http404("Видео не найдено")

    file_path = os.path.join(VIDEO_ROOT, os.path.basename(v.video_path))

    if not os.path.exists(file_path):
        raise Http404("Файл не найден")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range")

    if range_header:
        range_value = range_header.replace("bytes=", "")
        start_str, end_str = range_value.split("-")

        start = int(start_str)
        end = int(end_str) if end_str else min(start + 1024 * 1024, file_size - 1)
        length = end - start + 1

        with open(file_path, "rb") as f:
            f.seek(start)
            data = f.read(length)

        response = HttpResponse(data, status=206, content_type="video/mp4")
        response["Content-Length"] = str(length)
        response["Accept-Ranges"] = "bytes"
        response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        return response

    response = FileResponse(open(file_path, "rb"), content_type="video/mp4")
    response["Content-Length"] = str(file_size)
    response["Accept-Ranges"] = "bytes"
    return response





@csrf_exempt
def get_stream_token(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    video_id = request.POST.get("video_id")
    user = request.POST.get("user")

    if not video_id or not user:
        return JsonResponse({"error": "missing data"}, status=400)

    # можно тут проверить права пользователя
    if not video.objects.filter(id=video_id).exists():
        return JsonResponse({"error": "video not found"}, status=404)

    payload = {
        "video_id": int(video_id),
        "user": user,
        "exp": int(time.time()) + settings.JWT_STREAM_TTL
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

    return JsonResponse({"token": token})

