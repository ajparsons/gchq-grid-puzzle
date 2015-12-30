'''

Brute forces the solution to the first part of the GCHQ Christmas Puzzle

http://www.gchq.gov.uk/press_and_media/news_and_features/Pages/Directors-Christmas-puzzle-2015.aspx

'''
from itertools import izip_longest,izip
from PIL import Image


def get_combo(slots,size,starting=[]):
    """
    given the number of slots and how many items to distribute
    - produce a list of all possible combinations where 
    that number of slots adds up to levels
    """
    items = []
    if len(starting) < slots :
        items = []
        """
        first and last slots can be empty
        """
        if starting == [] or len(starting) == slots-1:
            start = 0
        else:
            start = 1
         
        count = sum(starting)
        if count < size:    
            for x in range(start,size+1):
                if count + x <= size:
                    items.extend(get_combo(slots,size,starting=list(starting) + [x]))
        elif count == size and start == 0:
            items.append(list(starting) + [0])
            
    else:
        if sum(starting) == size:
            return [starting]
        else:
            return []
    return items
            

            
            
class Grid(object):
    
    def __init__(self):
        self.rows = []
        self.cols = []
        
        
    def print_global_count(self):
        print self.global_count()
        
    def global_count(self):
        return sum([x.option_count() for x in self.rows + self.cols])
    
    def rows_complete(self):
        return sum([x.option_count() for x in self.rows]) == len(self.rows)
                   
    
                   
    def result(self):
        self.rows.sort(key=lambda x:x.position)
        options = []
        for r in self.rows:
            if len(r.options) == 1:
                options.append(r.options[0].value)
            elif r.restrict:
                options.append(r.restrict)
            else:
                options.append("0000000000000000000000000")
                
        for o in options:
            print o
        return options
    
    def process(self):
        
        self.print_global_count()
        
        while self.rows_complete() == False:
            for r in self.rows:
                r.check_against(self.cols)
                self.print_global_count()
        
        return self.result()
    
class Option(object):
    """
    
    """
    def __init__(self,pattern,white_space):
        self.value = ""
        self.valid = True
        
        for w,p in izip_longest(white_space,pattern):
            if w:
                self.value += "".join(["0" for x in range(0,w)])
            if p:
                self.value += "".join(["1" for x in range(0,p)])
        assert len(self.value) == 25
            
    def __str__(self):
        return self.value
    
    def check_against(self,foreign_options,our_position,their_position):
        """
        if non of the farside match our patterns, discard them
        """
        match = False
        for f in foreign_options:
            if f.valid and self.check_single(f,our_position,their_position):
                match = True
                break
            
        if match == False:
            self.valid = False
                
    def check_single(self,other_option,our_position,their_position):
        return self.value[their_position - 1] == other_option.value[our_position-1]
            
    def match_restriction(self,restrict):
        """
        does the hint given match this option?
        """
        for o,r in izip(self.value,restrict):
            if r == "1" and o == "0":
                return False
        return True                
        
        
            
class Side(object):
    """
    contains the hints, any known locations and all possible options that result from these.
    """
    ROW = 1
    COLUMN = 2
    grid = None
    
    @classmethod
    def set_grid(cls,grid):
        cls.grid = grid    

    def desc(self):
        if self.type == self.__class__.ROW:
            return "row {0}".format(self.position)
        else:
            return "column {0}".format(self.position)

    def print_opts(self):
        for o in self.options:
            print o

    def __init__(self,pattern,position,restrict=None):
        
        if restrict:
            assert len(restrict) == 25
        self.pattern = pattern
        self.total = sum(pattern)
        self.unassigned = 25-self.total
        self.req_slots = len(self.pattern) +1
        self.position = position
        self.options = []
        self.restrict = restrict
        
        print "creating {0}".format(self.desc())
        
        self.generate_options()
        print "{0} options".format(self.option_count())
        
        self.register()
    
    def option_count(self):
        return len(self.options)        

    def register(self):
        """
        associate with the global grid
        """
        cls = self.__class__
        if cls.grid:
            if self.type == cls.ROW:
                cls.grid.rows.append(self)
            else:
                cls.grid.cols.append(self)

    def generate_options(self):
        """
        generate all valid options
        """        
        white_space = get_combo(self.req_slots,self.unassigned)
        self.options = [Option(self.pattern,w) for w in white_space]
        if self.restrict:
            self.options = [x for x in self.options if x.match_restriction(self.restrict)]
                
    def check_against(self,sides,no_backsies=False):
        """
        reduce our matches to only the ones that are capable of matching all those on the other axis
        """
        
        for s in sides:
            for o in self.options:
                    o.check_against(s.options,self.position,s.position)

            self.options = [x for x in self.options if x.valid]
            
            if len(self.options) == 0:
                raise ValueError("{0} ran out of options at {1}?".format(self.desc(),s.desc()))
        
        if no_backsies == False:
            for s in sides:
                s.check_against([self], no_backsies=True)
            
    def print_options(self):
        for o in self.options:
            print o
    
class Row(Side):
    """
    subclassing these for tidyness of the input
    """
    
    def __init__(self,*args,**kwargs):
        self.type = self.__class__.ROW
        super(Row,self).__init__(*args,**kwargs)

class Col(Side):
    """
    subclassing these for tidyness of the input
    """    
    def __init__(self,*args,**kwargs):
        self.type = self.__class__.COLUMN
        super(Col,self).__init__(*args,**kwargs)

def make_image(grid):
    img = Image.new( 'RGB', (250,250), "black") 
    pixels = img.load()
    
    for i in range(25):
        for j in range(25):
            if grid[i][j] == "0":
                value = (255,255,255)
            else:
                value = (0, 0, 0)
            
            for x in range(10): #make all squares 10x10 pixels
                for y in range(10):
                    pixels[j*10+x,i*10+y] = value          
    
    img.show()

if __name__ == "__main__":
    
    g = Grid()
    Side.set_grid(g) # all new rows and columns will add themselves to this grid
    
    Row([7,3,1,1,7],position=1)
    Row([1,1,2,2,1,1],position=2)
    Row([1,3,1,3,1,1,3,1],position=3)
    Row([1,3,1,1,6,1,3,1],position=4,restrict="0001100000001100000001000")
    Row([1,3,1,5,2,1,3,1],position=5)
    Row([1,1,2,1,1],position=6)
    Row([7,1,1,1,1,1,7],position=7)
    Row([3,3],position=8)
    Row([1,2,3,1,1,3,1,1,2],position=9,restrict="0000001100100011001000000")
    Row([1,1,3,2,1,1],position=10)
    Row([4,1,4,2,1,2],position=11)
    Row([1,1,1,1,1,4,1,3],position=12)
    Row([2,1,1,1,2,5],position=13)
    Row([3,2,2,6,3,1],position=14)
    Row([1,9,1,1,2,1],position=15)
    Row([2,1,2,2,3,1],position=16)
    Row([3,1,1,1,1,5,1],position=17,restrict="0000001000010000100010000")
    Row([1,2,2,5],position=18)
    Row([7,1,2,1,1,1,3],position=19)
    Row([1,1,2,1,2,2,1],position=20)
    Row([1,3,1,4,5,1],position=21)
    Row([1,3,1,3,10,2],position=22,restrict="0001100001100001000011000")
    Row([1,3,1,1,6,6],position=23)
    Row([1,1,2,1,1,2],position=24)
    Row([7,2,1,2,5],position=25)
    
    Col([7,2,1,1,7],position=1)
    Col([1,1,2,2,1,1],position=2)
    Col([1,3,1,3,1,3,1,3,1],position=3)
    Col([1,3,1,1,5,1,3,1],position=4)
    Col([1,3,1,1,4,1,3,1],position=5)
    Col([1,1,1,2,1,1],position=6)     
    Col([7,1,1,1,1,1,7],position=7)     
    Col([1,1,3],position=8)     
    Col([2,1,2,1,8,2,1],position=9)     
    Col([2,2,1,2,1,1,1,2],position=10)     
    Col([1,7,3,2,1],position=11)     
    Col([1,2,3,1,1,1,1,1],position=12)     
    Col([4,1,1,2,6],position=13)     
    Col([3,3,1,1,1,3,1],position=14)
    Col([1,2,5,2,2],position=15)     
    Col([2,2,1,1,1,1,1,2,1],position=16)     
    Col([1,3,3,2,1,8,1],position=17)     
    Col([6,2,1],position=18)      
    Col([7,1,4,1,1,3],position=19)     
    Col([1,1,1,1,4],position=20)     
    Col([1,3,1,3,7,1],position=21)     
    Col([1,3,1,1,1,2,1,1,4],position=22)     
    Col([1,3,1,4,3,3],position=23)
    Col([1,1,2,2,2,6,1],position=24)     
    Col([7,1,3,2,1,1],position=25)
    
    result = g.process()
    make_image(result)
