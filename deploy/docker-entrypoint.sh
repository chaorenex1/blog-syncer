#!/usr/bin/env bash
# 容器内启动脚本（已调整为默认启动 celery beat + worker）
# 用法: 通过环境变量 ROLE 来选择要运行的进程：
#   ROLE=web        -> 启动 uvicorn HTTP 服务
#   ROLE=worker     -> 只启动 celery worker
#   ROLE=celery     -> 启动 celery beat（后台）和 celery worker（前台）  <-- 默认
#   ROLE=both       -> 启动 web（后台）并启动 celery worker（前台）
# 可选环境变量：
#   MIGRATE=true    -> 如果安装了 alembic，则在启动前运行数据库迁移（alembic upgrade head）
#   WAIT_FOR=host:port -> 在启动前等待指定的 TCP 服务可达（可多次用逗号分隔）
#   APP_PORT        -> web 服务端口，默认 5006
#   CELERY_EXTRA_ARGS, CELERY_BEAT_EXTRA_ARGS -> 额外的 celery 参数

set -euo pipefail

APP_DIR="/app"
VENV_PY="$APP_DIR/.venv/bin/python"

log() { echo "[INFO]    $*"; }
warn() { echo "[WARN]    $*"; }
err() { echo "[ERROR]   $*"; }

start_web() {
  PORT=${APP_PORT:-5006}
  log "启动 web 服务 (uvicorn) 在 0.0.0.0:${PORT}"
  if [ -x "$VENV_PY" ]; then
    exec "$VENV_PY" -m uvicorn app:app --host 0.0.0.0 --port "$PORT"
  else
    log "没有找到虚拟环境，尝试直接用系统 python"
    exec python -m uvicorn app:app --host 0.0.0.0 --port "$PORT"
  fi
}

start_celery_beat() {
  log "启动 celery beat"
  BEAT_CMD=("-m" "celery" "-A" "celery_app" "beat" "-l" "info")
  if [ -n "${CELERY_BEAT_EXTRA_ARGS:-}" ]; then
    read -ra extra <<< "$CELERY_BEAT_EXTRA_ARGS"
    BEAT_CMD=("-m" "celery" "-A" "celery_app" "beat" "-l" "info" "${extra[@]}")
  fi
  if [ -x "$VENV_PY" ]; then
    "$VENV_PY" "${BEAT_CMD[@]}" &
  else
    python "${BEAT_CMD[@]}" &
  fi
  beat_pid=$!
  log "celery beat pid=$beat_pid"
}

start_celery_worker() {
  log "启动 celery worker"
  CELERY_CMD=("-m" "celery" "-A" "celery_app" "worker" "-l" "info")
  if [ -n "${CELERY_EXTRA_ARGS:-}" ]; then
    read -ra extra <<< "$CELERY_EXTRA_ARGS"
    CELERY_CMD=("-m" "celery" "-A" "celery_app" "worker" "-l" "info" "${extra[@]}")
  fi
  if [ -x "$VENV_PY" ]; then
    "$VENV_PY" "${CELERY_CMD[@]}" &
  else
    python "${CELERY_CMD[@]}" &
  fi
  child_pid=$!
  log "celery worker pid=$child_pid"
  wait "$child_pid"
  return $?
}

# Trap and forward signals to child processes
child_pid=0
beat_pid=0
term_handler() {
  log "收到终止信号，清理子进程"
  if [ "$child_pid" -ne 0 ]; then
    log "发送 SIGTERM 到 worker ($child_pid)"
    kill -TERM "$child_pid" 2>/dev/null || true
  fi
  if [ "$beat_pid" -ne 0 ]; then
    log "发送 SIGTERM 到 beat ($beat_pid)"
    kill -TERM "$beat_pid" 2>/dev/null || true
  fi
  # 等待子进程结束
  wait || true
  exit 0
}
trap term_handler SIGTERM SIGINT

# main
ROLE=${ROLE:-celery}
log "容器启动，ROLE=$ROLE"

case "$ROLE" in
  web)
    start_web
    ;;
  worker)
    start_celery_worker
    ;;
  celery)
    # 启动 beat（后台）并启动 worker（前台等待）
    start_celery_beat
    start_celery_worker
    ;;
  *)
    err "未知 ROLE: $ROLE. 支持的值: web | worker | celery | both"
    exit 2
    ;;
esac
