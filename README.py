# Simple-BB84-python-script
Simple python script in order to simulate BB84 protocol developed during my cybersecurity laboratories at Politecnico di Torino
import random
import time
import sys

# ---------------------------------------------------------------------------
# UX / TIMING HELPERS
# ---------------------------------------------------------------------------

DELAY_SEC = 1.5  # Default delay between major steps

def print_header(title):
    """Prints a step header with a delay."""
    print(f"\n... processing ...\n")
    time.sleep(DELAY_SEC)
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_delayed(text, delay=0.3):
    """Prints a line and waits a fraction of a second (typewriter effect)."""
    print(text)
    time.sleep(delay)

def get_int_input(prompt, default):
    """Helper to get an integer from user."""
    while True:
        try:
            user_in = input(f"{prompt} [default={default}]: ")
            if user_in.strip() == "":
                return default
            val = int(user_in)
            if val <= 0:
                print("Please enter a positive integer.")
                continue
            return val
        except ValueError:
            print("Invalid input. Please enter an integer.")

def get_float_input(prompt, default):
    """Helper to get a float (0.0 - 1.0)."""
    while True:
        try:
            user_in = input(f"{prompt} [default={default}]: ")
            if user_in.strip() == "":
                return default
            val = float(user_in)
            if 0.0 <= val <= 1.0:
                return val
            print("Please enter a value between 0.0 and 1.0")
        except ValueError:
            print("Invalid input.")

def get_bool_input(prompt, default):
    """Helper to get a boolean (y/n)."""
    default_str = "y" if default else "n"
    user_in = input(f"{prompt} (y/n) [default={default_str}]: ").lower().strip()
    if user_in == "":
        return default
    return user_in.startswith('y')

# ---------------------------------------------------------------------------
# QUANTUM HELPERS
# ---------------------------------------------------------------------------

def random_bits(n):
    return [random.randint(0, 1) for _ in range(n)]

def random_bases(n):
    # "+" = rectilinear, "x" = diagonal
    return [random.choice(["+", "x"]) for _ in range(n)]

def basis_symbol(basis):
    return "+" if basis == "+" else "×"

def measure_with_explanation(bit, prep_basis, meas_basis, owner_name):
    """
    Measures a photon and returns the result AND an explanation string.
    """
    if prep_basis == meas_basis:
        # Quantum Mechanics: Same basis -> State is preserved
        return bit, f"(Basis MATCH: {basis_symbol(prep_basis)}=={basis_symbol(meas_basis)} -> Deterministic)"
    else:
        # Quantum Mechanics: Different basis -> State is destroyed, result is random
        result = random.randint(0, 1)
        return result, f"(Basis MISMATCH: {basis_symbol(prep_basis)}!={basis_symbol(meas_basis)} -> RANDOM result)"

# ---------------------------------------------------------------------------
# MAIN SIMULATION
# ---------------------------------------------------------------------------

def bb84_simulation():
    print("\n" + "#" * 60)
    print("###      BB84 QKD PROTOCOL - INTERACTIVE SIMULATION      ###")
    print("#" * 60 + "\n")

    # --- 0. User Configuration ---
    print("--- Configuration ---")
    N = get_int_input("Number of photons to transmit", 10)
    EVE_ENABLED = get_bool_input("Enable Eve (Eavesdropper)?", True)
    
    EVE_PROB = 0.0
    if EVE_ENABLED:
        EVE_PROB = get_float_input("Probability of Eve intercepting a photon", 0.5)
    
    DECOY_ENABLED = get_bool_input("Enable Decoy States (Security check)?", True)
    
    input("\n>> Configuration complete. Press ENTER to start the simulation...")

    # --- 1. Alice Preparation ---
    # Alice generates random bits and bases
    alice_bits = random_bits(N)
    alice_bases = random_bases(N)

    # Decoy setup
    pulse_type = []
    if DECOY_ENABLED:
        for _ in range(N):
            # 30% chance of being a decoy
            pulse_type.append("Decoy" if random.random() < 0.3 else "Signal")
    else:
        pulse_type = ["Signal"] * N

    print_header("Step 1: Alice prepares photons")
    print(f"{'Idx':<4} | {'Type':<8} | {'Bit':<3} | {'Basis':<5} | {'Description'}")
    print("-" * 60)
    
    for i in range(N):
        b_sym = basis_symbol(alice_bases[i])
        desc = f"Alice encodes bit {alice_bits[i]} in {b_sym} basis"
        print_delayed(f"{i:<4d} | {pulse_type[i]:<8} | {alice_bits[i]:<3} | {b_sym:<5} | {desc}")
        transit_bits, transit_bases = list(alice_bits), list(alice_bases)

    # --- 2. Eve Interception ---
    print_header("Step 2: Transmission (Eve's Activity)")
    
    if EVE_ENABLED:
        print(f"Eve is ACTIVE with interception probability: {EVE_PROB*100:.1f}%")
        print("-" * 75)
        for i in range(N):
            if random.random() < EVE_PROB:
                # Eve intercepts
                eve_basis = random.choice(["+", "x"])
                # Eve measures using Alice's current state
                measured_bit, explanation = measure_with_explanation(alice_bits[i], alice_bases[i], eve_basis, "Eve")
                
                print_delayed(f"Photon {i:02d}: [INTERCEPTED] Eve chose {basis_symbol(eve_basis)}. {explanation}")
                print_delayed(f"           -> Eve resends bit {measured_bit} in basis {basis_symbol(eve_basis)} to Bob.")
                
                # IMPORTANT: The photon heading to Bob is now changed to what Eve measured/resent
                transit_bits[i] = measured_bit
                transit_bases[i] = eve_basis
            else:
                print_delayed(f"Photon {i:02d}: [--- OK --- ] Eve did not touch this photon.")
            time.sleep(0.1)
    else:
        print("Eve is DISABLED. Photons travel undisturbed to Bob.")

    # --- 3. Bob Measurement ---
    print_header("Step 3: Bob Measures")
    
    bob_bases = random_bases(N)
    bob_results = []
    
    print(f"{'Idx':<4} | {'Incoming (A/E)':<14} | {'Bob Basis':<9} | {'Result':<6} | {'Debug Info'}")
    print("-" * 75)

    for i in range(N):
        # Bob measures the incoming photon (which might be from Alice OR Eve)
        # Note: We use alice_bits/bases[i] here because they represent the current state of the photon 
        # (potentially modified by Eve in Step 2)
        measure_res, explain = measure_with_explanation(transit_bits[i], transit_bases[i], bob_bases[i], "Bob")
        bob_results.append(measure_res)
        
        inc_basis_sym = basis_symbol(alice_bases[i])
        bob_basis_sym = basis_symbol(bob_bases[i])
        
        print_delayed(f"{i:<4d} | {alice_bits[i]} in {inc_basis_sym:<9} | {bob_basis_sym:<9} | {measure_res:<6} | {explain}")

    # --- 4. Sifting ---
    print_header("Step 4: Sifting (Public Discussion of Bases)")
    print("Alice and Bob publicly compare bases. If bases match, they keep the bit.")
    print("-" * 80)
    print(f"{'Idx':<4} | {'A Basis':<7} | {'B Basis':<7} | {'Match?':<6} | {'A Bit':<5} | {'B Bit':<5} | {'Status'}")
    print("-" * 80)

    sifted_alice = []
    sifted_bob = []
    sifted_types = [] # To track if it was Signal or Decoy

    for i in range(N):
        a_sym = basis_symbol(alice_bases[i]) # Note: This is the photon state JUST before Bob measured
        b_sym = basis_symbol(bob_bases[i])
        
        match = (a_sym == b_sym)
        status_str = "KEPT" if match else "DISCARDED"
        
        print_delayed(f"{i:<4d} | {a_sym:<7} | {b_sym:<7} | {str(match):<6} | {alice_bits[i]:<5} | {bob_results[i]:<5} | {status_str}")

        if match:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])
            sifted_types.append(pulse_type[i])

    # --- 5. Analysis ---
    print_header("Step 5: Security Analysis & QBER")
    
    # Calculate QBER
    if len(sifted_alice) == 0:
        print("No bits remained after sifting! (Try increasing N)")
        return

    errors = 0
    print(f"{'Idx':<4} | {'A Bit':<5} | {'B Bit':<5} | {'Check'}")
    print("-" * 40)
    
    # We only reveal a subset of keys in real life, but here we show all for didactic purposes
    for j in range(len(sifted_alice)):
        a = sifted_alice[j]
        b = sifted_bob[j]
        is_err = (a != b)
        if is_err: 
            errors += 1
            check_str = "<< ERROR (Potential Eve)"
        else:
            check_str = "OK"
            
        print_delayed(f"{j:<4d} | {a:<5} | {b:<5} | {check_str}")

    qber = errors / len(sifted_alice)
    
    print("\n--- RESULTS ---")
    print(f"Total Sifted Bits: {len(sifted_alice)}")
    print(f"Total Errors:      {errors}")
    print(f"Calculated QBER:   {qber*100:.2f}%")
    
    # Decoy Analysis
    if DECOY_ENABLED:
        print("\n--- DECOY STATE ANALYSIS ---")
        sig_count = sum(1 for t in sifted_types if t == "Signal")
        dec_count = sum(1 for t in sifted_types if t == "Decoy")
        print(f"Signal pulses kept: {sig_count}")
        print(f"Decoy pulses kept:  {dec_count}")
        if sig_count > 0:
            print(f"Ratio (Decoy/Signal): {dec_count/sig_count:.2f}")
        else:
            print("Ratio: N/A (No signal pulses)")

    # --- 6. Final Verdict ---
    print_header("Step 6: Final Decision")
    
    # Threshold usually around 11% for standard BB84
    THRESHOLD = 0.11 
    
    print(f"Security Threshold: {THRESHOLD*100}%")
    
    if qber > THRESHOLD:
        print("RESULT: [ UNSAFE ]")
        print("Reason: QBER is too high. Eavesdropping is likely.")
        print("Action: ABORT PROTOCOL.")
    else:
        print("RESULT: [ SAFE ]")
        print("Reason: QBER is within acceptable limits.")
        print("Action: Proceed to Error Correction and Privacy Amplification.")
    
    print("\nSimulation Finished.")

if __name__ == "__main__":
    try:
        bb84_simulation()
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
