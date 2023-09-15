import matplotlib.pyplot as plt


class GraphGenerator:
    def generate_graph(self, filtered_pool: dict, graph_info: dict):
        graph_type = graph_info["graph_type"]
        if graph_type == 'Line graph':
            self._line_graph(filtered_pool, graph_info)

    def _line_graph(self, filtered_pool: dict, graph_info: dict):

        fig = plt.figure()
        for key in filtered_pool.keys():
            plt.plot(filtered_pool[key]['values'])
        fig.show()
