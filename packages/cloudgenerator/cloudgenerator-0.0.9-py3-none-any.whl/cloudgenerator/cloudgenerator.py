import random
import string
import secrets, time
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from Cryptodome.Hash import SHA256
import base64
from cryptography.fernet import Fernet
MAXLENGTH=200
MINLENGTH=200
DEFAULT_CHARACTERS = string.ascii_letters + string.digits + string.punctuation
SET_PRIVATE = False
PRIVATE = None

class Token:
    def __init__(self, token, signed_token, name, signed_name, signed_token_b64):
        self.__signed_token = signed_token
        self.__token = token
        self.__name = name
        self.__signed_name = signed_name
        self.__signed_token_b64 = signed_token_b64

    def __str__(self):
        return f"ntcdtkn<{self.__signed_token}>".replace("b'", "").replace('b"', "")

    def Token(self):
        return f"ntcdtkn<{self.__token}>"

    def token_with_name(self):
        return f"ntcdtkn<{self.__token}:{self.__name}>"
    def token_with_signed_name(self):
        return f"ntcdtkn<{self.__token}:{self.__signed_name}>"
    def signed_token_with_signed_name(self):
        return f"ntcdtkn<{self.__signed_token}:{self.__signed_name}>"
    def signed_token_with_name(self):
        return f"ntcdtkn<{self.__signed_token}:{self.__name}>"
    def signed_token_b64_with_signed_name(self):
        return f"ntcdtkn<{self.__signed_token_b64}:{self.__signed_name}>"
    def signed_token_b64_with_name(self):
        return f"ntcdtkn<{self.__signed_token_b64}:{self.__name}>"
    def signed_token_b64(self):
        return f"ntcdtkn<{self.__signed_token_b64}>"

class Grade:
    def __init__(self, grade):
        self.grade = grade
        try:
            if self.grade == 0:
                __complexity = "too weak"
            elif self.grade  == 1:
                __complexity = "weak"
            elif self.grade  in [2, 3]:
                __complexity = "medium"
            elif self.grade  == 4:
                __complexity = "good"
            elif self.grade  == 5:
                __complexity = "perfect"
        except:
            __complexity = "The grade need to be a Grade variable"
        self.word = __complexity

def generate_key():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    return public_key, private_key

def encrypt_message(message, secret_key):
    cipher_suite = Fernet(secret_key)
    encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
    return encrypted_message

def decrypt_message(encrypted_message, secret_key):
    cipher_suite = Fernet(secret_key)
    decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
    return decrypted_message

def sign_token2(token, private_key):
    signature = base64.b64encode(token.encode('utf-8') + private_key.to_bytes((private_key.bit_length() + 7) // 8, 'big')).decode('utf-8')
    return signature

def verify_token2(token, signature, public_key):
    expected_signature = base64.b64encode(token.encode('utf-8') + public_key.to_bytes((public_key.bit_length() + 7) // 8, 'big')).decode('utf-8')
    return signature == expected_signature


def sign_token(token, private_key):
    h = SHA256.new(token.encode())
    signature = pkcs1_15.new(private_key).sign(h)
    return signature

def verify_token(token, signature, public_key):
    h = SHA256.new(token.encode())
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False 

def calculate_complexity(password, log=False):
    length = len(password)
    has_lower = any(char.islower() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in string.punctuation for char in password)
    
    complexity = 0
    if length >= 8:
        complexity += 1
        if log:
            print("min length: yes")
    else:
        if log:
            print("min length: no")
    if length >= 12:
        complexity += 1
        if log:
            print("medium length: yes")
    else:
        if log:
            print("medium length: no")
    if has_lower and has_upper:
        complexity += 1
        if log:
            print("uppers and lowers: yes")
    else:
        if log:
            print("uppers and lowers: no")
    if has_digit:
        complexity += 1
        if log:
            print("digit: yes")
    else:
        if log:
            print("digit: no")
    if has_special:
        complexity += 1
        if log:
            print("specials: yes")
    else:
        if log:
            print("specials: no")

    Complexity = Grade(complexity)
    return Complexity

def setlength(min_length=None, max_length=None):
    global MAXLENGTH
    global MINLENGTH
    if min_length == None and not max_length == None:
        print("Please specify min_lenght")
        exit(1)
    elif not min_length == None and max_length == None:
        print("Please specify max_lenght")
        exit(1)
    elif min_length == None and max_length == None:
        print("Please specify min_lenght and max_lenght")
        exit(1)
    else:
        MAXLENGTH = max_length
        MINLENGTH = min_length

def generate_password(custom_characters=None):
    length = random.randint(MINLENGTH, MAXLENGTH)
    characters = custom_characters if custom_characters else DEFAULT_CHARACTERS
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def generate_key2(custom_characters=None):
    length = random.randint(MINLENGTH, MAXLENGTH)
    characters = string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def set_private_key(private_key):
    global PRIVATE
    PRIVATE = private_key

def set_private(Boolean):
    global SET_PRIVATE
    SET_PRIVATE = False
    

def generate_token(name="Token", minlength=160, maxlength=300):
    try:
        if PRIVATE != None:
            private_key = PRIVATE
        else:
            public_key, private_key=generate_key()
    except:
        private_key = PRIVATE
    if maxlength > 2000:
        print("Max length need to be less than 2000")
        exit(1)
    if maxlength < 10:
        print("Min length need to be more than 10")
        exit(1)
    
    timestamp = int(time.time() * 1000)  # Multiplicato per 1000 per ottenere millisecondi
    random_part = random.randint(0, 90000)
    unique_token = f"{timestamp}-"
    length = random.randint(minlength, maxlength)
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters + str(random_part)) for _ in range(length))
    
    signed_token = sign_token(token, private_key)  # Firma il token generato
    signed_name = sign_token(name, private_key)
    is_valid = verify_token(token, signed_token, private_key)
    
    secret_key = Fernet.generate_key()
    encrypted_message = encrypt_message(token, secret_key)
    token2 = encrypted_message.decode('utf-8')
    private_key = generate_key2()
    signed_token_b64= sign_token2(token2, int(private_key))
    token: Token = Token(f"{token}", f"{signed_token}", f"{name}", f"{signed_name}", f"{signed_token_b64}")
    if is_valid:
        return token
    else:
        return "Unknown error"

def help():
    print("""help:
    generate password: Generate a safe password,
    generate token: generate a safe and unique token if the token argue dont appear write (vairable_name): cloudgenerator.Token = cloudgenerator.generate_token(),
    set_length: set the length of the password,
    calculate_complexity: calculate the complexity of the password giving a vote of 1 to 5,
    complexity_word: giving the complexity generated with calculate_complexity it will translate the vote into words,
    generate_key: generate a plublic_key and a private_key to use for the token""")