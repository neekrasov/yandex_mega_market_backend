from rest_framework.response import Response


def custom_response(status_code: int, message: str) -> Response:
    return Response({
        'code': status_code,
        'message': message,
    }, status=status_code)
