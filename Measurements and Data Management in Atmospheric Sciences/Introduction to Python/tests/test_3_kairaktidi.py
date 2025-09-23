list = []

for i in range(1, 101, 1):
    list.append(i) 
    
print("the list is: ", list, "\n")

even = []
odd = []

for i in list:
    if i %2 == 0 :
        even.append(i)
    else:
        odd.append(i)
        
print("the even list is:", even, "\n")
print("the odd list is:",odd)




