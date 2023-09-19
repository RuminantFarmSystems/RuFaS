import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


class GraphGenerator:
    def generate_graph(self, filtered_pool: dict, graph_info: dict, graph_path: str):
        graph_type = graph_info["graph_type"]
        if graph_type == 'Line graph':
            self._line_graph(filtered_pool, graph_info, graph_path)

    def _line_graph(self, filtered_pool: dict, graph_info: dict, graph_path: str):

        fig, ax = plt.subplots()
        for key in filtered_pool.keys():
            ax.plot(filtered_pool[key]['values'])
        self._customize_graph(fig, graph_info)
        # plt.show()
        plt.savefig(graph_path)

    def _customize_graph(self, fig, graph_info: dict):
        if 'title' in graph_info.keys():
            fig.axes[0].set_title(graph_info['title'])
        if 'x_label' in graph_info.keys():
            fig.axes[0].set_xlabel(graph_info['x_label'])
        if 'y_label' in graph_info.keys():
            fig.axes[0].set_xlabel(graph_info['y_label'])
        # TODO: add more functionalities
        return fig
