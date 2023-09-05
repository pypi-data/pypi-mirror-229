"""Adapters


"""

from plot_serializer.plot import Plot, Axis, Trace


class MatplotlibAdapter(Plot):
    def __init__(self, fig) -> None:
        super().__init__()
        self.axes = self.get_axes(fig)
        pass

    def get_axes(self, fig):
        axes = []
        for axis in fig.axes:
            a = Axis()
            a.traces = self.get_traces(axis)
            axes.append(a)
        return axes

    def get_traces(self, axis):
        lines = self.get_lines(axis)
        # collections = self.get_collections()
        return lines

    def get_lines(self, axis):
        lines = []
        if len(axis.lines) > 0:
            for line in axis.lines:
                pe = Trace()
                pe.xdata = list(line.get_xdata())
                pe.ydata = list(line.get_ydata())
                pe.label = line.get_label()
                pe.color = line.get_color()
                pe.type = str(type(line))
                lines.append(pe)
        return lines
