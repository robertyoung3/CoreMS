# Molecular Formula Search in CoreMS

This guide explains how to perform molecular formula assignments in CoreMS, the parameters that control the search process, and how the database is used and updated.

## Basic Molecular Formula Search

```python
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.molecular_id.factory.classification import HeteroatomsClassification

# Configure search settings
mass_spectrum.molecular_search_settings.error_method = "None"
mass_spectrum.molecular_search_settings.min_ppm_error = -0.2
mass_spectrum.molecular_search_settings.max_ppm_error = 0.2

mass_spectrum.molecular_search_settings.min_dbe = 0
mass_spectrum.molecular_search_settings.max_dbe = 50

mass_spectrum.molecular_search_settings.isProtonated = True  # protonated or deprotonated
mass_spectrum.molecular_search_settings.isRadical = False
mass_spectrum.molecular_search_settings.isAdduct = False  

# Set atom constraints
mass_spectrum.molecular_search_settings.usedAtoms["C"] = (1, 90)
mass_spectrum.molecular_search_settings.usedAtoms["H"] = (4, 200)
mass_spectrum.molecular_search_settings.usedAtoms["O"] = (1, 25)
mass_spectrum.molecular_search_settings.usedAtoms["N"] = (0, 5)
mass_spectrum.molecular_search_settings.usedAtoms["S"] = (0, 2)

# Run the search
SearchMolecularFormulas(mass_spectrum, first_hit=True).run_worker_mass_spectrum()

# Get assignment statistics
mass_spectrum.percentile_assigned(report_error=True)

# Classify by heteroatom content
mass_spectrum_by_classes = HeteroatomsClassification(mass_spectrum, choose_molecular_formula=True)
```

## Understanding the Molecular Formula Search Process

The molecular formula search in CoreMS follows these steps:

1. **Database Candidate Generation**: When `run_worker_mass_spectrum()` is called, CoreMS first generates a set of candidate formulas based on the constraints specified in `molecular_search_settings`.

2. **Formula Database Querying**: The candidate formulas are queried from the SQL database based on nominal mass and heteroatom class.

3. **Peak-by-Peak Assignment**: Each peak in the mass spectrum is compared against potential formula matches within the error range specified.

4. **Isotopologue Calculation**: For each potential formula match, isotopologue patterns are calculated and matched against other peaks in the spectrum.

5. **Assignment Selection**: Molecular formulas are assigned to peaks based on mass accuracy, isotope pattern matching, and other criteria.

## Core Classes Involved

### SearchMolecularFormulas

The main class that handles the molecular formula search process:

```python
# Create an instance with a mass spectrum
search = SearchMolecularFormulas(mass_spectrum, first_hit=False, find_isotopologues=True)

# Run the search on the entire spectrum
search.run_worker_mass_spectrum()

# Or run the search on specific peaks
search.run_worker_ms_peaks(peaks_list)
```

Parameters:
- `mass_spectrum_obj`: The mass spectrum to search
- `sql_db`: Optional SQL database connection (created automatically if not provided)
- `first_hit`: If True, skips peaks that already have a formula assigned
- `find_isotopologues`: If True, calculates and searches for isotopologue patterns


## MolecularFormulaSearchSettings Parameters

The `molecular_search_settings` object controls how molecular formula searches are performed:

### Mass Error Parameters

```python
# Error method (controls how error window adjusts during search)
# Options: "None", "distance", "lowest", "average", "symmetrical"
mass_spectrum.molecular_search_settings.error_method = "None"

# Initial error window in ppm
mass_spectrum.molecular_search_settings.min_ppm_error = -0.2
mass_spectrum.molecular_search_settings.max_ppm_error = 0.2

# For dynamic error methods, the error range around the determined center
mass_spectrum.molecular_search_settings.mz_error_range = 0.2
```

### Structural Constraints

```python
# Double Bond Equivalent (DBE) range
mass_spectrum.molecular_search_settings.min_dbe = 0
mass_spectrum.molecular_search_settings.max_dbe = 50

# H/C ratio constraints
mass_spectrum.molecular_search_settings.min_hc_filter = 0.3  
mass_spectrum.molecular_search_settings.max_hc_filter = 3.0  

# O/C ratio constraints 
mass_spectrum.molecular_search_settings.min_oc_filter = 0  
mass_spectrum.molecular_search_settings.max_oc_filter = 1.3  
```

### Ion Types to Search

```python
# Search for protonated/deprotonated ions ([M+H]+ or [M-H]-)
mass_spectrum.molecular_search_settings.isProtonated = True

# Search for radical ions (M+• or M-•)
mass_spectrum.molecular_search_settings.isRadical = False

# Separate search for adduct ions based on ionization mode
mass_spectrum.molecular_search_settings.isAdduct = True  

# Adduct atoms to search in positive mode
mass_spectrum.molecular_search_settings.adduct_atoms_pos = ['Na', 'K']

# Adduct atoms to search in negative mode
mass_spectrum.molecular_search_settings.adduct_atoms_neg = ['Cl']
```

### Elemental Constraints

Define the min and max number of each atom type to consider:

```python
# Format: element_symbol = (min_count, max_count)
mass_spectrum.molecular_search_settings.usedAtoms["C"] = (1, 90)
mass_spectrum.molecular_search_settings.usedAtoms["H"] = (4, 200)
mass_spectrum.molecular_search_settings.usedAtoms["O"] = (1, 25)
mass_spectrum.molecular_search_settings.usedAtoms["N"] = (0, 5)
mass_spectrum.molecular_search_settings.usedAtoms["S"] = (0, 2)
```

### Isotopologue Matching Parameters

```python
# Abundance error range for isotopologue matching (percentage)
mass_spectrum.molecular_search_settings.min_abun_error = -25
mass_spectrum.molecular_search_settings.max_abun_error = 10
```

### Other Parameters

```python
# URL for the formula database
mass_spectrum.molecular_search_settings.url_database = "postgresql+psycopg2://username:password@host:port/database"

# Enable verbose output during processing
mass_spectrum.molecular_search_settings.verbose_processing = True

# Database chunk size (to manage memory usage)
mass_spectrum.molecular_search_settings.db_chunk_size = 100
```

## SQL Database and MolecularCombinations

CoreMS uses a PostgreSQL database to store molecular formula information. The database is queried based on constraints defined in the molecular search settings.

### Database Initialization and Population

When you first run a molecular formula search, if the database is empty, CoreMS will:

1. Generate all possible molecular formulas matching your constraints
2. Calculate their properties (exact mass, DBE, etc.)
3. Store them in the database for future searches

This initial calculation process can be time-consuming but only happens once for each unique combination of elements and their ranges. Subsequent searches with the same elements will be much faster as they'll use the pre-calculated formulas from the database.

```python
# The first time you run a search with specific elements, the database is populated
search = SearchMolecularFormulas(mass_spectrum, first_hit=True)
search.run_worker_mass_spectrum()
# At this point, formulas for the elements specified in usedAtoms are calculated and stored
```

### Adding New Elements to the Database

If you want to search for formulas containing elements that weren't included in previous searches:

1. Simply add the new element to your `usedAtoms` dictionary
2. Run a new search with these constraints
3. CoreMS will automatically calculate and add formulas with this element to the database

```python
# Add a new element (chlorine) to your search constraints
mass_spectrum.molecular_search_settings.usedAtoms["Cl"] = (0, 2)

# Run the search again
search = SearchMolecularFormulas(mass_spectrum, first_hit=True)
search.run_worker_mass_spectrum()

# This will generate and store formulas containing chlorine in the database
```

This on-demand database population approach means:
1. You don't need to delete containers or rebuild the database when adding new elements
2. The database grows over time to include formulas for all elements you've ever searched for
3. Initial searches with new elements will be slower due to the calculation and storage process

### Limitations and Database Management

There are practical limits to this approach:

1. **Memory and Storage Constraints**: Adding many elements with wide ranges can generate billions of possible formulas, potentially exceeding database capacity.

2. **Computation Time**: Initial formula generation with new elements can be very slow, especially for heavy elements with wide ranges.

3. **Schema Limitations**: The database schema must support the elements you want to search. If you need exotic elements not included in the schema, you would need to modify the database structure.

If you need to completely rebuild the database (e.g., to add elements not in the schema):

```bash
# Stop the CoreMS container
docker stop coremsapp_container

# Remove the database volume (this will delete all stored formulas)
docker volume rm corems_db_data

# Restart the CoreMS container
docker start coremsapp_container

# The database will be empty and ready to be populated with new formulas
```

### Database Connection

```python
from corems.molecular_id.factory.molecularSQL import MolForm_SQL

# Connect to the database
db_url = "postgresql+psycopg2://coremsappuser:coremsapppnnl@molformdb:5432/coremsapp"
sql = MolForm_SQL(url=db_url)

# Execute a query
result = sql.session.execute(text("SELECT COUNT(*) FROM molecularformula")).scalar()
print(f"Total records: {result}")

# Close the connection when done
sql.close()
```

### Database Structure

The molecular formula database contains pre-computed molecular formulas with the following key information:

- Formula string (e.g., "C6H12O6")
- Exact mass
- Molecular weight
- DBE (Double Bond Equivalent)
- Heteroatom class (e.g., "O6")
- Elemental counts (C, H, N, O, S, etc.)

### MolecularCombinations

The `MolecularCombinations` class is the key component that generates molecular formulas on-demand and queries existing formulas from the database:

```python
from corems.molecular_id.factory.MolecularLookupTable import MolecularCombinations

# Create combinations object with database connection
combinations = MolecularCombinations(sql_db)

# Generate classes based on search settings
# This will create formulas if they don't exist in the database
classes = combinations.runworker(mass_spectrum.molecular_search_settings)
```

This process:
1. Determines all valid heteroatom class combinations based on the search settings
2. Checks if these formulas already exist in the database
3. Generates and stores any missing formulas needed for your search
4. Returns the candidate formulas grouped by class for the search process

The actual formula generation happens in the `get_classes_in_mono_formula()` method, which:
1. Identifies all classes (combinations of elements) needed for the search
2. For each class, generates all possible formula combinations within the specified constraints
3. Calculates properties for each formula (exact mass, DBE, etc.)
4. Stores new formulas in the database

## Understanding Error Methods

CoreMS provides several methods for adjusting the error window during a search:

- **None**: Uses fixed min/max ppm error values
- **distance**: Updates error window based on the closest error from previous assignments
- **lowest**: Updates error window centered on the lowest error found so far
- **average**: Updates error window centered on the running average of errors
- **symmetrical**: Uses a fixed symmetric error window around a specified center

## Using Results After Assignment

After performing a formula search, you can access and visualize the results:

```python
# Get assigned peaks sorted by abundance
for mspeaks in mass_spectrum.sort_by_abundance(reverse=True)[:20]:
    for mf in mspeaks:
        print(f"Abundance: {mspeaks.abundance:.2f} | "
              f"m/z: {mf.mz_calc:.6f} | "
              f"Error: {mf.mz_error:.6f} | "
              f"DBE: {mf.dbe} | "
              f"Class: {mf.class_label} | "
              f"Formula: {mf.string_formated}")

# Get a list of all heteroatom classes
classes = mass_spectrum_by_classes.get_classes()

# Plot van Krevelen diagram for a specific class
mass_spectrum_by_classes.plot_van_krevelen("S1 O4")

# Plot DBE vs carbon number for a class
mass_spectrum_by_classes.plot_dbe_vs_carbon_number("S1 O4")

# Export results to CSV
mass_spectrum.to_csv("/path/to/output.csv")

# Get results as pandas DataFrame
df = mass_spectrum.to_dataframe()
```

### HeteroatomsClassification

After assignment, this class helps analyze and visualize results by heteroatom class:

```python
# Create classification object
mass_spectrum_by_classes = HeteroatomsClassification(mass_spectrum, choose_molecular_formula=True)

# Get list of classes found
classes = mass_spectrum_by_classes.get_classes()

# Create visualizations
mass_spectrum_by_classes.plot_van_krevelen("O4")
mass_spectrum_by_classes.plot_dbe_vs_carbon_number("S1 O4")
```

## Common Issues and Solutions

1. **No Formulas Assigned**:
   - Check that your error window is appropriate for your mass accuracy
   - Ensure your elemental constraints are not too restrictive
   - Verify the database connection is working

2. **Too Many Formulas per Peak**:
   - Narrow the error window
   - Add additional constraints (DBE, H/C ratio)
   - Set `first_hit=True` to assign only the first matching formula

3. **Database Connection Issues**:
   - Verify database URL is correct
   - Check network connectivity to the database server
   - Ensure proper credentials are provided

4. **Memory Issues with Large Datasets**:
   - Decrease the `db_chunk_size` parameter
   - Process subsets of the spectrum separately
   - Increase available RAM or use a machine with more memory

## Advanced: LC-MS Targeted Searches

For LC-MS data, CoreMS provides additional functionality for targeted molecular formula searching:

```python
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulasLC

# Create a search object for the LC-MS data
lcms_search = SearchMolecularFormulasLC(lcms_obj)

# Run search on mass features
lcms_search.run_mass_feature_search()
```

This performs molecular formula assignment on the apex spectra of detected features.

## Isotope Pattern Calculation and Matching

When CoreMS assigns molecular formulas, it uses isotope pattern matching as a key validation step. This process involves:

### Isotope Pattern Generation

For each candidate formula that matches a peak within the mass error tolerance:

1. **Theoretical Isotope Pattern Calculation**: 
   ```python
   # Inside the SearchMolecularFormulaWorker.find_formulas method
   # For each potential formula match:
   isotopologues = molecular_formula.isotopologues(
       min_abundance,  # Minimum abundance threshold
       ms_peak_abundance,  # Abundance of the monoisotopic peak
       mass_spectrum_obj.dynamic_range  # Dynamic range of the instrument
   )
   ```

   This calls the `isotopologues()` method of the MolecularFormula class, which:
   - Calculates the exact masses of all theoretical isotopologues
   - Determines their theoretical abundances relative to the monoisotopic peak
   - Returns only isotopologues above the minimum abundance threshold
   - Considers the instrument's dynamic range for abundance calculations

2. **Search for Isotopologue Peaks**:
   CoreMS then searches for each predicted isotopologue in the mass spectrum:
   ```python
   # For each isotopologue formula:
   for isotopologue_formula in isotopologues:
       # Search for peaks matching this isotopologue
       first_index, last_index = mass_spectrum_obj.get_nominal_mz_first_last_indexes(
           isotopologue_formula.mz_nominal_calc
       )
       
       for ms_peak_iso in mass_spectrum_obj[first_index:last_index]:
           error = self.calc_error(ms_peak_iso.mz_exp, isotopologue_formula.mz_calc)
           
           if min_ppm_error <= error <= max_ppm_error:
               # Check abundance error
               abundance_error = self.calc_error(
                   isotopologue_formula.abundance_calc,
                   ms_peak_iso.abundance,
                   method="perc"
               )
               
               if min_abun_error <= abundance_error <= max_abun_error:
                   # Link the isotopologue to its monoisotopic peak
                   # and track the matching information
                   // ...
   ```

### Abundance Error Calculation

The abundance error for isotopologue matching is calculated as a percentage difference between the theoretical and experimental abundances:

```python
abundance_error = ((theoretical_abundance - experimental_abundance) / theoretical_abundance) * 100
```

- `min_abun_error` and `max_abun_error` specify the acceptable range (default: -25% to +10%)
- This asymmetric default range accounts for the tendency of instruments to underestimate isotopologue abundances

### Isotope Score Calculation

CoreMS doesn't calculate an explicit isotope pattern score (like cosine similarity) by default. Instead, it uses a binary approach:

1. If an isotopologue peak is found within both mass error and abundance error tolerances, it's considered a match
2. The formula is assigned if its isotopologues match expected peaks in the spectrum
3. Each matching isotopologue increases confidence in the formula assignment

If you need a quantitative isotope pattern matching score, you could compute it post-assignment:

```python
# Example pseudocode for calculating isotope pattern similarity
def calculate_isotope_similarity(ms_peak, molecular_formula):
    score = 0
    total_theoretical_abundance = 0
    matched_abundance = 0
    
    # For each isotopologue expected by the formula
    for iso_formula in molecular_formula.expected_isotopologues:
        total_theoretical_abundance += iso_formula.abundance_calc
        
        # Check if this isotopologue was matched to a peak
        if iso_formula.mspeak_index_mono_isotopic is not None:
            matched_abundance += iso_formula.abundance_calc
    
    # Calculate a simple matching score
    if total_theoretical_abundance > 0:
        score = matched_abundance / total_theoretical_abundance
        
    return score
```

## Formula Selection When Multiple Candidates Match

When multiple molecular formulas match the same peak within the error tolerance, CoreMS uses several approaches to select the best formula:

### Default Selection Strategy

By default, CoreMS returns all matching formulas that satisfy the error criteria, sorted by mass error:

1. Each peak can have multiple formula assignments (`MolecularFormulaList`)
2. When exporting results, the formula with the lowest mass error is typically selected

### Using the first_hit Parameter

```python
# Only assign the first formula found for each peak
search = SearchMolecularFormulas(mass_spectrum, first_hit=True)
```

Setting `first_hit=True` makes CoreMS skip peaks that already have a formula assigned, effectively assigning only the first matching formula to each peak.

### Formula Selection in HeteroatomsClassification

When creating visualizations or analyzing results by compound class, the `HeteroatomsClassification` class has a parameter to choose how to handle multiple formula assignments:

```python
# Choose the best formula based on defined criteria
classes = HeteroatomsClassification(mass_spectrum, choose_molecular_formula=True)
```

When `choose_molecular_formula=True`, the following criteria are used (in order):
1. Isotopologue presence - formulas with matching isotopologues are preferred
2. Mass error - the formula with the lowest mass error is preferred
3. Formula simplicity - formulas with fewer heteroatoms are preferred

### Implementing Custom Selection Logic

You can implement your own formula selection logic by iterating through the assigned formulas:

```python
# Example: Select formulas with lowest H/C ratio when multiple matches exist
for ms_peak in mass_spectrum:
    if ms_peak.number_of_assignments > 1:
        best_formula = None
        lowest_hc_ratio = float('inf')
        
        for formula in ms_peak:
            hc_ratio = formula.H / formula.C if formula.C > 0 else float('inf')
            if hc_ratio < lowest_hc_ratio:
                lowest_hc_ratio = hc_ratio
                best_formula = formula
        
        # Remove all formulas except the best one
        ms_peak._MolecularFormulaList = [best_formula]
        ms_peak._molecular_formulas_dict = {best_formula.string_formated: best_formula}
        ms_peak._number_of_assignments = 1
```

## Key Classes for Isotope Pattern Calculation

The isotope pattern calculation and matching functionality is implemented across several classes:

1. **MolecularFormula** (corems.molecular_formula.factory.MolecularFormulaFactory): 
   - Contains the `isotopologues()` method that generates theoretical isotope patterns
   - Manages information about detected isotopologues with properties like `mspeak_mf_isotopologues_indexes`

2. **SearchMolecularFormulaWorker** (corems.molecular_id.search.molecularFormulaSearch):
   - Handles finding isotopologues in the mass spectrum using error tolerances
   - Links monoisotopic peaks with their isotopologues
   
3. **Atoms** (corems.encapsulation.constant.atoms):
   - Contains isotope masses and natural abundances used in isotope calculations
   
The core calculation is rooted in combinatorial probability based on the natural abundances of isotopes for each element in the formula. This calculation considers:

1. The probability of each isotope combination
2. The exact mass of each isotopologue
3. The abundance relative to the monoisotopic peak

## References to Scientific Literature

The isotope pattern calculation and matching approach in CoreMS is based on established methods in the field:

1. Kind, T., & Fiehn, O. (2006). Metabolomic database annotations via query of elemental compositions: Mass accuracy is insufficient even at less than 1 ppm. BMC Bioinformatics, 7, 234.

2. Kind, T., & Fiehn, O. (2007). Seven Golden Rules for heuristic filtering of molecular formulas obtained by accurate mass spectrometry. BMC Bioinformatics, 8, 105.

3. Dittwald, P., Claesen, J., Burzykowski, T., Valkenborg, D., & Gambin, A. (2013). BRAIN: a universal tool for high-throughput calculations of the isotopic distribution for mass spectrometry. Analytical Chemistry, 85(4), 1991-1994.

These methods emphasize the importance of isotope pattern matching as a critical filter for molecular formula assignments, particularly for complex samples where mass accuracy alone is insufficient.

## Molecular Formula Organization by Heteroatom Class

In CoreMS, "heteroatom class" serves as the fundamental organizing principle for both formula generation and results visualization. A heteroatom class represents a specific combination of heteroatoms (anything other than C and H) in a molecular formula.

### Classes in Database Organization

When CoreMS generates and stores molecular formulas in the database, it organizes them by heteroatom class:

1. **Class Definition**: Each class is defined by its heteroatom count (e.g., "O4" for formulas with 4 oxygen atoms, "N1O2" for formulas with 1 nitrogen and 2 oxygen atoms)
2. **Database Structure**: Formulas in the database are tagged with their corresponding class
3. **Query Efficiency**: When searching, CoreMS first identifies relevant classes based on your constraints, then queries formulas within those classes

```python
# MolecularCombinations determines what classes to search for
from corems.molecular_id.factory.MolecularLookupTable import MolecularCombinations

combinations = MolecularCombinations(sql_db)
classes = combinations.runworker(mass_spectrum.molecular_search_settings)
# 'classes' is a list of heteroatom class combinations to search
```

### Classes in Results Visualization

After formula assignment, CoreMS uses the same class concept to organize and visualize results:

```python
# HeteroatomsClassification organizes results by class for visualization
from corems.molecular_id.factory.classification import HeteroatomsClassification

# Group assigned formulas by heteroatom class
mass_spectrum_by_classes = HeteroatomsClassification(
    mass_spectrum, choose_molecular_formula=True
)

# Get all classes detected in your sample
detected_classes = mass_spectrum_by_classes.get_classes()
print(f"Classes found: {detected_classes}")

# Plot results for a specific class
mass_spectrum_by_classes.plot_van_krevelen("O4")
mass_spectrum_by_classes.plot_dbe_vs_carbon_number("N1O2")
```

The `HeteroatomsClassification` class provides several methods for class-based visualization:

1. **Van Krevelen Diagrams** (`plot_van_krevelen()`): Plots O/C vs H/C ratios for compounds in a class
2. **DBE vs Carbon Number** (`plot_dbe_vs_carbon_number()`): Plots double bond equivalent against carbon number
3. **Class Distribution** (`plot_ms_class_distribution()`): Shows the distribution of compound classes in the sample
4. **Mass Defect Analysis** (`plot_mz_error()`): Shows mass error distribution by class

### Benefits of Class-Based Organization

This consistent use of heteroatom class throughout CoreMS provides several advantages:

1. **Computational Efficiency**: Reduces the search space by dividing formulas into manageable groups
2. **Chemical Insight**: Provides natural chemical categorization of compounds
3. **Data Interpretation**: Enables comparison across samples based on compound class distribution
4. **Visualization Simplification**: Allows examining specific compound types in isolation

### Example Workflow Using Classes

```python
# 1. Run formula search
SearchMolecularFormulas(mass_spectrum).run_worker_mass_spectrum()

# 2. Organize results by class
mass_spectrum_by_classes = HeteroatomsClassification(
    mass_spectrum, choose_molecular_formula=True
)

# 3. Get available classes
classes = mass_spectrum_by_classes.get_classes()
print(f"Detected classes: {classes}")

# 4. Compare class distributions
mass_spectrum_by_classes.plot_ms_class_distribution()

# 5. Examine specific classes of interest
for class_name in ["O4", "O5", "O6"]:
    if class_name in classes:
        mass_spectrum_by_classes.plot_van_krevelen(class_name)
        mass_spectrum_by_classes.plot_dbe_vs_carbon_number(class_name)
```

This two-way integration of heteroatom class for both formula generation/searching and results visualization is a core design principle in CoreMS that facilitates both efficient processing and meaningful chemical interpretation of complex mass spectrometry data.
