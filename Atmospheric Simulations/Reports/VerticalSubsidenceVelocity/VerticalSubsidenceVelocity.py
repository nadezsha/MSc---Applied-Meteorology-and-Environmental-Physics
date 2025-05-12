import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# Create figures directory if it doesn't exist
os.makedirs('figures', exist_ok=True)

# Load data
nodiv = pd.read_csv('no divergence.csv')
weakdiv = pd.read_csv('weak divergence.csv')
strongdiv = pd.read_csv('strong divergence.csv')

nodiv_diu = pd.read_csv('no divergence (diurnal).csv')
weakdiv_diu = pd.read_csv('weak divergence (diurnal).csv')
strongdiv_diu = pd.read_csv('strong divergence (diurnal).csv')

# Adding 'ws [m s-¹]' column
nodiv['ws [m s-¹]'] = 0
weakdiv['ws [m s-¹]'] = -0.00001 * weakdiv['h [m]']
strongdiv['ws [m s-¹]'] = -0.00005 * strongdiv['h [m]']
nodiv_diu['ws [m s-¹]'] = 0
weakdiv_diu['ws [m s-¹]'] = -0.00001 * weakdiv_diu['h [m]']
strongdiv_diu['ws [m s-¹]'] = -0.00005 * strongdiv_diu['h [m]']

print(nodiv)

##### Functions #####
def plot_group_subsidence(dfs, labels, group_title, height_col='h [m]', velocity_col='ws [m s-¹]'):
    plt.figure(figsize=(6, 6))
    for df, label in zip(dfs, labels):
        if height_col not in df.columns or velocity_col not in df.columns:
            raise ValueError(f"Missing required column in DataFrame: {label}")
        plt.plot(df[velocity_col], df[height_col], label=label)
    
    plt.xlabel('Subsidence Velocity [m/s]')
    plt.ylabel('Height [m]')
    plt.title(group_title)
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    filename = group_title.replace(" ", "_").lower() + '.png'
    plt.savefig(os.path.join('figures', filename), dpi=300)
    plt.show()

def plot_3panel_temporal(dfs, labels, group_title):
    import matplotlib.pyplot as plt
    import os

    variables = ['θ [K]', 'Δθ [K]', 'h [m]']
    titles = ['Mean Potential Temperature (θ̄)', 'Δθ over Time', 'Boundary Layer Height (h) over Time']
    ylabels = ['θ̄ [K]', 'Δθ [K]', 'h [m]']

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for ax, var, title, ylabel in zip(axes, variables, titles, ylabels):
        for df, label in zip(dfs, labels):
            ax.plot(df['time [h]'], df[var], label=label)
        ax.set_title(title)
        ax.set_xlabel('Time [h]')
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True)

    fig.suptitle(group_title, fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])  # Ensure room for suptitle

    filename = group_title.replace(" ", "_").lower() + '.png'
    fig.savefig(os.path.join('figures', filename), dpi=300)
    plt.show()
    plt.close(fig)  

def compute_dh_dt(df, time_col='time [h]', height_col='h [m]', tol=1):
    """Adds ∂h/∂t column and returns rows where it is ~0."""
    df = df.copy()
    df['∂h/∂t'] = df[height_col].diff() / df[time_col].diff()
    zero_growth = df[df['∂h/∂t'].abs() < tol]
    return df, zero_growth

def plot_h_with_zero_growth_all(dfs, labels, title):
    plt.figure(figsize=(10, 6))
    for df, label in zip(dfs, labels):
        full_df, zero_df = compute_dh_dt(df)
        plt.plot(full_df['time [h]'], full_df['h [m]'], label=f'{label} h(t)')
        plt.scatter(zero_df['time [h]'], zero_df['h [m]'], color='red', s=30, label=f'{label} ∂h/∂t ≈ 0')

    plt.xlabel('Time [h]')
    plt.ylabel('Boundary Layer Height [m]')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Safe filename generation: remove or replace special characters
    safe_title = re.sub(r'[^\w\s-]', '', title)  # Remove special characters
    safe_title = safe_title.replace(' ', '_').lower() + '.png'

    plt.savefig(os.path.join('figures', safe_title), dpi=300)
    plt.show()
    plt.close()


# TASK zero : plot the subsidence velocity as a function of height to find its dependence on height.
# Non-diurnal
plot_group_subsidence(
    [nodiv, weakdiv, strongdiv],
    ['No Divergence', 'Weak Divergence', 'Strong Divergence'],
    'Subsidence vs Height (Non-Diurnal)'
)

# Diurnal
plot_group_subsidence(
    [nodiv_diu, weakdiv_diu, strongdiv_diu],
    ['No Divergence (Diurnal)', 'Weak Divergence (Diurnal)', 'Strong Divergence (Diurnal)'],
    'Subsidence vs Height (Diurnal)'
)

# TASK (a) : Compare the boundary layer characteristics in a situation without subsidence
# and influenced by the presence of a high pressure system.
# Non-diurnal
plot_3panel_temporal(
    [nodiv, weakdiv, strongdiv],
    ['No Divergence', 'Weak Divergence', 'Strong Divergence'],
    'Non-Diurnal Cases'
)

# Diurnal
plot_3panel_temporal(
    [nodiv_diu, weakdiv_diu, strongdiv_diu],
    ['No Divergence (Diurnal)', 'Weak Divergence (Diurnal)', 'Strong Divergence (Diurnal)'],
    'Diurnal Cases'
)

# TASK (b) : Find a situation where the boundary layer growth is 0, that is (∂h/∂t = 0).
# Discuss the implications for the entrainment flux
# Diurnal group
plot_h_with_zero_growth_all(
    [nodiv_diu, weakdiv_diu, strongdiv_diu],
    ['No Divergence (Diurnal)', 'Weak Divergence (Diurnal)', 'Strong Divergence (Diurnal)'],
    'Diurnal Cases – ∂h/∂t ≈ 0'
)

# Non-diurnal group
plot_h_with_zero_growth_all(
    [nodiv, weakdiv, strongdiv],
    ['No Divergence', 'Weak Divergence', 'Strong Divergence'],
    'Non-Diurnal Cases – ∂h/∂t ≈ 0'
)

