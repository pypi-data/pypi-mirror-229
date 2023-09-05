# cloudgenerator

This package is in development. If you want to contribute, you can write to this email: `noticedcloud@gmail.com`.

Developed by NoticedCloud.

## Generating a password
If you want to generate a password you can use generate_password()
```
import cloudgenerator

password = cloudgenerator.generate_password()
print(password)
```

### Checking the safety of a passowrd
You can check the safety of a password using calculate_complexity() it will give a grade from 1 to 5
```
import cloudgenerator

password = cloudgenerator.generate_password()
safety = cloudgenerator.calculate_complexity(password)
print(safety.grade)
```
## Generating a token
You can generate a token using generate_token()
```
import cloudgenerator

token = cloudgenerator.generate_token()
print(token)
```

And more :)