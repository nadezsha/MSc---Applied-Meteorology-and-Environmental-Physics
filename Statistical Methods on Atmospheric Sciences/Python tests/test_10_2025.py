import pandas as pd
import scipy

df=pd.read_csv('SMAS_Ithaka_Jan1987.csv',sep=',',index_col=0)
a=0.05
n=31
# Εφόσον έχουμε δεδομένα ενός μήνα τότε n=31 -> πολύ κοντά στο 30 
# οπότε θεωρούμε ότι τα δεδομένα ακολουθούν την κατανομή Student's t.

# Επειδή τα δεδομένα αφορούν δύο πόλεις μίας χώρας θεωρούμε τους δύο δειγματοχώρους εξαρτώμενους 
# διότι οι μέγιστες θερμοκρασίες σε κάθε πόλη θα καθορίζονται από το συνοπτικό σύστημα καιρού.

# Αφού θέλουμε να δούμε πόσο άλλαξαν οι μέγιστες θερμοκρασίες εντός του Ιανουαρίου
# πρόκειται για χρονικώς εξαρτώμενους δειγματοχώρους.

# Εφαρμόζουμε λοιπόν ‘έλεγχο t εξαρτώμενων δειγματοχώρων’

# Επειδή είναι απίθανο η διαφορά θερμοκρασίας να είναι 0
# θεωρούμε ως μηδενική υπόθεση Ho: μ=0
# και ως εναλλακτική την υπόθεση HA: μ!=0.

# Υπολογίζουμε τις διαφορές των μέγιστων θερμοκρασιών μεταξύ των δύο πόλεων:
diff=df['MaxTem_Ith']-df['MaxTem_Can']
print('Οι διαφορές των μέγιστων θερμοκρασιών είναι: ', diff)

# Υπολογίζυμε τη μέση τιμή:
x = diff.mean()
print('Η μέση τιμή των διαφορών είναι: ', round(x, 4))

# Υπολογίζουμε την τυπική απόκλιση:
s = diff.std()
print('Η τυπική απόκλιση των διαφορών είναι: ', round(s, 4))

# Υπολογίζουμε τον συντελεστή αυτοσυσχέτισης:
r1 = diff.autocorr(lag=1)
print('Ο συντελεστής αυτοσυσχέτισης των διαφορών είναι: ', round(r1, 4))

# Οι βαθμοί ελευθερίας σε αυτή την περίπτωση δίνονται από τον τύπο:
df = n * ((1-r1)/(1+r1))
print('Οι βαθμοί ελευθερίας είναι: ', round(df, 4))

# Η μέση τιμή της μηδενικής υπόθεσης:
M=0

# Το στατιστικό δίνεται από τον τύπο:
t = (x-M) / (s * (df**-0.5))
print('Η τιμή του στατιστικού είναι: ', round(t, 4))

# ΜΕΘΟΔΟΣ ΚΡΙΣΙΜΗΣ ΤΙΜΗΣ

# Υπολογίζουμε την κρίσιμη τιμή και από τις δύο πλευρές:
t_kr_meion = scipy.stats.t.ppf(a/2,df)
print('Η κρίσιμη τιμή αριστερά είναι: ', round(t_kr_meion, 4))
t_kr_syn = scipy.stats.t.ppf(1-a/2,df)
print('Η κρίσιμη τιμή δεξιά είναι: ', round(t_kr_syn, 4))

# Συμπεράσματα
# Εφόσον t < [-2.0532,2.0532] τότε η υπόθεση Hο απορρίπτεται.
# Οπότε οι μέσες μέγιστες θερμοκρασίες του Ιανουαρίου 1987
# στην Ithaca και στην Canandaigua είναι στατιστικώς διαφορετικές, με
# επίπεδο σημαντικότητας 0, 05.

# ΜΕΘΟΔΟΣ ΤΙΜΗΣ p

# Υπολογίζουμε την πιθανότητα το στατιστικό να είναι μικρότερο 
# από αυτό που προέκυψε από τα δεδομένα.
p = scipy.stats.t.cdf(t,df)
print('Η πιθανότητα είναι: ', round(p, 4))

# Συμπεράσματα
# Εφόσον p < a τότε η υπόθεση Hο απορρίπτεται.
# Οπότε οι μέσες μέγιστες θερμοκρασίες του Ιανουαρίου 1987
# στην Ithaca και στην Canandaigua είναι στατιστικώς διαφορετικές, με
# επίπεδο σημαντικότητας 0, 05.
