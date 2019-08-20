'''
handles any database management/ text file management
for yukinobot
'''
class Manager(object): 
    def __init__(self, filename, mode='r'):
        if mode not in ['r', 'w', 'w+']:
            raise ValueError("For the sake of this project, this manager only\
                supports 'r' or 'w' modes")
        self.filename = filename
        self.mode = mode

    def __str__(self):
        return 'Data Object of {self.filename} with mode {self.mode}'

    __repr__=__str__
        
    def __enter__(self): 
        self.file = open(self.filename, self.mode) 
        return self.file

    def __exit__(self): 
        self.file.close() 
    

