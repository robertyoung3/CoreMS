# CoreMS Database Initialization Process

This guide explains how the CoreMS SQL database is initialized, populated, and updated when performing molecular formula searches.

## Overview

CoreMS uses a PostgreSQL database to store molecular formula information for efficient searching. Instead of calculating formulas on-demand for each search, CoreMS:

1. Checks if formulas meeting your search criteria already exist in the database
2. If not found, calculates the formulas and stores them in the database
3. Reuses these formulas in future searches

This document explains the details of this process, how database growth works, and how to manage the database.

## Database Initialization Flow

When running a molecular formula search for the first time, the database is empty. Here's what happens:

```
┌─────────────────────┐     ┌────────────────────┐     ┌─────────────────────┐
│                     │     │                    │     │                     │
│ SearchMolecular     │     │ Molecular          │     │ MolForm_SQL         │
│ Formulas            │────►│ Combinations       │────►│ Database            │
│                     │     │                    │     │                     │
└─────────────────────┘     └────────────────────┘     └─────────────────────┘
  Triggers search           Handles formula            Stores & retrieves
  with parameters           generation                 formula data
```

## Key Classes and Functions

The database initialization and population is handled by several key components:

### 1. MolecularCombinations Class

This class is responsible for determining which formulas need to be generated and stored:

```python
# Typically called from SearchMolecularFormulas.run_molecular_formula
classes = MolecularCombinations(sql_db).runworker(
    molecular_search_settings,
    print_time=molecular_search_settings.verbose_processing
)
```

The `runworker` method:
1. Determines all possible heteroatom class combinations based on constraints
2. For each class, checks if formulas exist in the database
3. If formulas don't exist, generates and stores them

### 2. get_classes_in_mono_formula Method

This method within `MolecularCombinations` does the actual formula generation:

```python
def get_classes_in_mono_formula(self, **kwargs):
    # ... implementation details ...
    # Determines all heteroatom classes (e.g., "O2 N1", "O4", etc.)
    # For each class, generates all possible molecular formulas
    # Stores new formulas in the database
```

### 3. MolForm_SQL Class

This class handles the SQL database interactions:

```python
# Connection
sql_db = MolForm_SQL(url="postgresql+psycopg2://user:pass@host:port/db")

# Querying existing formulas
formulas = sql_db.get_formulas_by_nominal_mass_and_class(nominal_mass, class_str)

# Storing new formulas
sql_db.add_entries_dataframe(df_formulas)
```

## Database Growth Process

The database grows based on the elements and constraints you specify in your searches:

### Initial State - Empty Database

When you first use CoreMS, the database is empty:

```sql
SELECT COUNT(*) FROM molecularformula;
-- Result: 0
```

### First Search - Basic Elements

When you run your first search with basic settings:

```python
# First search with basic elements
mass_spectrum.molecular_search_settings.usedAtoms["C"] = (1, 50)
mass_spectrum.molecular_search_settings.usedAtoms["H"] = (4, 100)
mass_spectrum.molecular_search_settings.usedAtoms["O"] = (0, 10)
SearchMolecularFormulas(mass_spectrum).run_worker_mass_spectrum()
```

The database now contains all CH and CHO formulas within these constraints:

```sql
SELECT COUNT(*) FROM molecularformula;
-- Result: Several thousand formulas
```

### Second Search - New Element

When you add a new element to your search:

```python
# Second search adding sulfur
mass_spectrum.molecular_search_settings.usedAtoms["S"] = (0, 2)
SearchMolecularFormulas(mass_spectrum).run_worker_mass_spectrum()
```

CoreMS will:
1. Keep existing CH and CHO formulas
2. Generate and add CHS, CHOS formulas to the database

### Third Search - Expanded Range

When you expand the range of an existing element:

```python
# Third search with expanded carbon range
mass_spectrum.molecular_search_settings.usedAtoms["C"] = (1, 100)
SearchMolecularFormulas(mass_spectrum).run_worker_mass_spectrum()
```

CoreMS will:
1. Keep existing formulas with C1-C50
2. Generate and add formulas with C51-C100

## How CoreMS Determines What to Generate

When deciding which formulas to generate, CoreMS follows these steps:

1. **Heteroatom Class Determination**: 
   - Creates all possible combinations of elements (e.g., "O1", "O2", "N1", "N1O1")
   - Filters combinations that exceed specified constraints

2. **Database Querying**:
   - For each class, checks if formulas exist in the database for the required nominal masses
   - If missing, generates formulas for that class and nominal mass

3. **Formula Generation**:
   - Uses combinatorial algorithms to generate all possible formulas
   - Applies constraints (DBE, HC/OC ratios, etc.)
   - Calculates properties (exact mass, DBE, etc.)

4. **Storage**:
   - Saves new formulas to the database for future use

## MolecularLookupDictSettings Role

The `MolecularLookupDictSettings` class provides default constraints for molecular formula generation:

```python
class MolecularLookupDictSettings:
    # Default element ranges if none are specified
    def __init__(self):
        self.usedAtoms = {
            "C": (1, 100),
            "H": (4, 200),
            "O": (0, 50),
            "N": (0, 10),
            "S": (0, 10),
            "P": (0, 5),
            "Na": (0, 0),
            "K": (0, 0),
            "Cl": (0, 0),
            "F": (0, 0),
            "Si": (0, 0),
            #... other defaults
        }
```

### How `usedAtoms` Overrides Affect Database Generation

When you modify `usedAtoms` in your search settings, you're not just applying a filter - you're actually determining which formulas will be generated and added to the database:

```python
# Setting constraints for your search
mass_spectrum.molecular_search_settings.usedAtoms["C"] = (1, 90)
mass_spectrum.molecular_search_settings.usedAtoms["H"] = (4, 200)
mass_spectrum.molecular_search_settings.usedAtoms["O"] = (1, 25)
mass_spectrum.molecular_search_settings.usedAtoms["N"] = (0, 5)
mass_spectrum.molecular_search_settings.usedAtoms["S"] = (0, 2)
# Adding an element not previously searched
mass_spectrum.molecular_search_settings.usedAtoms["Cl"] = (0, 2)

# This will trigger database generation for any missing formulas
# that meet these constraints, including new Cl-containing formulas
SearchMolecularFormulas(mass_spectrum).run_worker_mass_spectrum()
```

Here's what happens:

1. **Initial Database Population**: When the database is empty, the first search will generate formulas based on the specified `usedAtoms` constraints, not the default ones from `MolecularLookupDictSettings`.

2. **Adding New Elements**: When you add elements that weren't in previous searches (like "Cl" above), new formulas containing these elements will be generated and added to the database.

3. **Expanding Ranges**: If you increase the range for an element (e.g., changing C from (1,50) to (1,90)), new formulas with the expanded range will be generated and added.

4. **Database Growth**: Each unique set of constraints you use with different combinations of elements and ranges will incrementally add new formulas to the database.

5. **SQL Schema Considerations**: The database schema must include columns for any elements you want to use. If you need exotic elements that aren't in the default schema, you would need to modify the database structure.

The `MolecularLookupDictSettings` defaults are primarily used when no explicit constraints are provided, but the actual database population is driven by the specific constraints you set in `mass_spectrum.molecular_search_settings.usedAtoms`.

In summary: Yes, overriding these defaults will add new formulas to the SQL database for any combinations that don't already exist there.

## Database Schema

The CoreMS molecular formula database has a schema designed to efficiently store and query formulas:

```
Table: molecularformula
-----------------------
- id: Primary key
- formula: String (e.g., "C6H12O6")
- mass: Float (exact mass)
- class: String (e.g., "O6")
- dbe: Float (double bond equivalent)
- C, H, N, O, S, P, ...: Integer columns for each element
- HC_FILTER: Float (H/C ratio)
- OC_FILTER: Float (O/C ratio)
- etc.
```

This schema supports efficient queries based on:
1. Nominal mass
2. Heteroatom class
3. Element counts
4. DBE and ratio filters

## Performance Considerations

Formula generation can be computationally intensive:

1. **Initial Generation**: The first search with new elements can be slow as formulas are generated
2. **Subsequent Searches**: Searches using previously generated formulas are much faster
3. **Memory Usage**: Large ranges for elements can generate billions of formulas
4. **Disk Space**: The database size grows with each new combination added

## Managing the Database

If you need to rebuild or reset the database:

```bash
# Stop the CoreMS container
docker stop coremsapp_container

# Remove the database volume
docker volume rm corems_db_data

# Restart the CoreMS container
docker start coremsapp_container
```

This will recreate an empty database that will be populated when you run new searches.

## Common Questions

### Q: What happens if I specify elements not in the schema?

A: If you specify elements that aren't defined in the database schema (i.e., columns don't exist for those elements), CoreMS won't be able to store or retrieve formulas with those elements. You would need to modify the database schema to include new element columns.

### Q: Does extending ranges always generate new formulas?

A: Yes, but only for the expanded portion. If you had previously searched with C1-50 and now search with C1-100, only formulas containing C51-100 will be newly generated.

### Q: Can I pre-populate the database?

A: Yes, you can run searches with broad constraints to pre-generate formulas:

```python
# Pre-generate a comprehensive formula database
settings = mass_spectrum.molecular_search_settings
settings.usedAtoms["C"] = (1, 100)
settings.usedAtoms["H"] = (1, 200)
settings.usedAtoms["O"] = (0, 30)
settings.usedAtoms["N"] = (0, 10)
settings.usedAtoms["S"] = (0, 5)
settings.usedAtoms["P"] = (0, 3)
SearchMolecularFormulas(mass_spectrum).run_worker_mass_spectrum()
```

This will create a comprehensive database that future searches can utilize.

## Conclusion

The CoreMS database initialization process provides an efficient compromise between computation and storage. By generating molecular formulas on-demand and storing them for future use, it balances performance and flexibility, allowing for faster subsequent searches while maintaining the ability to handle diverse chemical spaces.
