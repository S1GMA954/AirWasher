
class DataList(list):
    def append(self, value):
        if(self.__len__() < 11):      
            super().append(value)
        else:
            self.pop(1)
            super().append(value)
