import secrets
import string
class randomStr:
    def __init__(self,rand):
        self.rand=rand;

    def __rand__(self):
        return ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(self.rand))



