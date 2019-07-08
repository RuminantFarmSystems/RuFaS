# import ration
class AnimalObject:
    # daily vertical distance, km
    DVD = 0
    
    # daily horizontal distance, km
    DHD = 0
    
    # milk production, kg
    milk_production = 0

    def calc_daily_walking_dist(self, vertical_dist_to_parlor, horizontal_dist_to_parlor):
        '''
        Calculates and sets the animal's daily vertical and horizontal walking distance (DVD and DHD).
        Args:
            vertical_dist_to_parlor: number, km
            horizontal_dist_to_parlor: number, km
        '''
        # multiplied by 2 for return trip
        self.DVD = 2 * vertical_dist_to_parlor * self.times_milked_per_day
        self.DHD = 2 * horizontal_dist_to_parlor * self.times_milked_per_day
    
      
