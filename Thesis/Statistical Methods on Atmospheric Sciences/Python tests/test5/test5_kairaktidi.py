import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

data = pd.read_csv('Hellenicon_data.csv', sep=';', index_col=0, parse_dates=True)
data = data.dropna() 

# 1. Υπολογίστε τους συντελεστές συσχέτισης Pearson, Spearman και Kendall, μεταξύ των τριών παραμέτρων (ανά ζεύγη). 
# Ποιός συντελεστής εμφανίζει την καλύτερη συσχέτιση και μεταξύ ποιών παραμέτρων; Θεωρείτε το αποτέλεσμα λογικό;

# Pearson
print(stats.pearsonr(data['Tmax'], data['r']))
print(stats.pearsonr(data['Tmin'], data['r']))
print(stats.pearsonr(data['Tmax'], data['Tmin']))

# Spearman
print(stats.spearmanr(data['Tmax'], data['r']))
print(stats.spearmanr(data['Tmin'], data['r']))
print(stats.spearmanr(data['Tmax'], data['Tmin']))

# Kendall
print(stats.kendalltau(data['Tmax'], data['r']))
print(stats.kendalltau(data['Tmin'], data['r']))
print(stats.kendalltau(data['Tmax'], data['Tmin']))


'''
Η ισχυρότερη συσχέτιση εμφανίζεται μεταξύ Tmax και Tmin, 
με όλους τους συντελεστές να δείχνουν πολύ υψηλή θετική συσχέτιση, και συγκεκριμένα:

* Pearson: 0.9379
* Spearman: 0.9402
* Kendall: 0.7856

Αυτό σημαίνει ότι όσο αυξάνεται η μέγιστη θερμοκρασία (Tmax), 
αυξάνεται και η ελάχιστη θερμοκρασία (Tmin), κάτι που είναι απόλυτα λογικό, 
καθώς οι δύο αυτές τιμές εξαρτώνται έντονα από τις ίδιες κλιματικές συνθήκες.

'''

# 2. Αν σας πρότειναν να δημιουργήσετε ένα στατιστικό προγνωστικό υπόδειγμα με
# ανεξάρτητες μεταβλητές (δεδομένα εισόδου) τις τρεις αυτές παραμέτρους, θα επιλέγατε και τις τρεις, 
# ή θα αποκλείατε κάποια ή κάποιες από αυτές; Τεκμηριώστε την απάντησή σας.

'''
Δεν θα χρησιμοποιούσαμε και τις τρεις παραμέτρους, διότι υπάρχει πολύ ισχυρή συσχέτιση μεταξύ Tmax και Tmin,
συγκεκριμένα Tmax και Tmin έχουν Pearson = 0.9379, που σημαίνει ότι είναι σχεδόν γραμμικά εξαρτημένες.
Αν συμπεριλάβουμε και τις δύο στο υπόδειγμα, τα στατιστικά αποτελέσματα ενδεχομένως να είναι μη αξιόπιστα καθώς
οι δύο αυτές μεταβλητές είναι πρακτικά εξαρτημένες η μία από την άλλη. 
Συνεπώς, θα διατηρούσαμε είτε την Tmax είτε την Tmin, αλλά όχι και τις δύο μαζί.
Δεδομένου ότι όλοι οι συντελεστές συσχέτισης με την βροχόπτωση είναι μεγαλύτεροι στην περίπτωση της Tmax, 
θα επιλέγαμε να αποκλείσουμε την Tmin.

'''

# 3. Σχεδιάστε τα διαγράμματα αυτοσυσχέτισης των χρονοσειρών του υετού και μιας
# από τις δύο θερμοκρασίες (μέγιστης ή ελάχιστης); Ποιά από αυτές εμφανίζει τη
# μεγαλύτερη αυτοσυσχέτιση; Υπάρχει μετεωρολογική - κλιματολογική ερμηνεία για αυτό;

rain = data['r'] 
temperature = data['Tmax'] 

# αρχικά πρόσθεσα κάποια διαγράμματα για το αρχικό visualisation των δεδομένων
plt.figure(figsize=(10,4))
plt.plot(data.index, rain, label="Υετός (r)", color="blue")
plt.xlabel("Date")
plt.ylabel("Pricipitation (mm)")
plt.title("Precipitation timeseries")
plt.legend()
plt.show()

plt.figure(figsize=(10,4))
plt.plot(data.index, temperature, label="Maximum temperature (Tmax)", color="red")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Timeseries (Tmax)")
plt.legend()
plt.show()

# αυτοσυσχέτιση
print("Pricipitation autocorrelation (lag=1):", rain.autocorr(lag=1))
print("Temperature autocorrelation (lag=1):", temperature.autocorr(lag=1))

plt.figure(figsize=(8,4))
plot_acf(rain, lags=30, title="Pricipitation autocorrelation (r)")
plt.show()

plt.figure(figsize=(8,4))
plot_acf(temperature, lags=30, title="Temperature autocorrelation (Tmax)")
plt.show()

'''
Βλέπουμε ότι η αυτοσυσχέτιση της θερμοκρασίας (Tmax) είναι υψηλή, 
δηλαδή η θερμοκρασία έχει ισχυρή χρονική εξάρτηση (= η θερμοκρασία μιας ημέρας εξαρτάται έντονα από τις προηγούμενες ημέρες).
Αντίθετα, υετός (r) έχει χαμηλότερη αυτοσυσχέτιση, επειδή οι βροχοπτώσεις είναι συχνά πιο τυχαίες σε σύγκριση με τη θερμοκρασία.
Η μετεωρολογική - κλιματολογική ερμηνεία που μπορούμε να δώσουμε με βάση τα παραπάνω αποτελέσματα καθώς και τις θεωρητικές
μας γνώσεις είναι ότι η θερμοκρασία είναι μια σχετικά προβλέψιμη μεταβλητή, καθώς εξαρτάται από εποχιακά μοτίβα 
και τη γενική κλιματολογία μιας περιοχής. Ο υετός, αντίθετα, εξαρτάται από ατμοσφαιρικές διαταραχές, 
καιρικά συστήματα και τυχαία γεγονότα, οπότε η αυτοσυσχέτισή του είναι συνήθως μικρότερη.
'''

#4. Επιλέξτε δύο μετεωρολογικές παραμέτρους της αρεσκείας σας. Θεωρώντας ότι
# έχετε χρονοσειρές μετρήσεων της καθεμιάς οι οποίες αποτελούν δείγμα πληθυσμού, 
# η στατιστική κατανομή που ακολουθεί κάθε μία από αυτές είναι συνεχής ή διακριτή; Τεκμηριώστε την απάντησή σας.

'''
Έστω ότι επιλέγουμε τις μεταβλητές της θερμοκρασίας και της ταχύτητας ανέμου.

Η θερμοκρασία ακολουθεί συνεχή κατανομή καθώς μπορεί να πάρει οποιαδήποτε πραγματική τιμή μέσα σε ένα εύρος και
οι μετρήσεις γίνονται με θερμόμετρα που έχουν πολύ καλή διακριτότητα.
Η θερμοκρασία συνήθως ακολουθεί Κανονική Κατανομή, ειδικά όταν αναλύουμε ημερήσιες ή μηνιαίες μέσες τιμές.

Η ταχύτητα του ανέμου ακολουθεί και εκείνη συνεχή κατανομή καθώς μετριέται σε m/s ή km/h και μπορεί να πάρει οποιαδήποτε 
τιμή μέσα σε ένα εύρος. Η κατανομή της συνήθως ακολουθεί Weibull  κατανομή, καθώς οι περισσότερες ημέρες έχουν χαμηλές ταχύτητες
ανέμου, αλλά κάποιες μέρες εμφανίζονται πολύ ισχυροί άνεμοι.

Παρόλα αυτά, επειδή αναφερόμαστε σε μεγέθη τα οποία είναι μετρήσιμα και επιβαρύνονται από σφάλματα κατά την μέτρησή τους,
είναι σημαντικό να έχουμε στο νου μας το εξής απόφθεγμα όπως το αναλύει ο Wilks στο σύγγραμμά του (σελ 73):

" Strictly speaking, using a continuous distribution to represent observable data implies
that the underlying observations are known to an arbitrarily large number of significant
figures. Of course this is never true, but it is convenient and not too inaccurate to represent
as continuous those variables that are continuous conceptually but reported discretely.
Temperature and precipitation are two obvious examples that really range over some
portion of the real number line, but which are usually reported to discrete multiples of 1F
and 0.01 in. in the United States. Little is lost when treating these discrete observations
as samples from continuous distributions."

'''