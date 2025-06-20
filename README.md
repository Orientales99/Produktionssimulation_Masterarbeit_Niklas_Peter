# Produktionssimulation_Masterarbeit_Niklas_Peter

Um die Simulation zu starten, kann das Programm auf zwei unterschiedliche Weisen ausgeführt werden.
Die verwendeten Bibliotheken sind in der Datei [requirements](./requirements.txt) dokumentiert.
___
Die erste Variante ist, dass die Datei [app.py](./app.py) ausgeführt wird.
Mit der Methode wird auch ein Userinterface gestartet, welches es ermöglicht einige Simulationseinstellungen vor dem Start zu tätigen.

Sollten detaillierte Anpassungen vorgenommen werden, dann sollte das Programm mit der Datei [run_simulation](./src/run_simulation.py) in dem Order [src](./src) ausgeführt werden.

Die manuelle Anpassung der Simulationseinstellungen findet in den Konfigurationsdateien im Order [resource](./resources) statt

Wenn ein Topologie Manager eingesetzt wird, dann muss dieser den Materialfluss der Produkte zwischen den einzelnen Maschinen kennen.
Damit das der Fall ist, muss die Simulation mit den eingestellten Parametern einmal ohne die Verwendung eines Topologie Managers durchgeführt werden.
Im Anschluss müssen die Dateien aus dem Ordner [simulation_output_data](./simulation_output_data) vollständig in den Ordner [simulation_basis_for_topologie_manager](./resources/simulation_basis_for_topologie_manager)
kopiert werden, bevor der Durchlauf mit dem Topologie Manager stattfindet.

___

Wenn eine Simulation zu einem bestimmten Zeitpunkt nachgebildet werden soll, dann wird das über den Start der Datei [run_rebuilding_parts](./src/run_rebuilding_parts.py) gemacht.

Dabei ist darauf zu achten, dass in dem Ordner [simulation_output_data](./simulation_output_data) die notwendigen Dateien der nachzubildenden Simulation sind.

___
Beachten beim Verändern der Parameter:

- Wenn die Anzahl der Maschinen verändert wird, dann muss auch die Anzahl der möglichen Positionen in der Datei [potential_machine_and_store_positioning](./resources/potential_machine_and_store_positioning.json).
- Wenn die Größe der Produktionsfläche angepasst wird, dann müssen die möglichen Positionen ebenfalls angepasst werden.
- Die Änderung des Datums für die Bestellaufträge muss sowohl in der Datei [data_list](./resources/date_list.json), als auch in [simulation_starting_conditions](./resources/simulation_starting_conditions.json) stattfinden.

Es ist zu beachten, dass die Verwendung der Visualisierung den Simulationsprozess erheblich verlangsamt.

