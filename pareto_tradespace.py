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

# Pareto mask

def pareto_mask(data: np.ndarray) -> np.ndarray:
    is_pareto = np.ones(data.shape[0], dtype=bool)
    for i, row in enumerate(data):
        if is_pareto[i]:
            dominates = np.all(data >= row, axis=1) & np.any(data > row, axis=1)
            dominates[i] = False
            if np.any(dominates):
                is_pareto[i] = False
    return is_pareto

# Ensure venn module is importable
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
import venn

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

        # Events
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('pick_event', self.on_pick)

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        self.data = pd.read_csv(path)
        numeric = self.data.select_dtypes(include=[np.number])
        self.numeric_cols = list(numeric.columns)
        if self.numeric_cols:
            self.pareto = pareto_mask(numeric.values)
        else:
            self.pareto = np.zeros(len(self.data), dtype=bool)

        cols = list(self.data.columns)
        self.x_combo.clear(); self.x_combo.addItems(cols)
        self.y_combo.clear(); self.y_combo.addItems(cols)
        if cols: self.x_combo.setCurrentIndex(0)
        if len(cols)>1: self.y_combo.setCurrentIndex(1)

        ven_item = self.mode_combo.model().item(1)
        ven_item.setEnabled(2<=len(self.numeric_cols)<=6)
        if not ven_item.isEnabled(): self.mode_combo.setCurrentIndex(0)

        self.update_plot()

    def update_plot(self):
        if self.data is None:
            return
        mode = self.mode_combo.currentText()
        # Venn mode
        if mode=="Venn Diagram" and 2<=len(self.numeric_cols)<=6:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            numeric = self.data[self.numeric_cols]
            arr = numeric.values
            pareto_arr = arr[self.pareto]
            max_by_dim = pareto_arr.max(axis=0)
            sets_list = [set(np.where(self.pareto & (arr[:,j]==max_by_dim[j]))[0])
                         for j in range(len(self.numeric_cols))]
            labels = venn.get_labels(sets_list, fill=["number","logic"])
            func = getattr(venn, f"venn{len(self.numeric_cols)}")
            func(labels, names=self.numeric_cols, ax=ax)

            region_centers = {
                2:{"10":(0.26,0.30),"01":(0.74,0.30),"11":(0.50,0.30)},
                3:{"001":(0.50,0.27),"010":(0.73,0.65),"011":(0.61,0.46),
                   "100":(0.27,0.65),"101":(0.39,0.46),"110":(0.50,0.65),"111":(0.50,0.51)}
            }
            centers = region_centers[len(self.numeric_cols)]
            xs, ys, self.venn_indices = [], [], []
            for idx in np.where(self.pareto)[0]:
                key="".join("1" if arr[idx,j]==max_by_dim[j] else "0"
                              for j in range(len(self.numeric_cols)))
                if key in centers:
                    x0,y0 = centers[key]
                    dx,dy = (np.random.rand(2)-0.5)*0.05
                    xs.append(x0+dx); ys.append(y0+dy)
                    self.venn_indices.append(idx)
            self.venn_scatter = ax.scatter(xs, ys, color='black', s=30, picker=5)
            self.canvas.draw()
            return
        # Scatter mode
        if self.canvas.figure is not self.figure:
            self.canvas.figure = self.figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x_col = self.x_combo.currentText(); y_col = self.y_combo.currentText()
        if x_col and y_col:
            x=self.data[x_col]; y=self.data[y_col]
            ax.scatter(x[~self.pareto], y[~self.pareto], picker=True)
            ax.scatter(x[self.pareto], y[self.pareto], picker=True, color='red')
            ax.set_xlabel(x_col); ax.set_ylabel(y_col)
        self.canvas.draw()

    def on_click(self, event):
        if self.data is None or event.xdata is None: return
        mode=self.mode_combo.currentText(); xdata,ydata=event.xdata,event.ydata
        if mode=="Scatter Plot":
            x_col,y_col=self.x_combo.currentText(),self.y_combo.currentText()
            df=self.data[[x_col,y_col]].dropna(); pts=df.values
            d=np.sum((pts-[xdata,ydata])**2,axis=1); i=d.argmin();
            self.details.setText(self.data.iloc[i].to_string())
        else:
            coords=np.array(list(zip(*self.venn_scatter.get_offsets().T))).T if False else np.array(self.venn_scatter.get_offsets())
            d=np.sum((coords-[xdata,ydata])**2,axis=1); i=d.argmin()
            if d[i]<0.02:
                self.details.setText(self.data.iloc[self.venn_indices[i]].to_string())

    def on_pick(self, event):
        if self.data is None or self.mode_combo.currentText()!="Venn Diagram": return
        if event.artist!=self.venn_scatter: return
        i=event.ind[0]
        self.details.setText(self.data.iloc[self.venn_indices[i]].to_string())

if __name__=='__main__':
    app=QApplication(sys.argv)
    viz=DataVisualizer()
    viz.show()
    sys.exit(app.exec_())
