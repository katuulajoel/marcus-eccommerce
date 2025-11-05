"""
Celery tasks for AI assistant
Handles background index updates when database changes
"""

from celery import shared_task
from django.core.cache import cache


@shared_task(name='ai_assistant.rebuild_index')
def rebuild_ai_index():
    """
    Rebuild the AI knowledge index from database.
    This task runs in the background to avoid blocking requests.
    """
    from .services.index_service import get_index_service

    try:
        index_service = get_index_service()
        index_service.rebuild_index()
        return {"status": "success", "message": "AI index rebuilt successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task(name='ai_assistant.update_index')
def update_ai_index():
    """
    Update the AI knowledge index.
    Rebuilds the index from scratch to avoid duplicates when data changes.
    """
    from .services.index_service import get_index_service

    try:
        index_service = get_index_service()
        # Use rebuild_index to delete old collection and avoid duplicates
        index_service.rebuild_index()
        return {"status": "success", "message": "AI index updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task(name='ai_assistant.scheduled_index_refresh')
def scheduled_index_refresh():
    """
    Scheduled task to refresh index periodically.
    Run this daily or weekly to keep index up-to-date.
    """
    # Check if we need to refresh (use cache to avoid too frequent updates)
    last_refresh = cache.get('ai_index_last_refresh')

    if last_refresh is None:
        # First time or cache expired, do the refresh
        result = rebuild_ai_index.delay()
        cache.set('ai_index_last_refresh', 'in_progress', timeout=3600)  # 1 hour lock
        return {"status": "triggered", "task_id": result.id}

    return {"status": "skipped", "reason": "Recent refresh in progress or completed"}
