from sympy import isprime


class point:

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x},{self.y})'
    
    def __repr__(self) -> str:
        return self.__str__()


class elliptic_curve:

    def __init__(self,p: int, a: int, b: int):
        assert isprime(p)
        self.p = p
        self.a = a % p
        self.b = b % p

    def __str__(self) -> str:
        return f'y^2=x^3+{self.a}x+{self.b}(mod {self.p})'
    
    def is_singular(self) -> bool:
        print("\n")
        print(f'4*{self.a}^3+27*{self.b}^2(mod {self.p}) = {4*self.a**3+27*self.b**2}(mod {self.p})={(4*self.a**3+27*self.b**2)%self.p}')
        if (4*self.a**3+27*self.b**2)%self.p == 0:
            print("Сингулярная")
            return True
        else:
            print("Не сингулярная")
            return False

    def does_contain_point(self, P: point) -> bool:
        print("\n")
        print(self)
        print(f'Левая часть: y^2={P.y**2}(mod {self.p})={P.y**2 % self.p}')
        print(f'Правая часть: x^3+ax+b(mod {self.p})={P.x**3}+{self.a}*{P.x}+{self.b}(mod {self.p})={P.x**3+self.a*P.x+self.b}(mod {self.p})={(P.x**3+self.a*P.x+self.b) % self.p}')
        if P.y**2 % self.p == (P.x**3+self.a*P.x+self.b) % self.p:
            print("Левая часть равна правой, значит точка принадлежит кривой")
            return True
        else:
            print("Левая часть не равна правой, значит точка не принадлежит кривой")
            return False
        
    def add_points(self, P: point, Q: point) -> point:
        R = point()
        angular_coefficient = ((Q.y - P.y) * pow(Q.x - P.x, -1, self.p)) % self.p
        print(f'lamda=({Q.y}-{P.y})/({Q.x}-{P.x})(mod {self.p})={Q.y - P.y}/{Q.x - P.x}(mod {self.p})={Q.y - P.y}*{pow(Q.x - P.x, -1, self.p)}(mod {self.p})={(Q.y - P.y) * pow(Q.x - P.x, -1, self.p)}(mod {self.p})={angular_coefficient}')
        R.x = (angular_coefficient**2 - P.x - Q.x) % self.p
        print(f'x_R={angular_coefficient}^2-{P.x}-{Q.x}(mod {self.p})={angular_coefficient**2 - P.x - Q.x}(mod {self.p})={R.x}')
        R.y = (angular_coefficient * (P.x - R.x) - P.y) % self.p
        print(f'y_R={angular_coefficient}*({P.x}-{R.x})-{P.y}(mod {self.p})={angular_coefficient * (P.x - R.x) - P.y}(mod {self.p})={R.y}')
        print(f'{R=}')
        return R
    
    def __double_point(self, P: point) -> point:
        R = point()
        angular_coefficient = ((3 * P.x**2 + self.a) * pow(2 * P.y, -1, self.p))%self.p
        print(f'lamda=(3*{P.x}**2+{self.a})/(2*{P.y})(mod {self.p})={3 * P.x**2 + self.a}/{2 * P.y}(mod {self.p})={3 * P.x**2 + self.a}*{pow(2 * P.y, -1, self.p)}(mod {self.p})={(3 * P.x**2 + self.a) * pow(2 * P.y, -1, self.p)}(mod {self.p})={angular_coefficient}')
        R.x = (angular_coefficient**2 - 2 * P.x)%self.p
        print(f'x_R={angular_coefficient}^2-2*{P.x}(mod {self.p})={angular_coefficient**2 - 2 * P.x}(mod {self.p})={R.x}')
        R.y = (angular_coefficient * (P.x - R.x) - P.y)%self.p
        print(f'y_R={angular_coefficient}*({P.x}-{R.x})-{P.y}(mod {self.p})={angular_coefficient * (P.x - R.x) - P.y}(mod {self.p})={R.y}')
        print(f'{R=}')
        return R
    
    @staticmethod
    def __recursive_string(n: int) -> str:
        assert n >= 0
        if n == 0:
            return 'P'
        elif n == 1:
            return '2P'
        else:
            return f'2({elliptic_curve.__recursive_string(n-1)})'
    
    def multiply_point(self, P: point, multiplier: int) -> point:
        print("\n")
        multiplier_as_powers_of_two = [index for index, bit in enumerate(list(bin(multiplier)[2:][::-1])) if bit == '1']
        print(multiplier,end='=')
        for two_power in multiplier_as_powers_of_two: print(2**two_power,end='+')
        print()
        print(f'{multiplier}P',end='=')
        for two_power in multiplier_as_powers_of_two: print(f'{2**two_power}P',end='+')
        print(end='=')
        for two_power in multiplier_as_powers_of_two: print(elliptic_curve.__recursive_string(two_power),end='+')
        print()
        P_multiplied_by_powers_of_two = [P]
        for i in range(multiplier_as_powers_of_two[-1]):
            print(f'\nВычислим {2**(i+1)}P')
            P_multiplied_by_powers_of_two.append(self.__double_point(P_multiplied_by_powers_of_two[-1]))
        R = P_multiplied_by_powers_of_two[multiplier_as_powers_of_two[0]]
        for two_power in multiplier_as_powers_of_two[1:]:
            print()
            R = self.add_points(R,P_multiplied_by_powers_of_two[two_power])
        print(f'{R=}')
        return R
    

def test():
    E = elliptic_curve(31,6,16)
    P = point(5,4)
    Q = point(2,6)
    print("P+Q =",E.add_points(P,Q))
    print("2P =",E.multiply_point(P,2))
    print("4P =",E.multiply_point(P,4))
    print("7P =",E.multiply_point(P,7))
    print("3Q =",E.multiply_point(Q,3))
    E = elliptic_curve(7,2,6)
    print('(1,3)',E.does_contain_point(point(1,3)))
    print('(2,4)',E.does_contain_point(point(2,4)))
    print('(2,5)',E.does_contain_point(point(2,5)))
    print('(3,6)',E.does_contain_point(point(3,6)))
    print('(4,6)',E.does_contain_point(point(4,6)))
    print('(5,1)',E.does_contain_point(point(5,1)))
    print('(5,5)',E.does_contain_point(point(5,5)))
    print('E_11(5,7)', elliptic_curve(11,5,7).is_singular())
    print('E_13(2,11)', elliptic_curve(13,2,11).is_singular())
    print('E_23(5,13)', elliptic_curve(23,5,13).is_singular())
    print('E_31(1,1)', elliptic_curve(31,1,1).is_singular())


if __name__ == '__main__':
    test()