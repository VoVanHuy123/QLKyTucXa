from django.http import JsonResponse
import subprocess
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),".env")
load_dotenv(dotenv_path)
def update_code_and_deploy(request):
    # Lấy API token từ biến môi trường
    pa_token = os.getenv("PA_TOKEN")
    if not pa_token:
        return JsonResponse({"error": "PA_TOKEN not set"}, status=403)

    # Chạy file update_code.sh
    result = subprocess.run(
        ["bash", os.path.expanduser("~/update_code.sh")],
        capture_output=True,
        text=True
    )

    return JsonResponse({"stdout": result.stdout, "stderr": result.stderr})
# ================================