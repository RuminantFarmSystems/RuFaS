import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


class GraphGenerator:
    def generate_graph(self, filtered_pool: dict, graph_info: dict, graph_path: str, **kwargs):
        graph_type_funcs={
        "Line Graph": self._line_graph,
        "Bar Graph": self._bar_graph,
        }
        graph_type_funcs[graph_info["graph_type"]](filtered_pool, graph_info, graph_path)

    def _customize_graph(self, fig, graph_info: dict, **kwargs):
        if 'title' in graph_info.keys():
            fig.axes[0].set_title(graph_info['title'])
        if 'x_label' in graph_info.keys():
            fig.axes[0].set_xlabel(graph_info['x_label'])
        if 'y_label' in graph_info.keys():
            fig.axes[0].set_xlabel(graph_info['y_label'])
        return fig

    def _line_graph(self, filtered_pool: dict, graph_info: dict, graph_path: str, **kwargs):
        fig, ax = plt.subplots()
        for key in filtered_pool.keys():
            ax.plot(filtered_pool[key]['values'])
        self._customize_graph(fig, graph_info)
        plt.savefig(graph_path)

    def _bar_graph(self, filtered_pool: dict, graph_info: dict, graph_path: str, **kwargs):
        fig, ax = plt.subplots()
        category, count = [], []

        for key in filtered_pool.keys():
            category.append(key)
            count.append(filtered_pool[key]['values'])

        ax.bar(category, count)
        self._customize_graph(fig, graph_info)
        plt.savefig(graph_path)
