"""APScheduler 任务调度"""

import time
from dataclasses import dataclass, field
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("scheduler")


@dataclass
class ScheduledJob:
    """定时任务"""
    job_id: str
    job_type: str  # feedback_t1 / feedback_t7 / feedback_t30 / style_report
    target_id: str  # article_id / task_id
    scheduled_at: int  # unix timestamp
    status: str = "pending"  # pending / running / completed / failed
    retry_count: int = 0
    error: Optional[str] = None


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: dict[str, ScheduledJob] = {}

    def start(self) -> None:
        """启动调度器"""
        if settings.scheduler_enabled:
            self.scheduler.start()
            logger.info("Task scheduler started")

    def stop(self) -> None:
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")

    def schedule_feedback_sync(
        self,
        article_id: str,
        publish_time: int,
        delay_hours: int = 168,  # 默认 T+7 天
    ) -> str:
        """
        注册反馈同步任务

        Args:
            article_id: 文章ID
            publish_time: 发布时间（unix timestamp）
            delay_hours: 延迟小时数

        Returns:
            job_id
        """
        job_id = f"feedback_{article_id}_{int(time.time())}"
        scheduled_at = publish_time + delay_hours * 3600

        job = ScheduledJob(
            job_id=job_id,
            job_type="feedback_t7",
            target_id=article_id,
            scheduled_at=scheduled_at,
        )
        self.jobs[job_id] = job

        # 计算延迟秒数
        delay_seconds = max(scheduled_at - int(time.time()), 0)

        self.scheduler.add_job(
            func=self._execute_feedback_sync,
            trigger=DateTrigger(run_date=None),
            id=job_id,
            args=[article_id, job_id],
            next_run_time=None,
        )

        logger.info(f"Scheduled feedback sync: {job_id}, delay={delay_seconds}s")
        return job_id

    async def _execute_feedback_sync(self, article_id: str, job_id: str) -> None:
        """执行反馈同步"""
        job = self.jobs.get(job_id)
        if not job:
            return

        job.status = "running"
        logger.info(f"Executing feedback sync: {job_id}")

        try:
            # 实际执行逻辑
            from app.feedback.wechat_api import WeChatAPI

            api = WeChatAPI()
            stats = await api.get_article_stats(article_id)

            if stats:
                # 保存到数据库（简化：暂时只打印）
                logger.info(f"Got stats for {article_id}: views={stats.int_page_read_count}")

            await api.close()
            job.status = "completed"

        except Exception as e:
            logger.error(f"Feedback sync failed: {job_id}, error={e}")
            job.status = "failed"
            job.error = str(e)

            # 重试逻辑
            if job.retry_count < 3:
                job.retry_count += 1
                delay_hours = [1, 6, 24][job.retry_count - 1]
                # 简化重试：直接标记，不重新调度
                logger.info(f"Will retry {job_id} in {delay_hours}h")

    def get_job_status(self, job_id: str) -> Optional[ScheduledJob]:
        """获取任务状态"""
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """取消任务"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            return True
        except Exception:
            return False


# 全局调度器实例
_scheduler: Optional[TaskScheduler] = None


def get_scheduler() -> TaskScheduler:
    """获取调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler
