import random
import string

def generate_invite_code():
    from users.models import User 
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not User.objects.filter(invite_code=code).exists():
            return code
