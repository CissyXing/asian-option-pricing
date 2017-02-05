from fixed_call import FixedCall
import math
import numpy

class AsianVecerFixedCall(FixedCall):
    def __init__(self, maxt, numx, numt, r, sigma, initial_price, strike):
        super().__init__(maxt, numx, numt, r, sigma, initial_price, strike)
        self.xi_initial = self.xi(self.s0, 0)
        # We choose maxx to be = q(0)
        self.maxx = self.q(0)
        self.dx = (self.q(0) + self.maxx) / numx
        self.set_boundary_conditions()
        self.set_strange_boundary()
        self.j0 = round((self.xi_initial + self.maxx) / self.dx)

    def a(self, t):
        return 0

    def b(self, t):
        return 1

    def set_initial_boundary(self):
        for row in range(self.numx):
            self.grid.itemset((row, 0), self.initial_value_at_height(row))

    def initial_value_at_height(self, row):
        return max(-self.maxx + row * self.dx, 0)

    def set_strange_boundary(self):
        for row in range(self.numx):
            for col in range(1, self.numt + 1):
                self.grid.itemset((row, col), self.strange_boundary_value())

    def strange_boundary_value(self):
        return self.q(0)

    def alpha(self, height, time):
        return .5 * self.sigma ** 2 * (
            (1 - math.exp(-self.r * (time + 0.5) * self.dt)) / (self.r * self.maxt)
            + self.maxx - height * self.dx
        ) ** 2 / (2 * self.dx ** 2) * self.dt

    def A_matrix(self, time):
        A = numpy.matrix([[0] * self.numx] * self.numx, dtype = numpy.float64)
        for i in range(self.numx):
            a = self.alpha(i, time)
            if i - 1 >= 0:
                A.itemset((i, i-1), a)
            A.itemset((i, i), 1 - 2 * a)
            if i + 1 < numx:
                A.itemset((i, i + 1), a)
        return A

    def B_matrix(self, time):
        B = numpy.matrix([[0] * self.numx] * self.numx, dtype = numpy.float64)
        for i in range(self.numx):
            a = self.alpha(i, time)
            if i - 1 >= 0:
                B.itemset((i, i-1), a)
            B.itemset((i, i), -2 * a)
            if i + 1 < numx:
                B.itemset((i, i + 1), a)
        return B

    def solve(self):
        super().solve(lambda time: numpy.identity(self.numx) - self.B_matrix(time), lambda time: self.A_matrix(time))
        return self.s0 * self.grid[self.j0, self.numt]

# Constants
numx = 200
numt = 400
maxt = 1
r = 0.09
s0 = 100

sigma = 0.05
print('Expected: 13.38, Actual: ' + str(AsianVecerFixedCall(maxt, numx, numt, r, sigma, s0, 90).solve()))
print('Expected: 8.81, Actual: ' + str(AsianVecerFixedCall(maxt, numx, numt, r, sigma, s0, 95).solve()))
print('Expected: 4.33, Actual: ' + str(AsianVecerFixedCall(maxt, numx, numt, r, sigma, s0, 100).solve()))
print('Expected: 0.88, Actual: ' + str(AsianVecerFixedCall(maxt, numx, numt, r, sigma, s0, 105).solve()))
print('Expected: 0.06, Actual: ' + str(AsianVecerFixedCall(maxt, numx, numt, r, sigma, s0, 110).solve()))