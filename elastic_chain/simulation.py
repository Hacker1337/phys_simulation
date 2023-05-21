import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
from abc import abstractmethod, ABC
import matplotlib as mpl


g = -1   # free fall acceleration


class RingInterface(Circle, ABC):
    def __init__(self, y, r=0.2, color="black"):
        super().__init__((0.5, y), r, color=color, fill=False, linewidth=2, clip_on=True)
        self.y = y
        self.vy = 0
        self.r = r
    @abstractmethod
    def _move(self, dt):
        ...
        
    def move(self, dt):
        self._move(dt)
        if (self.y - self.r <= 0):
            self.y = self.r
            self.vy = 0
        self.center = self.center[0], self.y

    
class PassiveRing(RingInterface):
    def __init__(self, y, *args, **kwargs):
        super().__init__(y, *args, **kwargs)
    def _move(self, dt):
        self.y += self.vy*dt + g*dt**2/2
        self.vy += g*dt

class ActiveRing(RingInterface):
    
    def __init__(self, y, self_acceleration, *args, **kwargs):
        self.a = self_acceleration
        super().__init__(y, color="r", *args, **kwargs)
        
    def _move(self, dt):
        self.y += self.vy*dt + (g+self.a)*dt**2/2
        self.vy += (g+self.a)*dt

    
class Simulator:
    
    def __init__(self, N, F, axis, dt=0.01):
        """Simulates movements of chain elements

        Args:
            N (int): Number of chain elements
            F (float): force applied to first element (1 is grav force per element)
        """        
        r = 0.1
        self.rings = []
        for i in range(N-1):
            self.rings.append(PassiveRing(r, r=r))
        self.rings.append(ActiveRing(r, self_acceleration=F, r=r))
        for ring in self.rings:
            axis.add_patch(ring)
        self.pairs = [(i, i+1) for i in reversed(range(N-1))]
        self.dt = dt
        
    
    def check_end(self):
        yield False
        
    def get_artists(self):
        return self.rings
    def update(self, frame):
        for ring in self.rings:
            ring.move(self.dt)
        for i, j in self.pairs:
            ring1 = self.rings[i]
            ring2 = self.rings[j]
            if (abs(ring1.y - ring2.y) <= ring1.r + ring2.r):
                continue
            self.collide(ring1, ring2)
        return self.rings        
    
    def collide(self, ring1, ring2):
        v = (ring1.vy + ring2.vy)/2
        ring1.vy = v
        ring2.vy = v
        
        if (ring2.y < ring1.y):
            t = ring1
            ring1 = ring2
            ring2 = t
        y_av = (ring1.y+ring1.r + ring2.y-ring2.r)/2
        ring1.y = y_av - ring1.r
        ring2.y = y_av + ring2.r
        
def run_animation(T):
    
    plt.rcParams.update({
    "text.usetex" : True,
    "font.family" : "serif",
    "font.serif" : "Computer Modern",
    "text.latex.preamble" : r'\usepackage{amsmath} \usepackage{mathtext} \usepackage[english, russian]{babel}'
    })

    fig, ax = plt.subplots(figsize=(5, 5))
    F = 10
    ax.text(0.1, 0.9, f"$F={F}mg$")
    plt.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False, # labels along the bottom edge are off
        left=False,
        labelleft=False, # labels along the bottom edge are off

        )                   
    sim = Simulator(10, F, ax, dt=0.01)
    
    interval=40
    n = T*1000//interval
    ani = FuncAnimation(fig, sim.update,
                        # frames=sim.check_end,
                        frames=n,
                        interval=interval,
                        repeat=False,
                        init_func=sim.get_artists, blit=True)
    
    return ani
    

if __name__ == '__main__':
    T = 10
    ani = run_animation(T)
    f = r"media/animation.gif" 
    writer = mpl.animation.PillowWriter(fps=30) 
    ani.save(f, writer=writer, dpi=300)
    
    # plt.show(block=False)
    # plt.pause(T) 
    # plt.close("all")