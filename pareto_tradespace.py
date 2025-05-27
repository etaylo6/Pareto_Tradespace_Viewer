import sys
import os
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QTextEdit
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import venn

# Pareto mask function
def pareto_mask(data: np.ndarray) -> np.ndarray:
    is_pareto = np.ones(data.shape[0], dtype=bool)
    for i, row in enumerate(data):
        if is_pareto[i]:
            dominates = np.all(data >= row, axis=1) & np.any(data > row, axis=1)
            dominates[i] = False
            if np.any(dominates):
                is_pareto[i] = False
    return is_pareto

class DataVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pareto Trade-space Viewer")
        self.data = None
        self.pareto = None
        self.numeric_cols = []
        self.venn_scatter = None
        self.venn_indices = []
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        # Plot area
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        plot_layout.addWidget(self.canvas)
        layout.addWidget(plot_widget, stretch=3)

        # Controls
        ctrl = QWidget()
        ctrl_layout = QVBoxLayout(ctrl)
        layout.addWidget(ctrl, stretch=1)

        self.load_btn = QPushButton("Load CSV")
        self.load_btn.clicked.connect(self.load_data)
        ctrl_layout.addWidget(self.load_btn)

        ctrl_layout.addWidget(QLabel("Visualization Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Scatter Plot", "Venn Diagram"])
        self.mode_combo.currentIndexChanged.connect(self.update_plot)
        ctrl_layout.addWidget(self.mode_combo)

        ctrl_layout.addWidget(QLabel("X Axis:"))
        self.x_combo = QComboBox()
        self.x_combo.currentIndexChanged.connect(self.update_plot)
        ctrl_layout.addWidget(self.x_combo)

        ctrl_layout.addWidget(QLabel("Y Axis:"))
        self.y_combo = QComboBox()
        self.y_combo.currentIndexChanged.connect(self.update_plot)
        ctrl_layout.addWidget(self.y_combo)

        ctrl_layout.addWidget(QLabel("Point Details:"))
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        ctrl_layout.addWidget(self.details, stretch=1)

        # Connect events
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('pick_event', self.on_pick)

    def show_details(self, idx: int):
        row = self.data.iloc[idx]
        html = ['<table>']
        for col, val in row.items():
            v = f"{val:.3f}" if isinstance(val, float) else str(val)
            html.append(f'<tr><td><b>{col}</b></td><td>{v}</td></tr>')
        html.append('</table>')
        self.details.setHtml('\n'.join(html))

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        self.data = pd.read_csv(path)
        numeric = self.data.select_dtypes(include=[np.number])
        self.numeric_cols = list(numeric.columns)
        self.pareto = pareto_mask(numeric.values) if self.numeric_cols else np.zeros(len(self.data), dtype=bool)

        cols = list(self.data.columns)
        self.x_combo.clear(); self.x_combo.addItems(cols)
        self.y_combo.clear(); self.y_combo.addItems(cols)
        if cols: self.x_combo.setCurrentIndex(0)
        if len(cols) > 1: self.y_combo.setCurrentIndex(1)

        # Enable Venn only for 2–6 numeric dims
        ven_item = self.mode_combo.model().item(1)
        ven_item.setEnabled(2 <= len(self.numeric_cols) <= 6)
        if not ven_item.isEnabled():
            self.mode_combo.setCurrentIndex(0)

        self.update_plot()

    def update_plot(self):
        if self.data is None:
            return
        mode = self.mode_combo.currentText()

        # --- Venn Diagram Mode ---
        if mode == "Venn Diagram" and 2 <= len(self.numeric_cols) <= 6:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            arr = self.data[self.numeric_cols].values
            D = arr.shape[1]

            # Compute subspace-Pareto sets (exclude each dim)
            subfronts = []
            for j in range(D):
                subdims = [k for k in range(D) if k != j]
                mask = pareto_mask(arr[:, subdims])
                subfronts.append(set(np.where(mask)[0]))

            # All Pareto-optimal indices
            pareto_idx = np.where(self.pareto)[0]

            # Region dictionary: bitkey -> indices
            region_dict = {}
            # For each point, build inverted bitkey: 1 = excels in dim j
            for idx in pareto_idx:
                bitkey = ''.join(
                    '1' if idx not in subfronts[j] else '0'
                    for j in range(D)
                )
                region_dict.setdefault(bitkey, []).append(idx)

            # Blank interior labels and draw Venn
            labels = venn.get_labels([region_dict.get(k, []) for k in sorted(region_dict)], fill=["number","logic"])
            labels = {k: '' for k in labels}
            getattr(venn, f"venn{D}")(labels, names=self.numeric_cols, ax=ax)

            # Style set titles
            for txt in ax.texts:
                if txt.get_text() in self.numeric_cols:
                    txt.set_color('black')
                    x, y = txt.get_position()
                    txt.set_position((x, y + 0.05))

            # Precompute polar mapping
            pareto_arr = arr[pareto_idx]
            global_max = pareto_arr.max(axis=0)
            norm_factor = np.linalg.norm(global_max)
            angles = np.linspace(0, 2*np.pi, D, endpoint=False)
            max_r = 0.15

            # Hard-coded region centers
            region_centers = {
                2: {'10': (0.26,0.30), '01': (0.74,0.30), '11': (0.50,0.30)},
                3: {'001': (0.50,0.27), '010': (0.73,0.65), '011': (0.61,0.46),
                     '100': (0.27,0.65), '101': (0.39,0.46), '110': (0.50,0.65), '111': (0.50,0.51)}
            }[D]

            xs, ys, self.venn_indices = [], [], []
            # Place each point in its region
            for key, indices in region_dict.items():
                if key not in region_centers:
                    # fallback to full front
                    key = max(region_centers.keys(), key=lambda k: k.count('1'))
                x0, y0 = region_centers[key]
                for idx in indices:
                    perf = arr[idx]
                    # radius = distance from Pareto ideal
                    r = max_r * (np.linalg.norm(global_max - perf) / norm_factor)
                    # angle = weighted by performance
                    perf_norm = perf / global_max
                    vec = np.array([np.sum(perf_norm * np.cos(angles)),
                                    np.sum(perf_norm * np.sin(angles))])
                    theta = np.arctan2(vec[1], vec[0])
                    xs.append(x0 + r*np.cos(theta))
                    ys.append(y0 + r*np.sin(theta))
                    self.venn_indices.append(idx)

            self.venn_scatter = ax.scatter(xs, ys, color='black', s=30, picker=5)
            self.canvas.draw()
            return

        # --- Scatter Plot Mode ---
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x_col = self.x_combo.currentText(); y_col = self.y_combo.currentText()
        if x_col and y_col:
            x = self.data[x_col]; y = self.data[y_col]
            ax.scatter(x[~self.pareto], y[~self.pareto], picker=True)
            ax.scatter(x[self.pareto], y[self.pareto], picker=True, color='red')
            ax.set_xlabel(x_col); ax.set_ylabel(y_col)
        self.canvas.draw()

    def on_click(self, event):
        if self.data is None or event.xdata is None:
            return
        mode = self.mode_combo.currentText()
        xdata, ydata = event.xdata, event.ydata
        if mode == "Scatter Plot":
            pts = self.data[[self.x_combo.currentText(), self.y_combo.currentText()]].dropna().values
            d = np.sum((pts - [xdata, ydata])**2, axis=1)
            i = d.argmin()
            self.show_details(i)
        else:
            coords = np.array(self.venn_scatter.get_offsets())
            d = np.sum((coords - [xdata, ydata])**2, axis=1)
            i = d.argmin()
            if d[i] < 0.02:
                self.show_details(self.venn_indices[i])

    def on_pick(self, event):
        if self.data is None or self.mode_combo.currentText() != "Venn Diagram":
            return
        if event.artist is not self.venn_scatter:
            return
        i = event.ind[0]
        self.show_details(self.venn_indices[i])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viz = DataVisualizer()
    viz.show()
    sys.exit(app.exec_())