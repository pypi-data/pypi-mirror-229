print("""
Q8 ) class rectangle with function to find centre, area, and perimeter of a rectangle.

class Rectangle:
  def __init__(self, width, height , x_corner, y_corner):
    self.width = width
    self.height = height
    self.x_corner = x_corner
    self.y_corner = y_corner

  def area(self):
    return self.width * self.height

  def perimeter(self):
      return 2*(self.width + self.height)

  def center(self):
      center_x  =  self.x_corner + self.width/2
      center_y  =  self.y_corner + self.height/2
      return center_x, center_y

rect = Rectangle(10, 10 , 0 , 0)
center = rect.center()
area = rect.area()
peri = rect.perimeter()

print("Center :", center)
print("Area:", area)
print("Perimeter:", peri)""")