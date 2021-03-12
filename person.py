
class Person:
    
    def __init__(self, title, pagelink, imagelink, imagedate, birthdate, sex, pageid):
        self.title = title
        self.name = title
        self.pagelink = pagelink
        self.imagelink = imagelink
        self.imagedate = imagedate
        self.birthdate = birthdate
        self.sex = sex
        self.pageid = pageid
    
    def __str__(self):
        return """"<Person: {0}
        birth: {1}
        sex: {2}
        pagelink: {3}
        imagelink: {4}
        imagedate: {5}
        pageid: {6}
        >""".format(
            self.title, self.birthdate, self.sex, self.pagelink, 
            self.imagelink, self.imagedate, self.pageid
            )

    def toDB(self):
        return (self.title, self.birthdate, self.sex, self.pagelink, self.imagelink, self.imagedate, self.pageid)
