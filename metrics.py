# metrics.py - Custom Prometheus Metrics for HR Backend API
"""
Custom business metrics for monitoring the HR Resume Comparator application.
These metrics provide insights into business operations beyond standard HTTP metrics.
"""

from prometheus_client import Counter, Histogram, Gauge, Info

# ============================================
# Application Info
# ============================================
app_info = Info(
    'hr_backend_app',
    'HR Backend API application information'
)
app_info.info({
    'version': '1.0.0',
    'service': 'backend-api',
    'environment': 'production'
})

# ============================================
# Resume Metrics
# ============================================
resume_uploads_total = Counter(
    'hr_resume_uploads_total',
    'Total number of resumes uploaded',
    ['status', 'file_type']  # status: success/failed, file_type: pdf/docx
)

resume_parse_duration = Histogram(
    'hr_resume_parse_duration_seconds',
    'Time spent parsing resume files',
    ['file_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

resumes_total = Gauge(
    'hr_resumes_total',
    'Total number of resumes in the system'
)

# ============================================
# Job Description Metrics
# ============================================
jd_created_total = Counter(
    'hr_job_descriptions_created_total',
    'Total number of job descriptions created',
    ['status']  # status: success/failed
)

jd_total = Gauge(
    'hr_job_descriptions_total',
    'Total number of job descriptions in the system'
)

# ============================================
# Matching/AI Metrics
# ============================================
matching_requests_total = Counter(
    'hr_matching_requests_total',
    'Total number of resume-JD matching requests',
    ['status', 'source']  # status: success/failed, source: manual/auto
)

matching_duration = Histogram(
    'hr_matching_duration_seconds',
    'Time spent on AI matching operations',
    ['batch_size'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0]
)

ai_agent_calls_total = Counter(
    'hr_ai_agent_calls_total',
    'Total calls to AI Agent service',
    ['endpoint', 'status']  # endpoint: compare-batch/extract-resume/extract-jd
)

ai_agent_latency = Histogram(
    'hr_ai_agent_latency_seconds',
    'Latency of AI Agent API calls',
    ['endpoint'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# ============================================
# Match Results Metrics
# ============================================
match_scores = Histogram(
    'hr_match_scores',
    'Distribution of resume match scores',
    buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

candidates_by_fit = Gauge(
    'hr_candidates_by_fit_category',
    'Number of candidates by fit category',
    ['category']  # Best Fit, Partial Fit, Not Fit
)

# ============================================
# User/Auth Metrics
# ============================================
user_logins_total = Counter(
    'hr_user_logins_total',
    'Total user login attempts',
    ['status']  # success/failed
)

active_users = Gauge(
    'hr_active_users',
    'Number of currently active users'
)

user_registrations_total = Counter(
    'hr_user_registrations_total',
    'Total user registrations',
    ['status']
)

# ============================================
# Workflow Metrics
# ============================================
workflows_started_total = Counter(
    'hr_workflows_started_total',
    'Total workflows started',
    ['type']  # manual/scheduled
)

workflows_completed_total = Counter(
    'hr_workflows_completed_total',
    'Total workflows completed',
    ['status']  # success/failed/partial
)

workflow_duration = Histogram(
    'hr_workflow_duration_seconds',
    'Total workflow execution time',
    ['resume_count'],
    buckets=[30, 60, 120, 300, 600, 900, 1800]
)

workflow_in_progress = Gauge(
    'hr_workflows_in_progress',
    'Number of workflows currently in progress'
)

# ============================================
# File Storage Metrics
# ============================================
file_storage_bytes = Gauge(
    'hr_file_storage_bytes',
    'Total file storage used in GridFS',
    ['type']  # resumes/other
)

file_operations_total = Counter(
    'hr_file_operations_total',
    'Total file operations',
    ['operation', 'status']  # operation: upload/download/delete
)

# ============================================
# Database Metrics
# ============================================
db_operations_total = Counter(
    'hr_db_operations_total',
    'Total database operations',
    ['collection', 'operation']  # collection: resume/jd/users, operation: find/insert/update/delete
)

db_operation_duration = Histogram(
    'hr_db_operation_duration_seconds',
    'Database operation latency',
    ['collection', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# ============================================
# Helper Functions
# ============================================
def track_resume_upload(success: bool, file_type: str):
    """Track resume upload metric"""
    status = 'success' if success else 'failed'
    resume_uploads_total.labels(status=status, file_type=file_type).inc()

def track_matching_request(success: bool, source: str = 'manual'):
    """Track matching request metric"""
    status = 'success' if success else 'failed'
    matching_requests_total.labels(status=status, source=source).inc()

def track_ai_agent_call(endpoint: str, success: bool, duration: float):
    """Track AI Agent call metric"""
    status = 'success' if success else 'failed'
    ai_agent_calls_total.labels(endpoint=endpoint, status=status).inc()
    ai_agent_latency.labels(endpoint=endpoint).observe(duration)

def track_match_score(score: float):
    """Track match score distribution"""
    match_scores.observe(score)

def update_fit_categories(best_fit: int, partial_fit: int, not_fit: int):
    """Update fit category gauges"""
    candidates_by_fit.labels(category='Best Fit').set(best_fit)
    candidates_by_fit.labels(category='Partial Fit').set(partial_fit)
    candidates_by_fit.labels(category='Not Fit').set(not_fit)

def track_user_login(success: bool):
    """Track user login metric"""
    status = 'success' if success else 'failed'
    user_logins_total.labels(status=status).inc()

def track_workflow(started: bool = False, completed: bool = False, 
                   status: str = 'success', workflow_type: str = 'manual'):
    """Track workflow metrics"""
    if started:
        workflows_started_total.labels(type=workflow_type).inc()
        workflow_in_progress.inc()
    if completed:
        workflows_completed_total.labels(status=status).inc()
        workflow_in_progress.dec()
