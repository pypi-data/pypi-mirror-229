class Plot:
    # __slots__ = ["_id", "_axes", "_title", "_caption"]
    def __init__(self) -> None:
        self._id = None
        self._axes = None
        self._title = None
        self._caption = None
        self._dataset = None
        pass

    @property
    def axes(self):
        return self._axes

    @axes.setter
    def axes(self, axes):
        self._axes = axes

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        if type(id) is str:
            self._id = id
        else:
            raise TypeError("id must be a string.")

    def add_plot_metadata(self, title, id, caption):
        self._id = id
        self._title = title
        self._caption = caption

    def add_custom_metadata(self, metadata_dict: dict) -> None:
        for k, v in metadata_dict.items():
            setattr(self.plot, k, v)


class Axis:
    def __init__(self, unit_ontology="default") -> None:
        self._traces = None
        self._title = None
        self._xlabel = None
        self._ylabel = None
        self._xquantity = None
        self._yquantity = None
        self._xunit = None
        self._yunit = None
        self.unit_ontology = unit_ontology
        pass

    @property
    def traces(self):
        return self._traces

    @traces.setter
    def traces(self, ts):
        if not all(isinstance(p, Trace) for p in ts):
            raise TypeError("Must be a list of instances of Trace.")
        self._traces = ts

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if not isinstance(title, str):
            raise TypeError("title must be a string.")
        self._title = title

    @property
    def xlabel(self):
        return self._xlabel

    @xlabel.setter
    def xlabel(self, xlabel):
        if not isinstance(xlabel, str):
            raise TypeError("xlabel must be a string.")
        self._xlabel = xlabel

    @property
    def ylabel(self):
        return self._ylabel

    @ylabel.setter
    def ylabel(self, ylabel):
        if not isinstance(ylabel, str):
            raise TypeError("ylabel must be a string.")
        self._ylabel = ylabel

    @property
    def xquantity(self):
        return self._xquantity

    @xquantity.setter
    def xquantity(self, xquantity):
        if (not isinstance(xquantity, str)) and (xquantity is not None):
            raise TypeError("xquantity must be a string or None.")
        self._xquantity = xquantity

    @property
    def yquantity(self):
        return self._yquantity

    @yquantity.setter
    def yquantity(self, yquantity):
        if (not isinstance(yquantity, str)) and (yquantity is not None):
            raise TypeError("yquantity must be a string or None.")
        self._yquantity = yquantity

    @property
    def xunit(self):
        return self._xunit

    @xunit.setter
    def xunit(self, xunit):
        if (not isinstance(xunit, str)) and (xunit is not None):
            raise TypeError("xunit must be a string or None.")
        # if not unit_in_ontology(xunit, self.unit_ontology):
        #     warn(
        #         "Unit {} is not in the selected ontology.".format(xunit),
        #         OntologyWarning,
        #     )
        self._xunit = xunit

    @property
    def yunit(self):
        return self._yunit

    @yunit.setter
    def yunit(self, yunit):
        if (not isinstance(yunit, str)) and (yunit is not None):
            raise TypeError("yunit must be a string or None.")
        # if not unit_in_ontology(yunit, self.unit_ontology):
        #     warn(
        #         "Unit {} is not in the selected ontology.".format(yunit),
        #         OntologyWarning,
        #     )
        self._yunit = yunit


class Trace:
    def __init__(self) -> None:
        self._xdata = None
        self._ydata = None
        self._label = None
        self._type = None
        self._color = None

    @property
    def xdata(self):
        return self._xdata

    @xdata.setter
    def xdata(self, data):
        if not isinstance(data, list):
            raise TypeError("xdata must be a list.")
        if self.ydata is not None and len(data) != len(self.ydata):
            raise RuntimeError("Length of xdata and ydata differs.")
        self._xdata = data

    @property
    def ydata(self):
        return self._ydata

    @ydata.setter
    def ydata(self, data):
        if not isinstance(data, list):
            raise TypeError("ydata must be a list.")
        if self.xdata is not None and len(data) != len(self.xdata):
            raise RuntimeError("Length of xdata and ydata differs.")
        self._ydata = data

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        if not isinstance(label, str):
            raise TypeError("label must be a string.")
        self._label = label

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if not isinstance(color, str):
            raise TypeError("color must be a string")
        self._color = color


class Dataset:
    def __init__(self) -> None:
        self._URL = None
        self._file_name = None
        pass
