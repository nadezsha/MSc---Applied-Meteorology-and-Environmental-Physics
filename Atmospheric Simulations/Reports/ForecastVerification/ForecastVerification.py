import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
import os

# create output folder for plots
os.makedirs('./figures', exist_ok=True)
os.makedirs('./outputs', exist_ok=True)

# import Data
data = pd.read_excel('io_tc2d03.xlsx')
data['Datetime'] = pd.to_datetime(data[['YEAR', 'MONTH', 'DAY', 'HOUR']])
data = data.set_index('Datetime').drop(['YEAR', 'MONTH', 'DAY', 'HOUR'], axis=1)
data = data.dropna(subset=['OBS', 'MOD'])

'''
(α) Να υπολογίσετε την ημερήσια μέση θερμοκρασία (TAVG) και να σχεδιάσετε τις 
ημερήσιες χρονοσειρές (observed, modelled) στο ίδιο διάγραμμα για τον Ιανουάριο. 
Να επαναλάβετε τη διαδικασία για όλους τους μήνες (12 panel plots). 
Σε ποιους μήνες διακρίνετε την καλύτερη και την χειρότερη συμπεριφορά του μοντέλου? 
Σχολιασμός.
(β) Να επαναλάβετε την παραπάνω διαδικασία για την μέγιστη και την ελάχιστη θερμοκρασία. 
Οι μεταβλητες TMIN και TMAX έχουν παρόμοια συμπεριφορά με την TAVG? Σχολιασμός.
'''

# calculation of mean, min, max temps
def daily_mean(data):
    mean_obs = data['OBS'].resample('D').mean()
    mean_mod = data['MOD'].resample('D').mean()
    return mean_obs, mean_mod

def daily_min(data):
    min_obs = data['OBS'].resample('D').min()
    min_mod = data['MOD'].resample('D').min()
    return min_obs, min_mod

def daily_max(data):
    max_obs = data['OBS'].resample('D').max()
    max_mod = data['MOD'].resample('D').max()
    return max_obs, max_mod

# daily plots for the temps for all months
def plot_daily(obs, mod, title, fig_name):
    month_names = calendar.month_abbr[1:]
    
    fig, axs = plt.subplots(nrows=3, ncols=4, figsize=(16, 10), sharex=False)
    fig.suptitle(title, fontsize=18)
    axs = axs.ravel()
    
    for idx, ax in enumerate(axs):
        month = idx + 1
        obs_month = obs[obs.index.month == month]
        mod_month = mod[mod.index.month == month]
        
        year = obs_month.index.year[0] if len(obs_month) > 0 else 2024
        days_in_month = calendar.monthrange(year, month)[1]
        full_days = pd.date_range(start=f'{year}-{month:02d}-01', periods=days_in_month, freq='D')
        
        obs_month_reindexed = obs_month.reindex(full_days)
        mod_month_reindexed = mod_month.reindex(full_days)
        
        day_range = np.arange(1, days_in_month + 1)
        
        ax.plot(day_range, obs_month_reindexed.values, label='observed', linewidth=2)
        ax.plot(day_range, mod_month_reindexed.values, label='modeled', linewidth=2)
        
        ax.set_title(month_names[idx])
        ax.grid(True)
        
        if idx // 4 == 2:  # bottom row
            ax.set_xlabel('Day of Month', fontsize=12)
        if idx % 4 == 0:  # first column
            ax.set_ylabel('T (°C)', fontsize=12)
    
    # shared legend 
    fig.legend(*axs[0].get_legend_handles_labels(),
               loc='lower center',
               ncol=2,
               fontsize=14,
               bbox_to_anchor=(0.5, -0.03))
    
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(f'./figures/{fig_name}', bbox_inches='tight')
    plt.close()


# calculation of mean, min and max temps using the above functions
obs_mean, mod_mean = daily_mean(data)
obs_min, mod_min = daily_min(data)
obs_max, mod_max = daily_max(data)

# daily temp plots 
plot_daily(obs_mean, mod_mean, 'Daily Mean Temperature', 'daily_mean.png')
plot_daily(obs_min, mod_min, 'Daily Min Temperature', 'daily_min.png')
plot_daily(obs_max, mod_max, 'Daily Max Temperature', 'daily_max.png')

'''
(γ) Να υπολογίσετε το ME (mean error) και το MSE (mean square error) για 
την ετήσια χρονοσειρα της θερμοκρασίας. 
(γ1) Να επαναλάβετε τη διαδικασία για κάθε μήνα ξεχωριστά και να παρουσιάσετε 
τα αποτελέσματα σε διάγραμμα. Σε ποιους μήνες διακρίνετε την καλύτερη και την 
χειρότερη συμπεριφορά του μοντέλου? Σχολιασμός.
(γ2) Να επαναλάβετε τη διαδικασία για κάθε ώρα της ημέρας ξεχωριστά και να παρουσιάσετε 
τα αποτελέσματα σε διάγραμμα. Σε ποιους ώρες διακρίνετε την καλύτερη και την 
χειρότερη συμπεριφορά του μοντέλου? Σχολιασμός.
'''

# (γ) annual ME and MSE
def compute_me_mse(obs, mod):
    me = (mod - obs).mean()
    mse = ((mod - obs) ** 2).mean()
    return me, mse

# calculate on the hourly data 
annual_me, annual_mse = compute_me_mse(data['OBS'], data['MOD'])
annual_mean_me, annual_mean_mse = compute_me_mse(obs_mean, mod_mean)
annual_max_me, annual_max_mse = compute_me_mse(obs_max, mod_max)
annual_min_me, annual_min_mse = compute_me_mse(obs_min, mod_min)

with open('./outputs/total_stats.txt', 'w') as f:
    f.write('--- ME and MSE values ---\n')
    f.write(f'Annual ME: {round(annual_me, 2)}°C\n')
    f.write(f'Annual MSE: {round(annual_mse, 2)}°C²\n')
    f.write(f'Annual Mean ME: {round(annual_mean_me, 2)}°C\n')
    f.write(f'Annual Mean MSE: {round(annual_mean_mse, 2)}°C²\n')    
    f.write(f'Annual Max ME: {round(annual_max_me, 2)}°C\n')
    f.write(f'Annual Max MSE: {round(annual_max_mse, 2)}°C²\n')    
    f.write(f'Annual Min ME: {round(annual_min_me, 2)}°C\n')
    f.write(f'Annual Min MSE: {round(annual_min_mse, 2)}°C²\n')

# (γ1) monthly ME and MSE
monthly_me = data.groupby(data.index.month).apply(lambda df: compute_me_mse(df['OBS'], df['MOD'])[0])
monthly_mse = data.groupby(data.index.month).apply(lambda df: compute_me_mse(df['OBS'], df['MOD'])[1])

fig, ax1 = plt.subplots(figsize=(10, 5))
months = np.arange(1, 13)
month_labels = calendar.month_abbr[1:]

ax1.plot(months, monthly_me, marker='o', color='blue', label='ME')
ax1.set_ylabel('Mean Error (°C)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(months, monthly_mse, marker='o', color='red', label='MSE')
ax2.set_ylabel('Mean Squared Error (°C²)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

ax1.set_xticks(months)
ax1.set_xticklabels(month_labels)
ax1.set_xlabel('Month')
plt.title('Monthly ME and MSE')
plt.grid(True)
plt.tight_layout()
plt.savefig('./figures/monthly_me_mse.png')
plt.close()

# (γ2) Hourly ME and MSE
hourly_me = data.groupby(data.index.hour).apply(lambda df: compute_me_mse(df['OBS'], df['MOD'])[0])
hourly_mse = data.groupby(data.index.hour).apply(lambda df: compute_me_mse(df['OBS'], df['MOD'])[1])

fig, ax1 = plt.subplots(figsize=(10, 5))
hours = np.arange(24)

ax1.plot(hours, hourly_me, marker='o', color='blue', label='ME')
ax1.set_ylabel('Mean Error (°C)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(hours, hourly_mse, marker='o', color='red', label='MSE')
ax2.set_ylabel('Mean Squared Error (°C²)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

ax1.set_xticks(hours)
ax1.set_xlabel('Hour of Day')
plt.title('Hourly ME and MSE')
plt.grid(True)
plt.tight_layout()
plt.savefig('./figures/hourly_me_mse.png')
plt.close()


'''
(δ) Να υπολογίσετε το 95ο εκατοστημόριο (percentile) των μετρήσεων (warm days). 
Να κατασκευάσετε τον contingency table, να υπολογίσετε τους δείκτες POD, FAR, CSI 
και να ερμηνεύσετε το αποτέλεσμα. Επίσης, να σχεδιάσετε το αντίστοιχο διάγραμμα διασποράς 
(observed, modelled) όπου να τοποθετήσετε το threshold που υπολογίσατε παραπάνω.
'''

# calculate 95th percentile of observed temperatures
percentile_95 = data['OBS'].quantile(0.95)

with open('./outputs/total_stats.txt', 'a') as f:
    f.write(f'95th Percentile (Warm Day Threshold): {round(percentile_95, 1)}°C\n')

# classification of warm days
obs_warm = data['OBS'] >= percentile_95
mod_warm = data['MOD'] >= percentile_95

# Contingency table components
hits = (obs_warm & mod_warm).sum()
misses = (obs_warm & ~mod_warm).sum()
false_alarms = (~obs_warm & mod_warm).sum()
correct_non_events = (~obs_warm & ~mod_warm).sum()
total = hits + misses + false_alarms + correct_non_events

# POD, FAR, CSI
POD = hits / (hits + misses) if (hits + misses) > 0 else np.nan
FAR = false_alarms / (hits + false_alarms) if (hits + false_alarms) > 0 else np.nan
CSI = hits / (hits + misses + false_alarms) if (hits + misses + false_alarms) > 0 else np.nan

# Save results
with open('./outputs/total_stats.txt', 'a') as f:
    f.write('--- Indexes ---\n')
    f.write(f'POD = a / (a + c): {POD:.2f}\n')
    f.write(f'FAR = b / (a + b): {FAR:.2f}\n')
    f.write(f'CSI = a / (a + b + c): {CSI:.2f}\n')
    f.write('--- Contingency Table (a, b, c, d) ---\n')
    f.write(f'a = Hits: {hits}\n')
    f.write(f'b = False Alarms: {false_alarms}\n')
    f.write(f'c = Misses: {misses}\n')
    f.write(f'd = Correct Non-events: {correct_non_events}\n')
    f.write(f'Total (a + b + c + d): {total}\n')

print("Contingency Table:")
print("                 | Observed Yes | Observed No ")
print("Forecast Yes     | {:>12} | {:>11}".format(hits, false_alarms))
print("Forecast No      | {:>12} | {:>11}".format(misses, correct_non_events))

plt.figure(figsize=(8, 6))
plt.scatter(data['OBS'], data['MOD'], alpha=0.5, edgecolor='k', label='Data points')
plt.axhline(y=percentile_95, color='r', linestyle='--', label='Threshold')
plt.axvline(x=percentile_95, color='r', linestyle='--')
plt.xlabel('Observed Temperature (°C)')
plt.ylabel('Modeled Temperature (°C)')
plt.title('Scatter Plot with 95th Percentile Threshold')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('./figures/warm_days_scatter.png')
plt.close()