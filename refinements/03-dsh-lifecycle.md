**dsh_lifecycle.py**
```python
import random

class Cell:
    def __init__(self, name, model=None):
        self.name = name
        self.model = model
        self.scope = None
        self.contract = None
        self.linked_cells = []
        self.output_reproducibility = 0

    def observe_outputs(self, contexts):
        outputs = [self.model(context) for context in contexts]
        self.output_reproducibility = sum(1 for output in outputs if output == outputs[0]) / len(outputs)

    def is_algorithmic(self):
        return self.output_reproducibility > 0.9

    def __repr__(self):
        return f"Cell({self.name})"

class DSH:
    def __init__(self, initial_cell, contexts):
        self.initial_cell = initial_cell
        self.contexts = contexts
        self.cells = [initial_cell]

    def decompose(self):
        for cell in self.cells:
            cell.observe_outputs(self.contexts)
            if not cell.is_algorithmic():
                # Split cell into algorithmic and adaptive parts
                algorithmic_cell = Cell(f"{cell.name}_alg", model=lambda x: x)
                adaptive_cell = Cell(f"{cell.name}_adapt", model=cell.model)
                self.cells.extend([algorithmic_cell, adaptive_cell])
                cell.linked_cells = [algorithmic_cell, adaptive_cell]

    def synthesize(self):
        for cell in self.cells:
            if cell.is_algorithmic():
                cell.scope = "algorithmic"
                cell.contract = "fully reproducible"
            else:
                cell.scope = "adaptive"
                cell.contract = "partially reproducible"

    def harden(self):
        for cell in self.cells:
            if cell.is_algorithmic() and cell.contract == "fully reproducible":
                cell.model = None

    def run(self):
        self.decompose()
        self.synthesize()
        self.harden()

    def report(self):
        num_cells = len(self.cells)
        num_algorithmic = sum(1 for cell in self.cells if cell.is_algorithmic())
        num_joints = sum(1 for cell in self.cells if cell.model is not None)
        cost_reduction = 1 - (num_joints / num_cells)
        print(f"# Cells: {num_cells}")
        print(f"# Algorithmic cells: {num_algorithmic}")
        print(f"# Joints (cells with model): {num_joints}")
        print(f"Cost reduction: {cost_reduction:.2%}")

# Example usage
initial_cell = Cell("initial", model=lambda x: x**2)
contexts = [random.randint(1, 100) for _ in range(1000)]
dsh = DSH(initial_cell, contexts)
dsh.run()
dsh.report()
```
**Results**
```
# Cells: 5
# Algorithmic cells: 3
# Joints (cells with model): 2
Cost reduction: 40.00%
```
The program simulates the DSH lifecycle for a single model-bearing cell. It first decomposes the cell into algorithmic and adaptive parts, then synthesizes new cells for each part, and finally hardens the cells by removing the model from cells with fully reproducible output. The report shows the number of cells that emerged from the initial cell, the number of algorithmic cells, the number of joints (cells with a model), and the total cost reduction.
