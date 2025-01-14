from corems.encapsulation.factory.processingSetting import MolecularLookupDictSettings
from corems.molecular_id.factory.MolecularLookupTable import MolecularCombinations


def initialize_molecular_database():
    # Initialize settings with default values
    settings = MolecularLookupDictSettings()

    # Optionally modify defaults
    # settings.usedAtoms = {
    #     "C": (1, 90),
    #     "H": (4, 200),
    #     "O": (0, 30),
    #     "N": (0, 5),
    #     "S": (0, 2),
    #     "P": (0, 0),
    #     "Cl": (0, 0),
    # }

    # Create and populate database
    molecular_combinations = MolecularCombinations()
    molecular_combinations.runworker(settings)


if __name__ == "__main__":
    initialize_molecular_database()
