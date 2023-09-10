class Suggestion():
    def __init__(self, date, accuracy):
        self.date = date
        self.accuracy = accuracy

    def __eq__(self, other):
        return self.date == other.date and self.accuracy == other.accuracy
    
    def __lt__(self, other):
        return self.accuracy < other.accuracy
    
    def __hash__(self):
        return hash(('date', self.date, 'accuracy', self.accuracy))
    
    def listify(self):
        return (
            self.date,
            self.accuracy,
        )