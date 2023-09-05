from string import ascii_lowercase as atoz
from string import ascii_uppercase as AtoZ

class Encryption:
    def caesarCipher(s,k):
        res=""
        for i in list(s):
            if i.isalpha():
                if i.islower():
                    res+=atoz[(atoz.index(i)+k)%26]
                elif i.isupper():
                    res+=AtoZ[(AtoZ.index(i)+k)%26]
            else:
                res=res+i
        return res
    
class Decryption:
    def caesarCipher(s,k):
        res=""
        for i in list(s):
            if i.isalpha():
                if i.islower():
                    res+=atoz[(atoz.index(i)-k)%26]
                elif i.isupper():
                    res+=AtoZ[(AtoZ.index(i)-k)%26]
            else:
                res=res+i
        return res