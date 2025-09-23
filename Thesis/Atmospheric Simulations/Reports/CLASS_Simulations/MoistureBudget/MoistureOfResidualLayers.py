import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ensure output directory exists
os.makedirs('figures', exist_ok=True)

# Load data
uniform = pd.read_csv('data/uniform conditions.csv')
dry = pd.read_csv('data/very dry conditions.csv')
uniform_diu = pd.read_csv('data/uniform conditions(diurnal).csv')
dry_diu = pd.read_csv('data/very dry conditions(diurnal).csv')
control = pd.read_csv('data/control.csv')
control_diu = pd.read_csv('data/control(diurnal).csv')

# Add condition labels
uniform['Condition'] = 'Uniform'
dry['Condition'] = 'Very Dry'
uniform_diu['Condition'] = 'Uniform (Diurnal)'
dry_diu['Condition'] = 'Very Dry (Diurnal)'
control['Condition'] = 'Control'
control_diu['Condition'] = 'Control (Diurnal)'

# Combine datasets
df_all = pd.concat([uniform, dry, uniform_diu, dry_diu, control, control_diu], ignore_index=True)
df_all.columns = df_all.columns.str.strip()

##### TASK A #####
# Compare the values of q, Δq,and LCL for the different cases. Is the potential
# temperature budget influenced by the different values of q?

# ---------------------------
# 1. Summary
# ---------------------------
summary = df_all.groupby('Condition')[
    ['q [g kg-¹]', 'Δq [g kg-¹]', 'LCL [m]', 'θ [K]', 'Δθ [K]', "w'θ'(M) [K m s-¹]"]
].mean()
print("=== Values by Condition ===")
print(summary)
summary.to_csv('summary.csv')

# ---------------------------
# 2. Bar Plots
# ---------------------------
sns.set(style="white")
bar_vars = ['q [g kg-¹]', 'Δq [g kg-¹]', 'LCL [m]']
for var in bar_vars:
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(data=df_all, x='Condition', y=var, estimator='mean', errorbar=None, width=0.4)
    
    # Add value labels
    means = df_all.groupby('Condition')[var].mean().values
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', padding=3)

    plt.title(f'{var} by Condition')
    plt.xticks(rotation=15)
    plt.tight_layout()
    filename = var.replace(" ", "_").replace("[", "").replace("]", "").replace("/", "")
    plt.savefig(f'figures/mean_{filename}.png')
    plt.show()

# ---------------------------
# 3. Time Series Plots: One Per Variable
# ---------------------------
time_col = 'time [h]'
time_vars = ['q [g kg-¹]', 'Δq [g kg-¹]', 'LCL [m]']

if time_col in df_all.columns:
    for var in time_vars:
        plt.figure(figsize=(10, 6))
        for condition in df_all['Condition'].unique():
            subset = df_all[df_all['Condition'] == condition].copy()
            subset = subset.sort_values(by=time_col)
            plt.plot(subset[time_col], subset[var], label=condition)
        plt.title(f'Time Series of {var}')
        plt.xlabel('Time [h]')
        plt.ylabel(var)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        filename = var.replace(" ", "_").replace("[", "").replace("]", "").replace("/", "")
        plt.savefig(f'figures/timeseries_{filename}.png')
        plt.show()
else:
    print(f"\n[Warning] Time column '{time_col}' not found. Skipping time series plots.")

# ---------------------------
# 4. Correlation Heatmaps 
# ---------------------------
corr_vars = ['q [g kg-¹]', 'Δq [g kg-¹]', 'LCL [m]', 'θ [K]', 'Δθ [K]', "w'θ'(M) [K m s-¹]"]
for condition in df_all['Condition'].unique():
    subset = df_all[df_all['Condition'] == condition]
    corr_matrix = subset[corr_vars].corr()
    
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(
        corr_matrix, annot=True, fmt=".2f",
        vmin=-1, vmax=1, square=True, cbar_kws={"shrink": 0.8}
    )
    ax.set_facecolor("white")  # No background grid
    plt.title(f'Correlation Heatmap - {condition}')
    plt.tight_layout()
    filename = condition.replace(" ", "_").replace("(", "").replace(")", "").lower()
    plt.savefig(f'figures/correlation_heatmap_{filename}.png')
    plt.show()


# ---------------------------
# 5. Print Correlation Coefficients (Overall)
# ---------------------------
print("\n=== Correlation Coefficients (All Data Combined) ===")
correlation_pairs = [
    ('q [g kg-¹]', 'θ [K]'),
    ('Δq [g kg-¹]', 'Δθ [K]'),
    ('LCL [m]', "w'θ'(M) [K m s-¹]")
]

for x, y in correlation_pairs:
    correlation = df_all[[x, y]].dropna().corr().iloc[0, 1]
    print(f"{x} vs {y}: {correlation:.3f}")


##### TASK B #####
# Under which conditions are boundary layer clouds formed and at which
# height? Discuss which are the most favourable early-morning conditions for
# Δq to form boundary-layer clouds.

'''

Boundary-layer clouds are most likely to form under Uniform (Diurnal) conditions,
where LCL values are lowest (e.g., around 400–600 m). These conditions show 
higher near-surface moisture q and larger Δq, especially during the early morning (0–9 h),
indicating strong moisture gradients.

In contrast, Very Dry conditions exhibit high LCLs (often exceeding 1000 m) 
and low Δq, making them less favorable for boundary-layer cloud development.

The most favorable early-morning conditions for cloud formation occur when:

* Δq is high, indicating moisture accumulation near the surface.

* LCL is low, indicating air parcels can reach saturation with minimal lifting.

These conditions are typically observed in the Uniform (Diurnal) scenario, 
suggesting that diurnal variations in moisture and temperature play a key role 
in driving cloud formation.

'''
'''
# 1. Scatter plot: LCL vs RH(surf)
plt.figure(figsize=(8, 6))
sns.lineplot(
    data=df_all.sort_values(by='RH(surf) [-]'),  
    x='RH(surf) [-]',
    y='LCL [m]',
    hue='Condition',
    estimator='mean',  
    ci=None,           
    lw=2               
)
plt.title('LCL vs Surface Relative Humidity')
plt.xlabel('Relative Humidity (Surface) [%]')
plt.ylabel('LCL [m]')
plt.grid(True)
plt.tight_layout()
plt.savefig('figures/LCL_vs_RHsurf.png')
plt.show()

# 2. Scatter plot: LCL vs Δq
plt.figure(figsize=(8, 6))
sns.lineplot(
    data=df_all.sort_values(by='Δq [g kg-¹]'),  
    x='Δq [g kg-¹]',
    y='LCL [m]',
    hue='Condition',
    estimator='mean',  
    ci=None,           
    lw=2               
)
plt.title('LCL vs Δq')
plt.xlabel('Δq [g kg⁻¹]')
plt.ylabel('LCL [m]')
plt.grid(True)
plt.tight_layout()
plt.savefig('figures/LCL_vs_dq.png')
plt.show()

# 3. Scatter plot: LCL vs q
plt.figure(figsize=(8, 6))
sns.lineplot(
    data=df_all.sort_values(by='q [g kg-¹]'),  
    x='q [g kg-¹]',
    y='LCL [m]',
    hue='Condition',
    estimator='mean',  
    ci=None,           
    lw=2               
)
plt.title('LCL vs q')
plt.xlabel('q [g kg⁻¹]')
plt.ylabel('LCL [m]')
plt.grid(True)
plt.tight_layout()
plt.savefig('figures/LCL_vs_q.png')
plt.show()

# 4. Correlation values
print("=== Correlation with LCL ===")
for var in ['RH(surf) [-]', 'Δq [g kg-¹]', 'q [g kg-¹]']:
    corr = df_all[['LCL [m]', var]].dropna().corr().iloc[0, 1]
    print(f"LCL vs {var}: {corr:.3f}")
'''

##### TASK C #####
# By now using the conditions of the control case (Δq = −1 g kg−1), we
# investigate the role of the other jump, the potential temperature jump, on the
# moisture budget. Design two numerical experiments to determine the impact
# of the potential temperature jump on the moisture budget.
#• What is the effect of the initial temperature jump on the moisture budget?
# At which time of the <q> evolution is the influence of Δθ more evident?
#• Is Δθ influencing cloud formation?
def plot_non_diurnal_and_diurnal(df_all):
    sns.set(style="whitegrid")
    
    # Define variables and labels
    time_col = 'time [h]'
    plot_vars = ['h [m]', 'Δθv [K]', 'RH(top) [-]']
    
    # Separate non-diurnal and diurnal data based on 'Condition' name
    non_diurnal_conditions = [cond for cond in df_all['Condition'].unique() if 'diurnal' not in cond.lower()]
    diurnal_conditions = [cond for cond in df_all['Condition'].unique() if 'diurnal' in cond.lower()]
    
    # Plotting helper for subplots
    def plot_subplots(conditions, prefix):
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=False)
        
        for idx, var in enumerate(plot_vars):
            ax = axes[idx]
            for condition in conditions:
                subset = df_all[df_all['Condition'] == condition].copy()
                if time_col in subset.columns and var in subset.columns:
                    subset = subset.sort_values(by=time_col)
                    ax.plot(subset[time_col], subset[var], label=condition)
                else:
                    print(f"[Warning] Missing column '{var}' or '{time_col}' in data for condition '{condition}'. Skipping.")
            ax.set_title(f'{var}')
            ax.set_xlabel('Time [h]')
            ax.set_ylabel(var)
            ax.grid(True)
            ax.legend()

        plt.suptitle(f'Time Series for {prefix.capitalize()} Conditions', fontsize=14)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        filename = f'{prefix}_h_dtheta_rhtop_horizontal.png'
        plt.savefig(f'figures/{filename}')
        plt.show()
    
    # Plot combined subplots for both non-diurnal and diurnal
    plot_subplots(non_diurnal_conditions, 'non_diurnal')
    plot_subplots(diurnal_conditions, 'diurnal')


# Call the function
plot_non_diurnal_and_diurnal(df_all)