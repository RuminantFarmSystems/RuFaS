"""This file provides a few examples of alternative logic for the main percolation method.
The purpose of these examples is to improve the visual clarity and readability of the method.

In addition to the structure, variable names have also been selected to improve clarity and comprehension.
"""

# TODO: delete this file before merging

class Percolation:
    def __init__(self, soil_data):
        self.data = soil_data

    def percolate_a(self, has_seasonal_high_water_table: bool) -> None:
        """alternative percolation method (A)

        Details: this version aims to keep the logic from the original but drastically
        reduce the amount of nesting and if else blocks, for improved readability"""
        layer_count = len(self.data)
        deepest_layer = layer_count - 1  # stupid pythonic counting

        for layer_number in range(layer_count):
            current_layer = self.data.layers[layer_number]

            # special case at the bottom of the profile
            if current_layer == deepest_layer and current_layer.temperature > 0:
                percolated_water = self._percolate_between_layers(24, current_layer, self.data.vadose_zone_layer)
                current_layer.soil_water_content -= percolated_water
                self.data.vadose_zone_layer.soil_water_content += percolated_water
                continue  # done with this iteration

            # normal case for all other layers
            layer_below = self.data.layers[layer_number + 1]
            can_percolate = self._determine_if_percolation_allowed(layer_below.soil_water_content,
                                                                  layer_below.field_capacity_content,
                                                                  layer_below.saturation_content,
                                                                  has_seasonal_high_water_table)
            if current_layer.temperature > 0 and can_percolate:
                percolated_water = self._percolate_between_layers(24, current_layer, layer_below)
                current_layer.soil_water_content -= percolated_water
                layer_below.soil_water_content += percolated_water


    def percolate_b(self, has_seasonal_high_water_table: bool):
        """alternative percolation method (A)

        Details: this version simply decides how to specify the underlying layer. This version is intuitive because it
        treats the underlying layer the same no matter what.

        It would inolve altering the vadose_zone_layer attribute to work properly with
        _determine_if_percolation_allowed(). I wonder if setting saturation_content = math.inf would work.
        """
        layer_count = len(self.data)
        deepest_layer = layer_count - 1  # stupid pythonic counting

        for layer_number in range(layer_count):  # loop through each layer
            current_layer = self.data.layers[layer_number]

            # get the appropriate underlying layer
            if current_layer < deepest_layer:
                layer_below = self.data.layers[layer_number + 1]
            else:
                layer_below = self.data.vadose_zone_layer

            # check for percolation conditions
            can_percolate = self._determine_if_percolation_allowed(layer_below.soil_water_content,
                                                                  layer_below.field_capacity_content,
                                                                  layer_below.saturation_content,
                                                                  has_seasonal_high_water_table)
            if current_layer.temperature > 0 and can_percolate:
                percolated_water = self._percolate_between_layers(24, current_layer, layer_below)
                current_layer.soil_water_content -= percolated_water
                layer_below.soil_water_content += percolated_water









