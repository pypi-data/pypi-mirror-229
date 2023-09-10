def ifact(x):
       f=1
       for i in range(1, x+1):
               f=f*i
       return f
def rfact(n):    
       if n == 1:
               return 1
       else:
               return n * rfact(n-1)