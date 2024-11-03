from rest_framework import status
from rest_framework.response import Response


def check_token_match(generated_token, sent_token):
    if sent_token != generated_token:
        return False, Response(
            {"message": "درخواست نامعتبر"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return True, "OK"


def check_code_match(generated_code, sent_code):
    if sent_code != generated_code:
        return False, Response(
            {"message": "کد ارسالی اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
        )

    return True, "OK"
