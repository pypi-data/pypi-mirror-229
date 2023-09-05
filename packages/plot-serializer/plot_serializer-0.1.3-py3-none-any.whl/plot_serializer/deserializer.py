import json
import matplotlib.pyplot as plt

from plot_serializer.plot import Plot, Axis, Trace


class Deserializer:
    def __init__(self) -> None:
        self._plot = None
        pass

    def from_json(self, filename):
        """Creates a Plot object out of a JSON file created with Serializer.

        Args:
            filename (str): path to the JSON file

        Returns:
            plot_serializer.Plot: Plot object from the JSON file
        """
        with open(filename, "r") as openfile:
            # Reading from json file
            d = json.load(openfile)
        p = Plot()
        p.axes = []
        for a in d["axes"]:
            axis = Axis()
            axis.traces = []
            for t in a["traces"]:
                plotted_element = Trace()
                axis.traces.append(self.dict_to_object(t, plotted_element))
            p.axes.append(axis)
        return p

    def dict_to_object(self, d, o):
        for key, value in d.items():
            setattr(o, key, value)
        return o

    def json_to_matplotlib(self, json_file):
        """Converts the Plot objects from JSON to matplotlib.pyplot.

        Args:
            json_file (str): path to the JSON file

        Returns:
            matplotlib.pyplot.Figure: matplotlib.pyplot.Figure created from the JSON file
        """
        self.plot = self.from_json(json_file)
        fig = plt.figure()
        for axis in self.plot.axes:
            ax = fig.add_subplot()
            for t in axis.traces:
                ax.plot(t.xdata, t.ydata, label=t.label, color=t.color)
        return fig
