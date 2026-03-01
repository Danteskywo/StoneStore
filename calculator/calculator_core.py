class StoneCalculator:
    def __init__(self, stone, length, width, thickness, edge_type='straight'):
        self.stone = stone
        self.length = float(length)
        self.width = float(width)
        self.thickness = int(thickness)
        self.edge_type = edge_type
        
    def calculate_area(self):
        return self.length * self.width
    
    def calculate_perimeter(self):
        return 2 * (self.length + self.width)
    
    def calculate_stone_price(self):
        return self.calculate_area() * float(self.stone.price_per_sqm)
    
    def calculate_cutting_price(self):
        return self.calculate_perimeter() * float(self.stone.cutting_price_per_m)
    
    def calculate_edge_processing(self):
        edge_prices = self.stone.edge_processing_prices or {}
        return float(edge_prices.get(self.edge_type, 0)) * self.calculate_perimeter()
    
    def calculate_sink_cutout(self, has_sink=False):
        return float(self.stone.sink_cutout_price) if has_sink else 0
    
    def calculate_hob_cutout(self, has_hob=False):
        return float(self.stone.hob_cutout_price) if has_hob else 0
    
    def calculate_installation(self, need_install=False):
        if not need_install:
            return 0
        return float(self.stone.installation_price_per_m) * self.calculate_perimeter()
    
    def calculate_total(self, has_sink=False, has_hob=False, need_install=False):
        total = self.calculate_stone_price()
        total += self.calculate_cutting_price()
        total += self.calculate_edge_processing()
        total += self.calculate_sink_cutout(has_sink)
        total += self.calculate_hob_cutout(has_hob)
        total += self.calculate_installation(need_install)
        
        return {
            'stone_price': round(self.calculate_stone_price(), 2),
            'cutting_price': round(self.calculate_cutting_price(), 2),
            'edge_price': round(self.calculate_edge_processing(), 2),
            'sink_price': round(self.calculate_sink_cutout(has_sink), 2),
            'hob_price': round(self.calculate_hob_cutout(has_hob), 2),
            'installation_price': round(self.calculate_installation(need_install), 2),
            'total': round(total, 2),
            'area': round(self.calculate_area(), 2),
            'perimeter': round(self.calculate_perimeter(), 2)
        }
    
    def to_dict(self):
        return {
            'length': self.length,
            'width': self.width,
            'thickness': self.thickness,
            'area': self.calculate_area(),
            'perimeter': self.calculate_perimeter()
        }