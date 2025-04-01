import numpy as np
import matplotlib.pyplot as plt

# Constants
S = 1370  # Solar constant (W/m^2)
sigma = 5.67e-8  # Stefan-Boltzmann constant (W/m^2*K^4)
alpha = 0.3  # Planetary albedo
epsilon = 0.6  # Emissivity 

# Defining functions (to be used later on)

def EBM(Cp_atm, step):
    """
    Simulates Earth's temperature evolution towards radiative equilibrium and plots the results.
    
    Parameters:
    Cp_atm (float): Heat capacity of the atmosphere (J/m2*K)
    step (int): Duration of the simulation in days
    
    Returns:
    time_reached_teq (float): The time in days when Teq is first reached
    """
    
    # Time stepping parameters
    dt = 3600  # time step in seconds (1 hour)
    t_max = step * 24 * 3600  # total simulation time in seconds
    n_steps = int(t_max / dt)  # number of time steps

    # Initialize temperature array
    T = np.zeros(n_steps)
    T[0] = 250  # initial temperature in Kelvin

    # Time evolution loop
    time = np.linspace(0, t_max / (24 * 3600), n_steps)  # time in days
    for i in range(n_steps - 1):
        # Compute the rate of temperature change
        dT_dt = ((1 - alpha) * S / 4 - epsilon * sigma * T[i]**4) / Cp_atm
        T[i + 1] = T[i] + dT_dt * dt  # update the temperature at the next time step

    # Plot results
    plt.figure(figsize=(8, 5))
    plt.plot(time, T, label="Temperature Evolution", color="blue")
    plt.axhline(Teq, color="red", linestyle="--", label=f"Teq ≈ {Teq:.2f} K")
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (K)")
    plt.title("Temperature Evolution to Radiative Equilibrium")
    plt.legend()
    plt.grid()
    plt.show()

def cooling_simulation(Cp, label):
    """
    Simulate temperature decay when the Sun stops shining and compute e-folding time.
    
    Parameters:
    Cp (float): Heat capacity (J/K)
    label (str): Label for the simulation (Atmosphere or Upper Ocean)
    Teq (float): Radiative equilibrium temperature in Kelvin
    
    Returns:
    None
    """
    S = 0  # set to zero because the Sun has stopped shining
    
    # Time stepping parameters
    dt = 3600  # timestep (1 hour)
    t_max = 26500 * 24 * 3600  # maximum simulation time (in seconds)
    n_steps = int(t_max / dt)  # number of steps

    # Compute e-folding time
    target_T = Teq / np.e 
    t = 0  # start time
    T = Teq  # initial temperature 

    while T > target_T:
        # Compute rate of temperature change
        dT_dt = -epsilon * sigma * T**4 / Cp
        T += dT_dt * dt  # update temperature
        t += dt  # increment time

    # Convert time from seconds to days
    tau = t / (24 * 3600)  # e-folding time in days
    print(f"E-folding time for {label}: {tau:.1f} days")

    # Initialize temperature array for simulation
    T_sim = np.zeros(n_steps)
    T_sim[0] = Teq  # start from equilibrium temperature

    # Time evolution loop
    time = np.linspace(0, t_max / (24 * 3600), n_steps)  # in days
    for i in range(n_steps - 1):
        dT_dt = ((1 - alpha) * S / 4 - epsilon * sigma * T_sim[i]**4) / Cp  # cooling term
        T_sim[i + 1] = T_sim[i] + dT_dt * dt  # update temperature

    # Plot results
    plt.plot(time, T_sim, label=f"{label} (τ ≈ {tau:.1f} days)")


# 1) What is the radiative equilibrium temperature of Earth?

Teq = ((1-alpha)*S/(4*epsilon*sigma)) ** (0.25)
print(f"The radiative equilibrium temperature of Earth is {Teq:.2f}K")


# 2) How does this depend on the choice of the time step?

'''
The choice of the time step primarily affects numerical simulations 
of Earth's energy balance over time rather than the radiative equilibrium 
temperature itself, which is derived analytically. However, if we're solving 
for temperature evolution using a time-stepping approach (e.g., with a finite difference method), 
the time step (Δt) can impact the stability and accuracy of the solution:

1. Numerical Stability:
* If Δ𝑡 is too large, the numerical solution may become unstable, 
leading to unrealistic temperature fluctuations.
* Stability often depends on the heat capacity and the rate of energy exchange 
in the system.

2. Accuracy:
* A smaller time step results in a more accurate solution but requires more computational power.
* A larger time step speeds up the simulation but can introduce errors.

3. Physical Interpretation:
* If we're modeling how the system approaches equilibrium, Δt determines how quickly 
temperature updates at each step.
* A large time step might overshoot the equilibrium temperature, while a very small time step 
will take longer to converge.
'''

EBM(1e7, 190)

# 3) Change the heat capacity so as to model the upper 70 meters of the ocean rather than
# the atmosphere (Cp = 2.95e8 J/K). Does the equilibrium temperature change? 

EBM(2.95e8, 4500)

'''
The Teq does not change because the equation is not dependent on Cp
'''

# 4) Is the mean temperature the same if there is a diurnal cycle? Annual cycle? "Glacial" cycle?

'''
The mean temperature will not necessarily be the same under different timescales of forcing 
(diurnal, annual, glacial) because of thermal inertia and nonlinear responses in the system.

Diurnal Cycle
* The atmosphere responds quickly to daily heating and cooling.
* The mean temperature over a day might be close to the equilibrium temperature, 
but the fluctuations will be large, especially over land (where heat capacity is low).
* The ocean, with a higher heat capacity, will smooth out these variations.

Annual Cycle (Seasons) 
* If the Earth's tilt and orbit variations are included, we get seasonal changes in solar insolation 
  (due to the radiation reaching Earth at a different angle).
* The mean annual temperature should be close to the equilibrium temperature, but seasonal variations will cause differences
  (e.g., winter vs. summer).
* Oceans delay seasonal responses due to their higher Cp (in comparison to the lands Cp).

Glacial Cycle (Ice Ages)
* These cycles occur over thousands to millions of years, influenced by Milankovitch cycles 
  (orbital variations).
* Ice sheets and greenhouse gas changes affect albedo and long-term heat storage, 
  which can lead to different mean temperatures. Parameters such as ice-albedo, CO₂ changes etc can shift 
  the mean temperature significantly.
'''

# 5) If the Sun should stop, how long does it take for the temperature to become a factor of e-1
# its equilibrium value (i.e what is the e-folding time) for both the atmosphere and upper ocean ?

plt.figure(figsize=(8, 5))
cooling_simulation(1e7, "Atmosphere")
cooling_simulation(2.95e8, "Upper Ocean")
plt.axhline(Teq / np.e, color="black", linestyle="--", label=f"T_eq / e ≈ {Teq / np.e:.2f} K")
plt.xlabel("Time (days)")
plt.ylabel("Temperature (K)")
plt.title("Temperature Decay After Sun Stops")
plt.legend()
plt.grid()
plt.show()


# 6) How can the e-folding time be found analytically from eq 1?

'''
Cp*dT/dt = (1-a)*(S/4) - epsilon*sigma*T**4

we set S=0 so that 

Cp*dT/dt = - epsilon*sigma*T**4

moving dt and T around we have 

dT/T**4 = - epsilon*sigma*dt / Cp

we apply the method of separation of variables and integrate

∫ dT/T**4 = - ∫ epsilon*sigma*dt / Cp

- 1 / 3* T**3 = -epsilon*sigma*t / Cp + C

in order to find C we set T=To for t=0 and C is calculated to be equal to 

C = - 1 / 3* To**3

replacing C with its value and removing all minus signs we get that 

1 / 3* T**3 = epsilon*sigma*t / Cp + 1 / 3* To**3

for T = Teq/e (e-folding time)

epsilon*sigma*t / Cp = 1 / 3* (Teq/e)**3 - 1 / 3* To**3

t = Cp /3*epsilon*sigma * [1 /(Teq/e)**3 - 1 /To**3]

'''

# 7) What are some limitations of this model, and what are their consequences?

'''
- No Latitudinal Variation
The model doesn't account for the equator-to-pole temperature gradient or heat transport by winds and ocean currents.

- No Vertical Structure
The atmosphere is treated as a single heat reservoir with no stratification.
It cannot capture phenomena like the greenhouse effect acting differently at different altitudes.

- No Seasonal or Orbital Effects
The model assumes constant solar radiation (except for the stopping-sun experiment).
It does not account for seasonal variations due to Earth's axial tilt or long-term Milankovitch cycles.

- No variation in albedo or emissivity.
Temperature is dependent on both of these parameters so we lose accuracy in calculations.

- No Feedback Mechanisms
Key climate feedbacks (e.g., water vapor, clouds, particulate matter etc) are missing.
The model might underestimate or overestimate climate sensitivity to changes in solar or greenhouse forcing.

- No Heat Transport
The model doesn't simulate horizontal energy transport by winds or ocean currents.
This could affect the accuracy of response times and equilibrium temperatures.

'''

# 8) How would you construct a coupled atmosphere-ocean model with this level of complexity?

'''
To construct a coupled atmosphere-ocean model, we need to implement ways to include
the above limitations. We should also introduce an additional equation governing 
the heat exchange between the atmosphere and the upper ocean. The atmosphere and ocean 
will exchange heat, with the ocean acting as a thermal buffer that delays the temperature response (due to higher Cp).

We can define two coupled energy balance equations:

1. Atmospheric energy balance:
    dT_atm/dt = ((1 - alpha) * S / 4 - epsilon * sigma * T_atm**4 - H) / Cp_atm

2. Ocean energy balance:
    dT_ocean/dt = ((1 - alpha) * S / 4 - epsilon * sigma * T_atm**4 + H) / Cp_ocean

Where:
    - H = k * (T_atm - T_ocean) represents the heat exchange between the atmosphere and ocean.
    - k is the heat transfer coefficient.
    - Cp_atm is the heat capacity of the atmosphere.
    - Cp_ocean is the heat capacity of the upper ocean.
'''
