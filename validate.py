def validate_(inputdata):
    if inputdata == '':
        return " is blank"
    elif len(inputdata)<3:
        return " must be at least 3 characters"
    elif len(inputdata)>20:
        return " exceeds 20 character max"
    else:
        for letter in inputdata:
             if letter == " ":
                 return " cannot contain spaces"
    return ""

def password_verify_same(password, verify):
    if password != verify:
        return " do not match!"
    else:
        return ""

def empty_post(content):
    if not content:
        return False
    return True