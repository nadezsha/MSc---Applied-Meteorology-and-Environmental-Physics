# Sqrt Calculation

a_sq = 16
a1 = a_sq ** .5
print(a1)

# Using a library

import numpy as np

print(np.sqrt(a_sq))

import math
a3 = math.sqrt(a_sq)
print(a3)

# Lists

a = ['alpha', 'bravo', 'charlie', 'delta']
print(a)

b = [1, 2, 3, 4]
print(b)

# Lists are ordered
b = ['bravo', 'alpha', 'charlie', 'delta']
a == b

# Lists can contain arbitrary objects
a = [21.42, 'foobar', 3, 4, 'bark', False, 3.14159]
print(a)

# List elements can be accessed by index
a = ['alpha', 'bravo', 'charlie', 'delta', 'foxtrot', 'echo', 'golf']
print(a[0])
print(a[3])
print(a[-1])
print(a[-3])
print(a[0:3])
print(a[-5:-2])
print(a[0:6])
print(a[0:6:2])
a[:]

# Logical operations
'charlie' in a
'romeo' not in a
'foxtrot' not in a

# Concatenation - replication
a + ['hotel', 'India', 'Juliet']
a*2

# Lists can be nested
x = ['a', ['bb', ['ccc', 'ddd'], 'ee', 'ff'], 'g', ['hh', 'ii'], 'j']
print(x)
print(x[1])  # Sub-list
print(x[3])  # Another sublist
print(x[1][1])
print(x[1][1][1])
print(x[1][1][-2])

# Modifying a single list value
a = ['alpha', 'bravo', 'charlie', 'delta', 'foxtrot', 'echo', 'golf']
a[2] = 10
a[-1] = 20
print(a)

# Deleting values
del a[2]
print(a)
del a[-1]
print(a)

# Inserting values
a = ['alpha', 'bravo', 'charlie', 'delta', 'foxtrot', 'echo', 'golf']
a[1:4] = [1.1, 2.2, 3.3, 4.4, 5.5]
print(a)

# Apending - Prepending items
a = ['charlie', 'delta', 'foxtrot', 'echo', 'golf']
a += ['alpha', 'bravo']
print(a)
a = ['charlie', 'delta', 'foxtrot', 'echo', 'golf']
a = ['alpha', 'bravo'] + a
print(a)

a = ['charlie', 'delta', 'foxtrot', 'echo', 'golf', 'alpha']
a.append('tango')
print(a)

a.extend(['romeo', 'x-ray','papa'])
print(a)

a.insert(3, 'november')
print(a)

a.remove('november')
print(a)

a.pop()
a.pop(-1)
a.pop(1)

# Tupples are immutable

a = ('alpha', 'bravo', 'charlie', 'delta', 'foxtrot', 'echo', 'golf')
print(a)

a[1]
a[0:3]
a[2] = 10

# For loops

a = ['alpha', 'bravo', 'charlie', 'delta', 'foxtrot', 'echo', 'golf']

for i in a:
    print(i)

for n in (0, 1, 2, 3, 4):
    print(n)

for k in range(5):
    print(k)

x = range(5)
print(x)

for i in x:
    print(i)

# Altering if operation
for i in ['alpha', 'bravo', 'charlie', 'delta']:
    if 'b' in i:
        break
    print(i)

for i in ['alpha', 'bravo', 'charlie', 'delta']:
    if 'b' in i:
        continue
    print(i)

for i in ['alpha', 'bravo', 'charlie', 'delta']:
    print(i)
else:
    print('Done')