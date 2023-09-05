import matplotlib
import json
import inspect
import warnings
from collections import OrderedDict
from plot_serializer.adapters import Plot, MatplotlibAdapter
from plot_serializer.exceptions import OntologyWarning


class Serializer:
    def __init__(self, p=None, suppress_ontology_warnings=False) -> None:
        self._plot = None
        self._axis = None
        if p is not None:
            self.load_plot(p)
        if suppress_ontology_warnings is True:
            warnings.filterwarnings(action="ignore", category=OntologyWarning)
        pass

    @property
    def plot(self):
        return self._plot

    @plot.setter
    def plot(self, plot):
        if not issubclass(type(plot), Plot):
            raise TypeError("plot must be a subclass of plot_serializer.adapters.Plot")
        else:
            self._plot = plot

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, axis):
        self._axis = axis

    def load_plot(self, p) -> None:
        if isinstance(p, matplotlib.pyplot.Figure):
            self.plot = MatplotlibAdapter(p)
            self.axis = MatplotlibAdapter(p).get_axes(p)
        else:
            raise NotImplementedError(
                "Only matplotlib is implemented. Make sure you submit a matplotlib.pyplot.Figure object."
            )

    def to_json(self, header=["id"]) -> str:
        """Exports plot to json.

        Args:
            header (list, optional): list of keys to appear on top of the json string. Defaults to ["id"].

        Returns:
            str: json string
        """
        d = json.loads(json.dumps(self.plot, default=lambda o: self._getattrorprop(o)))
        od = OrderedDict()
        for k in header:
            od[k] = d[k]
        for k in set(d.keys()) - set(header):
            od[k] = d[k]
        return json.dumps(od)

    def add_plot_metadata(self, id=None, title=None, caption=None):
        """Adds plot metadata to the plot object.

        Args:
            id (int, optional): the id of plot. Defaults to None.
            title (str, optional): the title of plot. Defaults to None.
            caption (str, optional): the caption of plot. Defaults to None.
        """
        self.plot.id = id
        self.plot.title = title
        self.plot.caption = caption

    def add_axis_metadata(
        self,
        axis_index,
        title,
        xlabel,
        ylabel,
        xunit=None,
        yunit=None,
        xquantity=None,
        yquantity=None,
    ):
        """Adds axis metadata to the axis selected by index

        Args:
            axis_index (int): the index of subplot
            title (str): the title of subplot
            xlabel (str): the label of x-axis
            ylabel (str): the label of y-axis
            xunit (str, optional): the unit of x-axis. Defaults to None.
            yunit (str, optional): the unit of y-axis. Defaults to None.
            xquantity (str, optional): the quantity of x-axis. Defaults to None.
            yquantity (str, optional): the quantity of y-axis. Defaults to None.
        """
        # TODO: überprüfen die anzhal des subplots
        self.plot.axes[axis_index].title = title
        self.plot.axes[axis_index].xlabel = xlabel
        self.plot.axes[axis_index].ylabel = ylabel
        self.plot.axes[axis_index].xunit = xunit
        self.plot.axes[axis_index].yunit = yunit
        self.plot.axes[axis_index].xquantity = xquantity
        self.plot.axes[axis_index].yquantity = yquantity

    def add_custom_metadata(self, metadata_dict: dict, obj) -> None:
        """Adds custom metadata to a specified object.

        Args:
            metadata_dict (dict): dictionary that contains metadata to add
            obj (plot_serializer.plot.Plot | plot_serializer.plot.Axis |
                plot_serializer.plot.Trace): Plot, Axis, or Trace
                assigned to Serializer

        Raises:
            ValueError: obj must be the plot or its attributes assigned to the
                Serializer function

        Returns:
            plot_serializer.plot.Plot |
            plot_serializer.plot.Axis |
            plot_serializer.plot.Trace: obj including metadata
        """
        if obj in [
            self.plot,
            *self.plot.axes,
            *[t for a in self.plot.axes for t in a.traces],
        ]:
            for k, v in metadata_dict.items():
                setattr(obj, k, v)
            return obj
        else:
            raise ValueError(
                "obj must be the plot or its attributes assigned to the Serializer function"
            )

    def _getattrorprop(self, o):
        d = dict(
            (k, v)
            for k, v in inspect.getmembers(o)
            if not k.startswith("_")
            and not inspect.ismethod(v)
            and not inspect.isfunction(v)
        )
        return d
