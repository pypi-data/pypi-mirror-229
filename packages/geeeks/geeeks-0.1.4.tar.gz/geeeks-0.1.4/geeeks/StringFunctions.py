class StringFunctions:
    def __init__(self):
        pass
    def reverse(data):
        return "".join(list(data)[::-1])
    
    def make_link(line):
        return "-".join(line.lower().split(" "))
    
    def swap_case(string):
        string = list(string)
        for i in range(len(string)):
            if(string[i].isupper()):
                string[i] = string[i].lower()
            elif(string[i].islower()):
                string[i] = string[i].upper()
        
        return "".join(string)
    
    def make_chunks(string,k):
        return [string[i:i+k] for i in range(0,len(string),k)]